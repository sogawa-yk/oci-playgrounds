# Ingress 接続問題および Pod 起動エラーの修正計画

## 問題の調査結果
1.  **HTTPS 接続タイムアウトの原因**:
    - OCI ロードバランサが配置されているサブネット (`...jreq`) に紐づくセキュリティリスト (`...eie7l2q`) に、**ポート 443 (HTTPS) の受信ルールが存在しません**。(ポート 80 のみ許可されています)
2.  **Pod 起動エラー (ImagePullBackOff)**:
    - 指定されたコンテナイメージ `hashicorp/http-echo` のプルに失敗しています (`short name mode is enforcing`)。明示的なレジストリプレフィックス (`docker.io/`) が必要であるか、イメージが古い可能性があります。

## 変更内容

### 1. マニフェスト修正 (Pod error fix)
#### [MODIFY] [ingress-demo.yaml](file:///Users/sogawa/Documents/GitHub/oci-playgrounds/oke/cert-manager/ingress-demo.yaml)
- Deployment `echo-deployment` の image を `hashicorp/http-echo` から `gcr.io/google-containers/echoserver:1.10` に変更します。
  - 理由: `hashicorp/http-echo` は古く、`args` の形式も特殊なため、より汎用的な `echoserver` (ポート8080) を使用して確実に動作させます。
  - 合わせて `containerPort` と Service の `targetPort` を `5678` から `8080` に変更します。

### 2. OCI セキュリティリスト修正 (Connectivity fix)
以下のコマンドを実行し、ポート 443 (TCP) への受信許可ルールを追加します。

```fish
oci network security-list update --security-list-id ocid1.securitylist.oc1.ca-toronto-1.aaaaaaaamckpazn7qyk7j4m5tffabdwso7ujc2rw7l7f4pmrm4mh6eie7l2q --region ca-toronto-1 --ingress-security-rules '[{"protocol":"6","source":"0.0.0.0/0","tcpOptions":{"destinationPortRange":{"max":80,"min":80}},"isStateless":false},{"protocol":"6","source":"0.0.0.0/0","tcpOptions":{"destinationPortRange":{"max":443,"min":443}},"isStateless":false}]' --force
```
※ 既存のルール (Port 80) を上書きしないよう、Port 80 と 443 の両方を含むリストで更新します。

## 検証計画
1. マニフェストを適用する。
2. セキュリティリスト更新コマンドを実行する。
3. Pod が `Running` になることを確認する。
4. `curl -k https://example.com --resolve example.com:443:40.233.90.123` が成功することを確認する。
