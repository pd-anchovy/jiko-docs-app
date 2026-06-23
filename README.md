# 事故書類整理アプリ

事故書類(紙・スキャン画像)をブラウザにドラッグ&ドロップ → AI(Gemini)が項目を読み取り → 確認・修正 → Google スプレッドシートへ車両番号＋発生日で突合追記する、社内2〜3人向けの無料Streamlitアプリ。

## 抽出項目
- **① 受付書類:** 車両番号 / 発生日 / 補償の種類 / 運転者名
- **② 支払書類:** 車両番号 / 発生日 / 支払完了(はい/いいえ)

## 1. 準備するもの
1. **Gemini APIキー** … [Google AI Studio](https://aistudio.google.com/) で発行(無料枠)
2. **Google サービスアカウント** … Google Cloud でサービスアカウントを作成し、JSONキーを発行。Google Sheets API / Drive API を有効化しておく
3. **スプレッドシート** … Google スプレッドシートを作成し、**1行目に列ヘッダ**を入力:
   ```
   車両番号 | 発生日 | 補償の種類 | 運転者名 | 受付登録日時 | 支払完了 | 支払登録日時
   ```
4. 上記スプレッドシートを、**サービスアカウントのメールアドレス**(`xxx@xxx.iam.gserviceaccount.com`)に**編集者**として共有

## 2. ローカル実行
```bash
python -m venv .venv
.venv/Scripts/activate            # Windows(Git Bash)。PowerShellは .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
`.streamlit/secrets.toml` を `.streamlit/secrets.toml.example` を元に作成し、実際の値を記入(このファイルはコミットしない):
```toml
app_password = "共有パスワード"
gemini_api_key = "AI Studio のAPIキー"
sheet_id = "スプレッドシートのID(URLの /d/ と /edit の間)"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```
起動:
```bash
streamlit run app.py
```

### 動作確認(スモーク)
1. パスワードでログインできる
2. 種類(①受付/②支払)を切り替えられる
3. 画像をドラッグ&ドロップ →「読み取り」で結果が表で出る
4. 表のセルを編集できる
5. 「スプレッドシートに送信」で対象シートに行が追加/更新され、成功メッセージが出る

## 3. デプロイ(Streamlit Community Cloud / 無料)
1. **GitHubのプライベートリポジトリ**にpush(`.gitignore` で secrets と venv は除外済み)
2. [share.streamlit.io](https://share.streamlit.io/) で **New app** → リポジトリと `app.py` を指定
3. アプリの **Settings → Secrets** に、上記 `secrets.toml` の中身をそのまま貼り付け(`[gcp_service_account]` セクション含む)
4. デプロイ後、URLと共有パスワードを社内2〜3人に共有

## 使い方の流れ
1. ログイン(共有パスワード)
2. 書類の種類を選ぶ(①受付 / ②支払)
3. 画像をドラッグ&ドロップ(複数可)
4. 「読み取り」→ 編集可能な表で結果を確認・修正
5. 「スプレッドシートに送信」→ 車両番号＋発生日で①②を突合して追記
   - 「受付済みだが支払未完了」= **支払完了が空の行**として一目で分かる

## 注意・補足
- **プライバシー:** Gemini は AI Studio **無料枠**を使用。無料枠では入力データ(事故書類＝個人情報を含む)が**Geminiの改善・学習に利用される可能性がある**。完全無料を最優先して採用。重視する場合は **Vertex AI(会社のGoogle Cloud)** に切り替えると学習に使われず、コストもほぼ無料。
- **モデル名:** 既定は `gemini-2.0-flash`。無料枠で使えない/変更したい場合は `extract.py` の `model_name` を AI Studio で利用可能なビジョン対応モデルに変更。
- **テスト:** `pytest -q` で純粋ロジック(項目定義・突合・JSON解析・シート書き込み)を検証。

## ファイル構成
- `app.py` … Streamlit UI(ログイン・種別選択・D&D・確認表・送信)
- `schema.py` … 列・項目定義
- `matcher.py` … 突合と行マージの純関数
- `extract.py` … Gemini呼び出し(画像→項目)
- `sheets.py` … Google Sheets 読み書き
- `tests/` … pytest
