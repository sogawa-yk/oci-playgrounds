# Ingress 接続不具合調査レポート

## 調査結果概要
`curl -k https://example.com` が `Connection refused` になる原因は、**OCI ロードバランサ (LB) にポート 443 (HTTPS) およびポート 80 (HTTP) のリスナーが作成されていないこと**です。

これは、OKE Native Ingress Controller が LB API に対して設定を適用する際、以下のエラーにより同期に失敗し続けているためです。

## 詳細なエラー内容

### 1. IAM 権限不足 (HTTPS/TLS)
Ingress Controller が証明書関連の処理を行う際、以下の権限エラーが発生しています。
```
Error returned by CertificatesManagement Service. Http Status Code: 404. Error Code: NotAuthorizedOrNotFound.
Message: Authorization failed or requested resource not found.
Operation Name: ListCaBundles
```
Controller は `ListCaBundles` API を呼び出そうとしていますが、権限がない (404/403) ため失敗しています。これにより TLS 設定の同期が中断されています。

### 2. BackendSet 作成失敗 (共通)
上記エラーまたは他の競合により、LB に必要な Backend Set が作成されていません。その結果、リスナー作成 (Routing Policy 作成) 時に以下のエラーが発生しています。
```
Error returned by LoadBalancer Service. Http Status Code: 400. Error Code: InvalidParameter.
Message: Routing Policy 'route_80' contains a rule referencing BackendSet 'bs_99b...' which does not exist
```
Backend Set が存在しないため、リスナーも作成されず、結果として LB はどのポートでも待ち受けを行っていない状態です (`Connection refused`)。

## 推奨される対策

### 1. IAM ポリシーの確認と追加
Native Ingress Controller のワークロード ID (またはインスタンスプリンシパル) に対して、以下のサービスへのアクセス権限を付与してください。
- `certificates-management-family` (CA Bundle 参照用と思われる)
- `load-balancer-family` (LB 操作用、既にありそうだが念のため)

### 2. 競合リソースの削除 (実施済み)
調査過程で、ポート 80 を占有していた `mcp-server-ingress` が競合を起こしていたため、削除しました。

### 3. Controller の再起動
IAM ポリシー付与後、状態をリセットするために Controller Pod を再起動することをお勧めします。
```bash
kubectl delete pod -n native-ingress-controller-system -l app=oci-native-ingress-controller
```
