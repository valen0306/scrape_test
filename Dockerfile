# ベースイメージとしてPythonの公式イメージを使用
FROM python:3.11-slim-buster

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール（Chrome用）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコンテナにコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコンテナにコピー
COPY ./app /app

# アプリケーションを起動するコマンドを定義
# Uvicornを使って、8000番ポートでFastAPIアプリケーションを実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
