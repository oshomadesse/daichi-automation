# daichi-automation

インタビュー書き起こしテキストから、動画企画案3つ + 見積書PDF を自動生成し、Drive格納・スプシ転記・メール通知まで一括処理するツール。

## アーキテクチャ

```
┌──────────────────────────────────────────────────────────────┐
│  daichi が Claude Code に依頼                                │
│  「この書き起こしから企画案と見積書を作って」                     │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    Claude Code (本体)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. 書き起こしテキストを読み込む                           │  │
│  │    (Notta等で事前に文字起こし済みのファイル)               │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 2. 企画案3つを生成 (Claude Code自身が考える)             │  │
│  │    → runs/<案件名>/proposals.json に書き出し             │  │
│  └──────────────────────┬─────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 3. python main.py proposals.json を実行                 │  │
│  │    → 以下6ステップを自動処理                             │  │
│  └──────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼────────────────────────────────────┘
                          │
          ┌───────────────┼──────────────────────┐
          ▼               ▼                      ▼
    [Step 1-3]       [Step 4-5]            [Step 6]
    見積り処理        Google APIs            通知
          │               │                    │
          ▼               ▼                    ▼
   ┌────────────┐  ┌────────────┐   ┌──────────────┐
   │ ① 単価読込  │  │ ④ Drive     │   │ ⑥ メール通知  │
   │ Sheets API │  │  見積PDF   │   │  SMTP/Gmail  │
   │ (単価タブ)  │  │  アップロード│   └──────────────┘
   └─────┬──────┘  │ + Google   │
         │         │  ドキュメント│
         ▼         │  (企画案)   │
   ┌────────────┐  └─────┬──────┘
   │ ② 見積計算  │        │
   │ 単価×数量   │        ▼
   └─────┬──────┘  ┌────────────┐
         │         │ ⑤ スプシ転記 │
         ▼         │ Sheets API │
   ┌────────────┐  │ (管理タブ)  │
   │ ③ PDF生成   │  └────────────┘
   │ fpdf2      │
   └────────────┘
```

### データフロー

```
Notta等で文字起こし済みテキスト
  │
  ├──[Claude Code]───────► proposals.json
  │                         ├─ 企画案1: {title, concept, scenes[], cost_factors}
  │                         ├─ 企画案2: ...
  │                         └─ 企画案3: ...
  │
  └──[python main.py]
       │
       ├──[Sheets API]──────► rate_table  ← スプシ「単価」タブから読込
       │
       ├──[見積計算]─────────► estimates  ← rate_table × cost_factors
       │
       ├──[fpdf2]───────────► estimate.pdf (日本語対応)
       │
       ├──[Google Docs API]─► proposal_doc_url (企画案ドキュメント)
       │
       ├──[Drive API]───────► pdf_url (見積PDFリンク)
       │
       ├──[Sheets API]──────► 「管理」タブに1行追加
       │
       └──[SMTP]────────────► メール通知
```

## ワークフロー

daichi がNotta等で文字起こししたテキストファイルをローカルに配置し、Claude Code に依頼する。

**依頼例:**
> この書き起こしテキストを読んで、動画企画案3つと見積書を作って。
> テキスト: /path/to/transcript.txt
> 案件名: 田中様インタビュー

**Claude Code の実行手順:**
1. 指定されたテキストファイルを Read ツールで読み込む
2. テキスト内容を分析し、企画案を3つ生成する
   - 1つ目: 王道・安定した構成
   - 2つ目: 斬新・チャレンジ的な構成
   - 3つ目: コスパ重視・ミニマルな構成
3. `runs/<案件名>/proposals.json` に書き出す（Write ツール使用）
4. 以下のコマンドを実行:
   ```
   python main.py runs/<案件名>/proposals.json --name <案件名>
   ```
5. 実行結果（企画案URL, 見積書URL）をユーザーに報告する

## proposals.json のフォーマット

Claude Code が生成する企画案JSON。**必ずこの形式で出力すること。**

```json
{
  "proposals": [
    {
      "title": "企画タイトル",
      "concept": "2〜3文でのコンセプト説明",
      "target_audience": "ターゲット視聴者",
      "duration_seconds": 180,
      "scenes": [
        {
          "scene_number": 1,
          "description": "シーンの内容説明",
          "duration_seconds": 30,
          "visual_notes": "映像イメージ・演出メモ"
        }
      ],
      "key_messages": ["伝えたいメッセージ1", "伝えたいメッセージ2"],
      "tone": "プロフェッショナル",
      "cost_factors": {
        "shooting_days": 2,
        "locations": 1,
        "talent_count": 1,
        "post_production_days": 3,
        "needs_narration": true,
        "needs_bgm": true
      }
    }
  ]
}
```

