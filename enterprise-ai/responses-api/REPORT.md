# OCI Enterprise AI - メモリ機能調査レポート

## 調査日

2026-04-07

## 調査対象プロジェクト

- **Project OCID**: `ocid1.generativeaiproject.oc1.ap-osaka-1.amaaaaaassl65iqahgxjrfsrylxyfdyejtii6ef7u3juahqz46syytx6vqea`
- **リージョン**: ap-osaka-1 (大阪)
- **モデル**: openai.gpt-oss-120b

---

## 1. メモリ機能の概要

OCI Enterprise AI の Responses API には、以下のメモリ機能が提供されている。

### 1.1 短期メモリ（Short-Term Memory）

同一会話内のコンテキストを保持する機能。3つの方式がある。

| 方式 | 説明 | 状態管理 |
|---|---|---|
| `previous_response_id` | 前回のレスポンスIDを渡して会話を連鎖 | サーバー側 |
| Conversations API | 会話オブジェクトを作成し、`conversation=id` で紐づけ | サーバー側 |
| Client-Managed State | クライアントが会話履歴を `[{role, content}, ...]` 配列で保持し `input` に渡す | クライアント側 |

#### 短期メモリ最適化（Short-Term Memory Compaction）

- プロジェクトレベルで有効化する設定
- 長い会話の履歴を自動的に要約・圧縮し、トークン使用量とレイテンシを削減する
- **一度有効化すると無効化できない**（プロジェクト削除が必要）
- 圧縮に使用するモデルもプロジェクト作成時に選択（後から変更不可）

**現在のプロジェクトの状態**: Conversations API でのレスポンスに `short_term_memory_optimization: true` が含まれており、**有効化されている**。

```python
# 確認方法: Conversations API のレスポンスメタデータに含まれる
conv = client.conversations.create(metadata={})
print(conv.metadata)
# => {'short_term_memory_optimization': 'true'}
```

#### 大阪リージョンで利用可能な圧縮モデル

| モデル |
|---|
| Google Gemini 2.5 Pro |
| Google Gemini 2.5 Flash |
| Meta Llama 3.3 (70B) |
| OpenAI gpt-oss-120b |

### 1.2 長期メモリ（Long-Term Memory）

会話を跨いで情報を保持する機能。

- 会話から重要な情報を抽出し、ベクトルとして保存
- `subject_id` を使って同一プロジェクト内でユーザーごとに記憶を分離
- ユースケース: ユーザーの好み、背景情報の保持
- **一度有効化すると無効化できない**

#### 大阪リージョンで利用可能なモデル

| 用途 | モデル |
|---|---|
| 抽出モデル（Extraction） | OpenAI gpt-oss-120b |
| 埋め込みモデル（Embedding） | Cohere Embed 4 |

**現在のプロジェクトの状態**: API レスポンスに長期メモリ関連の情報が含まれておらず、OCI CLI からもプロジェクト設定を取得できなかった（Enterprise AI 向けの CLI コマンドが未提供）。**OCI Console から直接確認が必要**。

---

## 2. file_search との組み合わせにおける制限事項

### 2.1 当初発見した問題（2026-04-07）

`file_search` ツールを使用した場合、サーバー側での会話管理（`previous_response_id` / Conversations API）が **2ターン目以降で `json_parse_error` になる**問題を確認。

```python
# 1ターン目: 正常に動作
r1 = client.responses.create(
    model="openai.gpt-oss-120b",
    input="OCI API Gatewayとは？",
    tools=[{"type": "file_search", "vector_store_ids": ["vs_..."]}],
    store=True,
)

# 2ターン目: json_parse_error
r2 = client.responses.create(
    model="openai.gpt-oss-120b",
    input="その主な機能を3つ挙げて",
    previous_response_id=r1.id,  # ← ここでエラー
)
```

エラー内容:

```
Status Code from provider: 400
Invalid JSON data: Failed to deserialize the JSON body into the target type:
input: data did not match any variant of untagged enum ResponseInput
```

当初の回避策として Client-Managed State を採用していた。

### 2.2 再検証結果（2026-04-08）

`verify_file_search_bug.py` による体系的なテストの結果、**当初のバグは修正済み**であることを確認。ただし新たなエッジケースを発見。

#### テストマトリクス（全テスト3回実行、全回一致）

