# Research Assistant Demo

Chainlit + Responses API + OCI Vector Store を使ったデモアプリです。

このリポジトリでは、説明しやすいように実装を次の 3 層に分けています。

1. UI表示層
2. アプリケーション層
3. Responses API呼び出し層

## Architecture

```text
+------------------------------+
| UI Layer                     |
| ui/chainlit_app.py           |
| ui/chainlit_app_memory.py    |
+------------------------------+
              |
              v
+------------------------------+
| Service Layer                |
| services/search_service.py   |
| - search_stateless()         |
| - search_with_memory()       |
+------------------------------+
              |
              v
+------------------------------+
| Gateway Layer                |
| gateways/responses_gateway.py|
| - build_request()            |
| - query_responses_api()      |
+------------------------------+
              |
              v
+------------------------------+
| External Services            |
| - Responses API              |
| - OCI Vector Store           |
+------------------------------+
```

## Directory Layout

```text
.
├── chainlit_app.py
├── chainlit_app_memory.py
├── domain/
│   └── models.py
├── gateways/
│   └── responses_gateway.py
├── references/
│   └── responses_api/
│       ├── common.py
│       ├── search_memory.py
│       ├── search_stateless.py
│       └── upload_docs_to_vector_store.py
├── services/
│   └── search_service.py
├── ui/
│   ├── chainlit_app.py
│   ├── chainlit_app_memory.py
│   └── chainlit_common.py
└── README.md
```

## Layer Responsibilities

### 1. UI表示層

対象ファイル:

- `ui/chainlit_app.py`
- `ui/chainlit_app_memory.py`
- `ui/chainlit_common.py`

責務:

- Chainlit のイベントを受け取る
- 画面表示用のメッセージを組み立てる
- service 層を呼び出す

この層では、Responses API のリクエスト形式や認証処理は扱いません。

### 2. アプリケーション層

対象ファイル:

- `services/search_service.py`

責務:

- stateless と memory の振る舞いを分ける
- UI から見たユースケースを表現する
- gateway 層のエラーをアプリ用の意味に寄せる

このデモでは、UI は `search_stateless()` または `search_with_memory()` を呼ぶだけです。

### 3. Responses API呼び出し層

対象ファイル:

- `gateways/responses_gateway.py`

責務:

- OCI 認証を初期化する
- OpenAI クライアントを作る
- Responses API のリクエストを組み立てる
- `file_search` の結果を `SearchResult` に変換する

外部 API に依存するコードはこの層に閉じ込めています。

### Domain

対象ファイル:

- `domain/models.py`

責務:

- 層をまたいで受け渡すデータ構造を定義する

このデモでは `SearchResult` を使っています。

## Stateless / Memory Difference

### Stateless

- 毎回独立した質問として Responses API を呼び出します
- 前の会話は使いません

呼び出し元:

- `ui/chainlit_app.py`

### Memory

- `previous_response_id` を使って Responses API の会話継続を試みます
- Chainlit の `user_session` には最新の `response_id` だけを保持します

呼び出し元:

- `ui/chainlit_app_memory.py`

## PDF Upload From UI

- Chainlit UI で PDF を添付して送信すると、その PDF はベクトルストアへアップロードされます
- 添付だけで送信した場合は、アップロードだけを実行します
- 添付と質問文を同時に送信した場合は、先にアップロードし、その後で検索を実行します
- アップロード処理は `services/search_service.py` の `upload_pdfs_to_vector_store()` から呼ばれます
- 実際のベクトルストア登録は `gateways/responses_gateway.py` の `upload_pdf_to_vector_store()` で実行されます

UI 側の該当箇所:

- `ui/upload_handlers.py`
- `ui/chainlit_app.py`
- `ui/chainlit_app_memory.py`

## Entry Points

ルートの次のファイルは、既存の起動方法を変えないための薄いエントリポイントです。

- `chainlit_app.py`
- `chainlit_app_memory.py`

実装本体は `ui/` 配下にあります。

## Responses API References

UI を使わずに Responses API を直接試したい場合は、`references/responses_api/` 配下のスクリプトを使います。

### PDF をベクトルストアへアップロード

```bash
python references/responses_api/upload_docs_to_vector_store.py
```

### Stateless 検索

```bash
python references/responses_api/search_stateless.py
```

### Memory 検索

```bash
python references/responses_api/search_memory.py
```

## Chainlit Startup

### Stateless

```bash
chainlit run chainlit_app.py --host 0.0.0.0 --port 8000
```

### Memory

```bash
chainlit run chainlit_app_memory.py --host 0.0.0.0 --port 8000
```

## UI Operation

### PDF をアップロードするだけ

1. クリップアイコンから PDF を添付する
2. メッセージ本文を空のまま送信する
3. `Uploaded to vector store:` が表示されたら完了

### PDF をアップロードしてすぐ質問する

1. クリップアイコンから PDF を添付する
2. そのまま質問文を入力して送信する
3. アップロード完了後に検索結果が表示される

### 既存の PDF 群に対して質問する

1. 添付せずに質問文だけ送信する
2. ベクトルストア内の PDF を対象に検索して回答する

## Notes

- memory 版は Responses API の `previous_response_id` を使っています
- ただし OCI 経由の実行では、2 ターン目以降に `json_parse_error` が返ることがあります
- そのため、このデモでは memory 版の失敗理由が UI 上で説明できるようにしています

## Recommended Reading Order

コードを説明する場合は、次の順で追うと分かりやすいです。

1. `ui/chainlit_app.py` または `ui/chainlit_app_memory.py`
2. `services/search_service.py`
3. `gateways/responses_gateway.py`
4. `domain/models.py`
