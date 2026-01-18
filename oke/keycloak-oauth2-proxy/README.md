## ゴール
1. Keycloakを立ち上げ、OIDCの設定を行う
2. `oauth2-proxy`をSidecarとして配置し、アプリへのアクセスを保護
3. アプリ側で`X-Forwarded-User`をチェックして、認証を確認する

## 設定手順
### Step1: Keycloakのデプロイ
[このhelmチャート](https://github.com/codecentric/helm-charts/tree/master/charts/keycloakx)を使う。
```bash
# リポジトリの追加
helm repo add codecentric https://codecentric.github.io/helm-charts
helm repo update

# Keycloakのインストール（開発用のため簡易設定）
helm install keycloak codecentric/keycloakx -f values.yaml
```
ポートフォワードで接続できるかを確認する。
```bash
kubectl port-forward svc/keycloak 8080:80
```
ブラウザで`http://localhost:8080`にアクセスして、Keycloakのダッシュボードにログインする。
