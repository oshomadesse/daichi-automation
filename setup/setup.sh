#!/bin/bash
# daichi-automation セットアップスクリプト

set -e

echo "=== daichi-automation セットアップ ==="
echo ""

# プロジェクトルートに移動
cd "$(dirname "$0")"

# 1. Python依存パッケージインストール
echo "[1/3] Python パッケージをインストール中..."
pip install -r requirements.txt
echo "  完了"
echo ""

# 2. フォントダウンロード
echo "[2/3] 日本語フォントをダウンロード中..."
if [ ! -f fonts/NotoSansJP-Regular.ttf ]; then
    curl -L -o fonts/NotoSansJP-Regular.ttf \
      "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
    echo "  ダウンロード完了"
else
    echo "  既にダウンロード済み、スキップ"
fi
echo ""

# 3. .env作成
echo "[3/3] .env ファイルを準備中..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  .env を作成しました"
else
    echo "  .env は既に存在します、スキップ"
fi
echo ""

# 完了
echo "=== セットアップ完了 ==="
echo ""
echo "次のステップ:"
echo "  1. credentials/service-account.json を配置"
echo "  2. .env を開いて各値を入力"
echo "  詳しくは README.md を参照"
