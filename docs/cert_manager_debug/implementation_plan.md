# Nginx HTTPS マニフェスト修正計画

## 問題の概要
`oke/cert-manager/nginx-https.yaml` を適用しても、ポートフォワードやサービス経由での HTTPS 接続 (ポート 443) が拒否される (`connection refused`)。
調査の結果、ConfigMap `nginx-conf` が `/etc/nginx/conf.data` にマウントされているが、Nginx は `/etc/nginx/conf.d/` 以下の設定ファイルを参照するため、カスタム設定が読み込まれていないことが判明した。

## ユーザー確認事項
なし

## 変更内容
### oke/cert-manager
#### [MODIFY] [nginx-https.yaml](file:///Users/sogawa/Documents/GitHub/oci-playgrounds/oke/cert-manager/nginx-https.yaml)
- Deployment `my-nginx` の `volumeMounts` において、`nginx-conf` の `mountPath` を `/etc/nginx/conf.data` から `/etc/nginx/conf.d` に変更する。

## 検証計画
### 自動テスト / 手動検証
1. マニフェストの再適用:
   ```fish
   kubectl apply -f oke/cert-manager/nginx-https.yaml
   ```
2. Pod の再起動 (設定反映のため):
   ```fish
   kubectl rollout restart deploy/my-nginx
   ```
3. ポートフォワードによる接続確認:
   ```fish
   kubectl port-forward svc/my-nginx 8443:443
   ```
   別ターミナルで `curl -k https://localhost:8443` を実行し、"Hello! This is HTTPS response..." が返ることを確認する。
