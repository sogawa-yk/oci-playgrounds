# Jupyter Notebook用のDev Container設定
FROM mcr.microsoft.com/devcontainers/python:3.11

# 必要なパッケージをインストール
RUN pip3 install --upgrade pip

# requirements.txtがある場合は先にコピーしてインストール
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Jupyter関連パッケージをインストール
RUN pip3 install jupyterlab ipykernel

# ワークスペースを作業ディレクトリに設定
WORKDIR /workspace

# デフォルトコマンド
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
