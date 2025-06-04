# YouTube Channel Auto-List

YouTubeの新興チャンネルを自動的に発見・フィルタリングし、Googleスプレッドシートに出力するPythonツールです。

## 概要

このツールは、特定のキーワードに基づいてYouTubeチャンネルを検索し、成長ポテンシャルの高い新興チャンネルを自動的に発見します。個人ブランディングが低く、ビジネス提携の可能性が高いチャンネルを識別する機能も備えています。

## 主な機能

- **自動チャンネル検索**: キーワードに基づいてYouTubeチャンネルを自動検索
- **スマートフィルタリング**: 
  - 登録者数 ≤ 20,000人
  - 動画数 ≤ 30本
  - チャンネル開設から2ヶ月以内
  - 拡散率3-8の動画を3本以上保有
- **個人ブランディング判定**: 個人チャンネル/Vlogチャンネルを自動識別し、ビジネス向けチャンネルを優先
- **拡散率計算**: 各動画の「再生回数/登録者数」を計算し、バイラル性を評価
- **Googleスプレッドシート連携**: フィルタリング結果を自動的にスプレッドシートに出力
- **バッチ処理**: 複数のキーワードを連続処理

## 前提条件

- Python 3.6以上
- YouTube Data API v3のAPIキー
- Google Cloud ServiceアカウントのJSON認証情報
- 必要なPythonライブラリ（requirements.txtに記載）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/Jun2664/yt-channel-autolist.git
cd yt-channel-autolist
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. YouTube Data APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成または既存のプロジェクトを選択
3. YouTube Data API v3を有効化
4. 認証情報を作成し、APIキーを取得

### 4. Google Sheets APIの設定

1. 同じGoogle Cloudプロジェクトで Google Sheets API を有効化
2. サービスアカウントを作成:
   - 「認証情報」→「認証情報を作成」→「サービスアカウント」
   - サービスアカウント名とIDを入力
   - 「作成して続行」をクリック
3. サービスアカウントに「編集者」ロールを付与
4. JSONキーを作成:
   - 作成したサービスアカウントをクリック
   - 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
   - JSON形式を選択してダウンロード

### 5. 環境変数の設定

以下の環境変数を設定してください：

```bash
# YouTube API キー
export YOUTUBE_API_KEY="your-youtube-api-key-here"

# Google Service Account JSON（JSONファイルの内容全体）
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'
```

または、`.env`ファイルを作成して管理することも可能です。

### 6. キーワードの設定

`keywords.txt`ファイルを編集して、検索したいキーワードを1行に1つずつ記載します。デフォルトでは以下のようなキーワードが含まれています：

- チュートリアル関連: "tutorial", "how to", "diy", "guide"
- 教育系: "programming", "science", "history", "mathematics"
- スキル系: "video editing", "3d modeling", "game development"
- ビジネス系: "business", "finance", "marketing", "investing"

## 使い方

### 基本的な実行

```bash
python main.py
```

実行すると、以下の処理が自動的に行われます：

1. `keywords.txt`から検索キーワードを読み込み
2. 各キーワードでYouTubeチャンネルを検索（最大50件/キーワード）
3. フィルタリング条件に基づいてチャンネルを選別
4. 結果をGoogleスプレッドシートに出力
5. スプレッドシートのURLを表示

### 出力形式

Googleスプレッドシートには以下の情報が出力されます：

| カラム | 説明 |
|--------|------|
| チャンネル名 | YouTubeチャンネルの名前 |
| チャンネルURL | チャンネルへの直接リンク |
| 登録者数 | 現在の登録者数 |
| 動画数 | 投稿された動画の総数 |
| チャンネル作成日 | チャンネルが開設された日付 |
| トップ動画1-3 | 拡散率の高い上位3動画 |
| 拡散率1-3 | 各動画の拡散率（再生回数/登録者数） |
| 検索キーワード | このチャンネルを発見したキーワード |
| 個人ブランディング | 「低」または「高」（DM可能性の指標） |
| 更新日時 | データが取得された日時 |

## 自動実行の設定

### Linuxの場合（cron）

```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行する例
0 9 * * * cd /path/to/yt-channel-autolist && python main.py
```

### GitHub Actionsを使用する場合

`.github/workflows/auto-run.yml`を作成：

```yaml
name: Auto Run YouTube Channel Scraper

on:
  schedule:
    # 毎日UTC 0:00（JST 9:00）に実行
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  run-scraper:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run scraper
      env:
        YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
      run: |
        python main.py
```

## 高度な設定

### フィルタリング条件のカスタマイズ

`youtube_scraper.py`の`filter_channels`メソッドで条件を調整できます：

```python
# 登録者数の上限を変更
if channel_info['subscriber_count'] > 50000:  # 20000から変更
    continue

# チャンネル年齢の条件を変更
channel_age_days = (datetime.now() - created_date).days
if channel_age_days > 90:  # 60日から90日に変更
    continue

# 拡散率の条件を変更
if 2 <= rate <= 10:  # 3-8から2-10に変更
    high_diffusion_videos.append(video)
```

### 個人ブランディング判定のカスタマイズ

`youtube_scraper.py`の`is_low_personal_branding`メソッドで判定キーワードを追加・削除できます：

```python
personal_keywords = [
    'face', 'selfie', 'vlog', 'my', '私', 'personal', 
    'daily', 'routine', 'lifestyle', 'diary', 
    # 新しいキーワードを追加
    'morning routine', 'night routine', 'grwm'
]
```

## トラブルシューティング

### よくあるエラーと解決方法

1. **APIキーエラー**
   ```
   Error: Invalid API key
   ```
   - 環境変数`YOUTUBE_API_KEY`が正しく設定されているか確認
   - APIキーがYouTube Data API v3で有効になっているか確認

2. **Google認証エラー**
   ```
   Error: Could not authenticate with Google Sheets
   ```
   - `GOOGLE_SERVICE_ACCOUNT_JSON`が正しいJSON形式か確認
   - サービスアカウントにGoogle Sheets APIへのアクセス権限があるか確認

3. **キーワードファイルエラー**
   ```
   Error: keywords.txt not found
   ```
   - `keywords.txt`がプロジェクトルートに存在するか確認

4. **API制限エラー**
   ```
   Error: Quota exceeded
   ```
   - YouTube Data APIの日次クォータを確認（デフォルト: 10,000ユニット/日）
   - 検索キーワード数を減らすか、実行頻度を調整

## 注意事項

- YouTube Data APIには使用制限があります（デフォルト: 10,000ユニット/日）
- 大量のキーワードを処理する場合は、API使用量に注意してください
- 個人情報保護の観点から、収集したデータの取り扱いには十分注意してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストは歓迎します。大きな変更を行う場合は、まずissueを作成して変更内容を説明してください。

## 作者

[@Jun2664](https://github.com/Jun2664)