| # | ステート方式 | ツール | 結果 |
|---|---|---|---|
| T01 | なし（ベースライン） | なし | **PASS** |
| T02 | なし（ベースライン） | file_search | **PASS** |
| T03 | previous_response_id | なし | **PASS** |
| T04 | previous_response_id | file_search（両ターン） | **PASS** ✅ 修正済み |
| T05 | previous_response_id | file_search（T1のみ、T2ツールなし） | **FAIL** 🐛 新規 |
| T06 | previous_response_id | file_search（T2のみ） | **PASS** |
| T07 | Conversations API | なし | **PASS** |
| T08 | Conversations API | file_search（両ターン） | **PASS** ✅ 修正済み |
| T09 | Client-Managed State | なし | **PASS** |
| T10 | Client-Managed State | file_search | **PASS** |
| T11 | previous_response_id | file_search、3ターン | **PASS** |
| T12 | Client-Managed（tool call除外） | file_search | **PASS** |
| T13 | previous_response_id + include=[] | file_search | **PASS** |
| T14 | previous_response_id | file_search、別モデル | SKIP |
| T15 | Conversations API | file_search（T1のみ） | **PASS** |
| T16 | previous_response_id | file_search、store=False | **FAIL** （想定通り） |

#### 新たに発見した問題: T05

**条件**: ターン1で `file_search` + `store=True` → ターン2で `previous_response_id` を指定するが `tools` パラメータを渡さない

**エラー**: 当初と同じ `json_parse_error`（`data did not match any variant of untagged enum ResponseInput`）

**原因推定**: サーバーが保存済みの `file_search_call` 出力をデシリアライズする際、ターン2のリクエストに `tools` 定義が含まれていないと型解決できない。ターン2でも `tools` を渡せば（T04）正常動作する。

**影響**: 実用上は軽微。通常、file_search を使うアプリケーションでは毎ターン `tools` を渡すため。ただしサーバー側のデシリアライゼーションロジックに残存する問題として報告可能。

**Conversations API（T15）では発生しない** ことから、`previous_response_id` 固有の問題。

#### T16 について

`store=False` で作成したレスポンスを `previous_response_id` で参照すると "not found" エラー。これは想定通りの動作（保存されていないレスポンスは参照できない）。

#### instructions パラメータとの組み合わせ問題

追加検証により、**`instructions` パラメータと `previous_response_id` + `file_search` の組み合わせでも `json_parse_error` が発生する**ことを確認。

| 条件 | 結果 |
|---|---|
| `instructions` なし + `previous_response_id` + `file_search` | **PASS** |
| `instructions` あり + `previous_response_id` + `file_search` | **FAIL** |
| `instructions` あり + Conversations API + `file_search` | **PASS** |
| developer ロールメッセージ + `previous_response_id` + `file_search` | **FAIL** |

`Conversations API` では `instructions` との組み合わせでも問題なく動作するため、`previous_response_id` 固有のデシリアライゼーション問題。

### 2.3 現在の対応

`previous_response_id` + `instructions` + `file_search` の組み合わせでバグが残存するため、アプリケーションを **Conversations API 方式に移行**。これにより:

- サーバー側の会話管理を活用可能
- `instructions` パラメータも問題なく使用可能
- 短期メモリ最適化（自動圧縮）の恩恵を受けられる
- クライアント側での履歴管理が不要になり、実装がシンプルに

---

## 3. データ保持（Data Retention）

| 設定 | 内容 |
|---|---|
| レスポンス保持期間 | 生成後、自動削除されるまでの時間 |
| 会話保持期間 | 最終更新後、自動削除されるまでの時間 |
| 最大保持期間 | 720時間（30日） |

※ 長期メモリ使用時は、両方を最大（720時間）に設定することが推奨されている。

---

## 4. 今後の確認事項

- [ ] OCI Console でプロジェクトの長期メモリ設定を確認する
- [ ] 短期メモリ最適化が Client-Managed State でも有効に機能するか検証する
- [ ] `file_search` + `previous_response_id` / Conversations API の問題が OCI 側で修正されるか追跡する
- [ ] `subject_id` パラメータの正しい使い方をドキュメントで確認する（現時点ではコード例がドキュメントに存在しない）

---

## 5. 参考ドキュメント

- [QuickStart Guide for Building Agents](https://docs.oracle.com/en-us/iaas/Content/generative-ai/get-started-agents.htm)
- [OCI vs OpenAI Responses API](https://docs.oracle.com/en-us/iaas/Content/generative-ai/oci-openai.htm)
- [Projects](https://docs.oracle.com/en-us/iaas/Content/generative-ai/projects.htm)
- [Creating a Project](https://docs.oracle.com/en-us/iaas/Content/generative-ai/create-project.htm)
- [Building Agents](https://docs.oracle.com/en-us/iaas/Content/generative-ai/building-agents.htm)
- [Models and Regions for Agentic API](https://docs.oracle.com/en-us/iaas/Content/generative-ai/agentic-regions.htm)