### cost_factors の説明

| フィールド | 型 | 説明 |
|---|---|---|
| shooting_days | int | 撮影日数 |
| locations | int | ロケ地の数 |
| talent_count | int | 出演者数 |
| post_production_days | int | 編集・後処理日数 |
| needs_narration | bool | ナレーション有無 |
| needs_bgm | bool | BGM/SE有無 |

これらの値はスプシ「単価」タブの単価と掛け合わせて見積り金額が算出される。
現実的な数値を設定すること。

## スプレッドシート構成

### 「単価」タブ（手動管理）

| 項目 | 単価 | 単位 |
|---|---|---|
| 撮影費 | 100000 | 円/日 |
| 編集費 | 80000 | 円/日 |
| ディレクション費 | 50000 | 円/日 |
| 出演者費 | 30000 | 円/人日 |
| ロケハン費 | 20000 | 円/箇所 |
| ナレーション | 50000 | 円/本 |
| BGM/SE | 30000 | 円/本 |

単価を変更したい場合はこのタブの値を直接編集する。コードの変更は不要。

### 「管理」タブ（自動書き込み）

パイプライン実行時に自動で1行追加される:

| 日付 | ファイル名 | 企画案URL | 見積URL | ステータス |

## CLIコマンド

```bash
# 企画案JSONから見積〜メールまで一括実行
python main.py proposals.json --name 案件名

# ドライラン（Drive/メール送信しない、ローカル確認用）
python main.py proposals.json --name 案件名 --dry-run

# 途中で失敗した場合の再開
python main.py proposals.json --name 案件名 --resume
```

## セットアップ

### 1. Python依存パッケージ
```bash
pip install -r requirements.txt
```

### 2. 環境変数
`.env.example` をコピーして `.env` を作成し、各値を設定:
```bash
cp .env.example .env
```

### 3. Google Cloud
1. Google Cloud Console でプロジェクト作成
2. 以下のAPIを有効化:
   - Google Drive API
   - Google Sheets API
   - Google Docs API
3. サービスアカウント作成 → JSONキーをダウンロード
4. `credentials/service-account.json` に配置
5. Drive フォルダとスプレッドシートをサービスアカウントのメールアドレスに共有

### 4. Gmail
1. Googleアカウントで2段階認証を有効化
2. アプリパスワードを生成
3. `.env` の `GMAIL_ADDRESS` と `GMAIL_APP_PASSWORD` に設定

### 5. 日本語フォント
`fonts/NotoSansJP-Regular.ttf` を配置（PDF日本語表示用）。
Google Fonts からダウンロード可能。

### 6. 文字起こし
Notta等の文字起こしサービスでインタビュー音声をテキスト化し、ローカルにファイルとして保存する。
Claude Code はこのテキストファイルを読み込んで企画案を生成する。

### 7. GitHubリポジトリを Public にする
daichi が Claude Code の Proプランでこのリポジトリを使うため、リポジトリを Public に設定する。
GitHub → Settings → Danger Zone → Change visibility → Public

## TODO

- [ ] Google Cloud プロジェクト作成 + API有効化 (Drive / Sheets / Docs)
- [ ] サービスアカウント作成 → JSON キーを `credentials/` に配置
- [ ] Drive に納品用フォルダ作成 → サービスアカウントに共有
- [ ] スプレッドシート作成（「単価」タブ + 「管理」タブ）→ サービスアカウントに共有
- [ ] 「単価」タブに単価テーブルを入力
- [ ] `.env` を作成して各値を設定
- [ ] Gmail アプリパスワード生成 → `.env` に設定
- [ ] `fonts/NotoSansJP-Regular.ttf` を配置
- [ ] `pip install -r requirements.txt` 実行
- [ ] GitHub リポジトリを Public に変更
- [ ] daichi に Notta 等の文字起こしサービスを契約してもらう
- [ ] daichi の PC に Claude Code + Pro プランをセットアップ
- [ ] テスト用の書き起こしテキストで全フロー通し実行
- [ ] daichi に操作手順をレクチャー
