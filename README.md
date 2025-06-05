# YouTube Channel Auto-List

A Python tool that automatically discovers and filters emerging YouTube channels across multiple regions and exports them to Google Sheets, JSON, or CSV.

## Overview

This tool searches for YouTube channels based on specific keywords and automatically discovers emerging channels with high growth potential. It features region-specific configurations, keyword analysis, and personal branding detection to identify channels suitable for business partnerships.

## Key Features

- **Multi-Region Support**: Search channels in JP, US, EN, ES, PT, BR markets
- **Automatic Channel Discovery**: Search YouTube channels based on keywords
- **Smart Filtering with Region-Specific Thresholds**: 
  - Subscriber count limits (JP: ≤20k, EN: ≤50k, etc.)
  - Video count ≤ 30
  - Channel age within 60 days
  - Multiple videos with optimal spread rates
- **Keyword Analysis**: Extract and analyze trending keywords from successful videos
- **Personal Branding Detection**: Automatically identify personal/vlog channels to prioritize business-suitable channels
- **Spread Rate Calculation**: Calculate view/subscriber ratio to evaluate viral potential
- **Multiple Output Formats**: Export to Google Sheets, JSON, or CSV
- **Batch Processing**: Process multiple keywords continuously
- **GitHub Actions Integration**: Automated weekly runs with region-specific processing

## Prerequisites

- Python 3.6+
- YouTube Data API v3 API key
- Google Cloud Service Account JSON credentials (for Sheets export)
- Required Python libraries (see requirements.txt)

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

## Usage

### Basic Usage (Japanese Market)

```bash
python main.py
```

### Search English Market Channels

```bash
python main.py --region US --lang en
```

### Export to Different Formats

```bash
# Export to JSON
python main.py --region EN --output-format json

# Export to CSV
python main.py --region ES --output-format csv

# Use custom keywords file
python main.py --region PT --keywords-file keywords_pt.txt
```

### Region Options

- `JP` - Japan (default)
- `US` - United States
- `EN` - English-speaking markets
- `ES` - Spanish-speaking markets
- `PT` - Portuguese-speaking markets
- `BR` - Brazil

The tool will:

1. Load keywords from the specified file
2. Search YouTube channels in the target region
3. Apply region-specific filtering thresholds
4. Extract and analyze keywords from successful videos
5. Output results in the specified format

### Output Formats

#### Google Sheets Output

| Column | Description |
|--------|-------------|
| Channel Name | YouTube channel name |
| Channel URL | Direct link to channel |
| Subscribers | Current subscriber count |
| Video Count | Total videos published |
| Created Date | Channel creation date |
| Top Video 1-3 | Top 3 high-spread videos |
| Spread Rate 1-3 | Spread rate for each video |
| Search Keyword | Keyword that found this channel |
| Personal Branding | Low/High (business suitability) |
| Top Keywords | Extracted trending keywords |
| Region | Target market region |
| Update Time | Data collection timestamp |

#### JSON Output
- File: `rising_channels_{region}_{YYYYMMDD}.json`
- Contains full channel data with metadata

#### CSV Output
- Channels: `rising_channels_{region}_{YYYYMMDD}.csv`
- Keywords: `hot_keywords_{region}_{YYYYMMDD}.csv` (score ≥ 6)

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

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# API Keys
YOUTUBE_API_KEY=your-youtube-api-key
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

# Region-specific thresholds (example for English market)
EN_MIN_VOLUME=1000000
EN_MAX_SUBS=50000
EN_MAX_VIDEOS=30
EN_SPREAD_RATE_MIN=2
EN_SPREAD_RATE_MAX=6
EN_CHANNEL_AGE_DAYS=60

# Optional keyword research APIs
VIDIQ_API_KEY=your-vidiq-key
TUBEBUDDY_API_KEY=your-tubebuddy-key
```

### Region-Specific Defaults

| Metric | JP | EN/US | ES | PT/BR |
|--------|----|----|----|----|
| Min Search Volume | 500k | 1M | 750k | 750k |
| Max Subscribers | 20k | 50k | 40k | 40k |
| Max Videos | 30 | 30 | 30 | 30 |
| Spread Rate Range | 3-8× | 2-6× | 2.5-7× | 2.5-7× |
| Channel Age | 60 days | 60 days | 60 days | 60 days |

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