# daichi-automation セットアップガイド

インタビューの書き起こしテキストから、動画企画案3つ + 見積書PDFを自動生成するツール。
Claude Code に依頼するだけで、企画案作成 → 見積PDF → Drive保存 → スプシ記録 → メール通知まで全自動で完了する。

## 必要なもの

- Mac
- Googleアカウント
- Claude Pro（月額$20）

---

## Step 0: Claude Code をインストール

### 0-1. ターミナルを開く

Macの「アプリケーション」→「ユーティリティ」→「ターミナル」を開く。
または Spotlight（Cmd + Space）で「ターミナル」と検索。

### 0-2. Node.js をインストール

ターミナルに以下を1行ずつコピペして実行:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Homebrew インストール後:

```bash
brew install node
```

### 0-3. Claude Code をインストール

```bash
npm install -g @anthropic-ai/claude-code
```

### 0-4. Claude Pro に登録

1. https://claude.ai にアクセス
2. アカウント作成（まだの場合）
3. Pro プラン（$20/月）に登録

### 0-5. Claude Code にログイン

```bash
claude
```

初回起動時にブラウザが開くのでログインする。ログインできたら `Ctrl+C` で一旦閉じてOK。

---

## Step 1: このフォルダを配置

このフォルダ（`setup/`）をダウンロードして、好きな場所に置く。

例: デスクトップに置く場合

```bash
mv ~/Downloads/setup ~/Desktop/daichi-automation
```

以降、このフォルダを `daichi-automation` と呼ぶ。

---

## Step 2: 自動セットアップを実行

ターミナルで以下を実行:

```bash
cd ~/Desktop/daichi-automation
bash setup.sh
```

これで以下が自動的に行われる:
- Python パッケージのインストール
- 日本語フォントのダウンロード
- `.env` ファイルの作成

---

## Step 3: Google Cloud の設定

ここが一番手順が多いが、1回やれば終わり。

### 3-1. Google Cloud Console にログイン

https://console.cloud.google.com にアクセスしてGoogleアカウントでログイン。

### 3-2. プロジェクトを作成

1. 画面上部の「プロジェクトの選択」をクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名: `daichi-automation`（なんでもOK）
4. 「作成」をクリック

### 3-3. API を3つ有効化

画面上部の検索バーに以下を1つずつ入力して、それぞれ「有効にする」をクリック:

1. `Google Drive API` → 有効にする
2. `Google Sheets API` → 有効にする
3. `Google Docs API` → 有効にする

### 3-4. OAuth 同意画面を設定

1. 左メニュー →「Google Auth Platform」→「概要」
2. 「開始」をクリック（初回の場合）
3. アプリ名: `daichi-automation`
4. ユーザーサポートメール: 自分のGmailアドレス
5. 対象: 「外部」を選択
6. 「保存」

### 3-5. テストユーザーを追加

1. 左メニュー →「対象」
2. 「テストユーザーを追加」をクリック
3. 自分のGmailアドレスを入力して保存

### 3-6. OAuth クライアントIDを作成

1. 左メニュー →「クライアント」
2. 「+ クライアントを作成」をクリック
3. アプリケーションの種類: 「デスクトップアプリ」
4. 名前: `daichi-automation-desktop`（なんでもOK）
5. 「作成」をクリック

### 3-7. JSON キーをダウンロード

1. 作成したクライアントの行の右端にあるダウンロードボタン（↓）をクリック
2. 「JSONをダウンロード」を選択
3. ダウンロードしたファイルを `credentials/` に配置:

```bash
mv ~/Downloads/client_secret_*.json ~/Desktop/daichi-automation/credentials/client_secret.json
```

### 3-8. Google Drive にフォルダを作成

1. https://drive.google.com を開く
2. 「+ 新規」→「新しいフォルダ」
3. フォルダ名: `daichi-納品`（なんでもOK）

**フォルダIDをメモ:**
フォルダを開いた状態のURLから取得:
`https://drive.google.com/drive/folders/【ここがフォルダID】`

### 3-9. スプレッドシートを作成

1. 3-8 で作ったDriveフォルダの中で「+ 新規」→「Google スプレッドシート」
2. スプレッドシート名: `daichi-管理シート`（なんでもOK）

### 3-10. タブを設定

1. シート下部の「シート1」タブを右クリック →「名前を変更」→ `単価` に変更
2. シート下部の「+」をクリックして新しいタブ追加 → `管理` に名前変更

### 3-11. 単価タブにデータを入力

「単価」タブのA1セルから以下を入力:

| A列（費目） | B列（単価） | C列（単位） |
|---|---|---|
| 撮影費 | 100000 | 円/日 |
| 編集費 | 80000 | 円/日 |
| ディレクション費 | 50000 | 円/日 |
| 出演者費 | 30000 | 円/人日 |
| ロケハン費 | 20000 | 円/箇所 |
| ナレーション | 50000 | 円/本 |
| BGM/SE | 30000 | 円/本 |

**注意:**
- 単価（B列の数字）は自由に変更OK
- **費目名（A列）の変更や行の追加・削除はしないこと**（コードが費目名で計算しているため）
- 費目を変更・追加したい場合は、Claude Code に「単価タブの費目を変更したい」と相談すれば、コードも一緒に修正してくれる

### 3-12. スプレッドシートIDをメモ

URLから取得:
`https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit`

---

## Step 4: Gmail アプリパスワードを取得

### 4-1. 2段階認証を有効化

1. https://myaccount.google.com/security にアクセス
2. 「2段階認証プロセス」→ 有効化（既に有効なら次へ）

### 4-2. アプリパスワードを生成

1. https://myaccount.google.com/apppasswords にアクセス
2. アプリ名: `daichi-automation`
3. 「作成」をクリック
4. 表示された16文字のパスワードをメモ（例: `xxxx xxxx xxxx xxxx`）

---

## Step 5: .env に値を入力

テキストエディタで `.env` ファイルを開く:

```bash
open -e ~/Desktop/daichi-automation/.env
```

以下の項目を、Step 3-4 でメモした値に書き換える:

```
GOOGLE_DRIVE_FOLDER_ID=ここにDriveフォルダIDを貼り付け
↓
GOOGLE_DRIVE_FOLDER_ID=1ABCxyz123456789     ← Step 3-8 でメモしたID

GOOGLE_SPREADSHEET_ID=ここにスプレッドシートIDを貼り付け
↓
GOOGLE_SPREADSHEET_ID=1DEFabc987654321     ← Step 3-12 でメモしたID

GMAIL_ADDRESS=ここに自分のGmailアドレス
↓
GMAIL_ADDRESS=daichi@gmail.com             ← 自分のGmailアドレス

GMAIL_APP_PASSWORD=ここにアプリパスワード
↓
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx     ← Step 4-2 でメモしたパスワード

NOTIFY_TO=ここに通知先メールアドレス
↓
NOTIFY_TO=daichi@gmail.com                 ← 自分宛ならGMAIL_ADDRESSと同じでOK
```

保存して閉じる。

---

## Step 6: テスト実行

全てが正しく設定されているか確認する:

```bash
cd ~/Desktop/daichi-automation
python main.py sample/sample_proposals.json --name テスト --dry-run
```

**初回実行時にブラウザが開く。** Googleアカウントでログインして許可する。
「このアプリはGoogleで確認されていません」と出たら「詳細」→「daichi-automation（安全でないページ）に移動」で進む。

`--dry-run` はDriveアップロードとメール送信をスキップするモード。
PDFが `runs/` フォルダに生成されていれば成功。

本番（全機能動作）テスト:

```bash
python main.py sample/sample_proposals.json --name テスト
```

実行後、以下を確認:
- Driveフォルダに企画案ドキュメントと見積PDFがアップロードされている
- スプレッドシート「管理」タブに1行追加されている
- メールが届いている

---

## Step 7: 本番の使い方

### 7-1. 書き起こしテキストを用意

インタビュー音声をNotta等で文字起こしし、テキストファイルとして保存。
例: `~/Desktop/tanaka-interview.txt`

### 7-2. Claude Code を起動

```bash
cd ~/Desktop/daichi-automation
claude
```

### 7-3. Claude Code に依頼

以下のように入力:

```
この書き起こしテキストを読んで、動画企画案3つと見積書を作って。
テキスト: ~/Desktop/tanaka-interview.txt
案件名: 田中様インタビュー
```

あとは自動で全部やってくれる。

---

## トラブルシューティング

### 「Python が見つからない」と出る

```bash
brew install python
```

### 「認証エラー」が出る

- `credentials/client_secret.json` が正しく配置されているか確認
- GCPのOAuth同意画面でテストユーザーに自分のGmailが追加されているか確認
- `credentials/token.json` を削除して再認証を試す:

```bash
rm credentials/token.json
```

### 「このアプリはGoogleで確認されていません」と出る

正常な動作。「詳細」→「daichi-automation（安全でないページ）に移動」で進む。

### 「メール送信に失敗」する

- `.env` の `GMAIL_ADDRESS` と `GMAIL_APP_PASSWORD` が正しいか確認
- Gmailの2段階認証が有効になっているか確認
- アプリパスワード（通常のパスワードではない）を使っているか確認

### 途中で止まった場合

`--resume` オプションで途中から再開できる:

```bash
python main.py runs/案件名/proposals.json --name 案件名 --resume
```
