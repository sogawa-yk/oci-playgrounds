OKEのアドオンでNative Ingress Controllerを有効化した後、追加で作業が必要。

1. IngressClassParametersを作成する
1. IngressClassを作成する

# 追加で何をするのか
Native Ingress Controllerを使うと、OCI LBをSSL終端としてパスルーティングなども行える。これにより、Kubernetes上のリソースを使わずに、外部からのアクセスを制御できる。

そのためには、当然Ingress管理下のOCI LBを事前に作成する必要がある（nginxのIngressの場合はこのLBがPodにあたる）。

その作業を行うのがこの手順。
IngressClassParameterに作成するLBの情報（OCIDなど）を設定する。
IngressClassにIngressClassParameterを紐付ける。

以上。