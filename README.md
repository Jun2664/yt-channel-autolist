# YouTube Channel Auto-List

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/Jun2664/yt-channel-autolist/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 プロジェクト概要

YouTube Channel Auto-List は、急成長中の YouTube チャンネルを自動的に発見・分析・フィルタリングし、ビジネスパートナーシップに適したチャンネルを特定するための Python ツールです。複数の地域・言語に対応し、Google Sheets、JSON、CSV など複数の形式でデータをエクスポートできます。

### 🎯 解決する課題

- **手動検索の限界**: 数百万のチャンネルから有望なチャンネルを手動で見つけるのは困難
- **地域別の最適化**: 各地域で異なる成長基準やトレンドに対応
- **ビジネス適合性**: 個人ブランディングが強すぎないビジネス向けチャンネルの特定
- **データ分析**: チャンネルの成長率、エンゲージメント率、キーワードトレンドの自動分析

### 🚀 主要機能

- **マルチリージョン対応**: JP, US, EN, ES, PT, BR の6つの市場に対応
- **スマートフィルタリング**: 地域別の閾値設定（登録者数、動画数、チャンネル年齢）
- **拡散率分析**: 動画の視聴回数/登録者数比率を計算し、バイラル性を評価
- **キーワード抽出・分析**: 成功動画からトレンドキーワードを自動抽出（NLTK使用）
- **個人ブランディング検出**: AI による個人/Vlog チャンネルの自動識別
- **複数の発見方法**: トレンド動画、カテゴリ別、最新チャンネル、関連チャンネルなど
- **バッチ処理**: 複数キーワードの連続処理に対応
- **柔軟な出力形式**: Google Sheets、JSON、CSV への自動エクスポート

### 📊 ユースケース

1. **マーケティング担当者**: インフルエンサーマーケティングのパートナー候補発見
2. **ブランドマネージャー**: 商品プロモーションに適したチャンネルの特定
3. **コンテンツクリエイター**: 競合分析とトレンド把握
4. **投資家・アナリスト**: 成長中のクリエイターエコノミーの分析
5. **エージェンシー**: クライアント向けのチャンネルリサーチ自動化

## 🛠️ セットアップ方法

### 前提条件

- Python 3.11 以上
- pip または Poetry（パッケージ管理）
- Google Cloud アカウント（API キー取得用）
- Git（リポジトリクローン用）

### 1. リポジトリのクローン

```bash
git clone https://github.com/Jun2664/yt-channel-autolist.git
cd yt-channel-autolist
```

### 2. 依存関係のインストール

#### pip を使用する場合
```bash
pip install -r requirements.txt
```

#### Poetry を使用する場合（推奨）
```bash
poetry install
```

### 3. YouTube Data API の設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成または既存プロジェクトを選択
3. 「APIとサービス」→「ライブラリ」で YouTube Data API v3 を検索・有効化
4. 「認証情報」→「認証情報を作成」→「API キー」を作成
5. API キーを安全な場所に保存

### 4. Google Sheets & Drive API の設定

1. Google Cloud Console で以下の API を有効化:
   - **Google Sheets API**
   - **Google Drive API** （必須）

2. サービスアカウントの作成:
   ```
   「認証情報」→「認証情報を作成」→「サービスアカウント」
   → サービスアカウント名を入力（例: yt-channel-autolist）
   → 「作成して続行」
   → ロール「編集者」を選択
   → 「完了」
   ```

3. JSON キーの生成:
   ```
   作成したサービスアカウントをクリック
   → 「キー」タブ
   → 「鍵を追加」→「新しい鍵を作成」
   → JSON 形式を選択
   → ダウンロード
   ```

### 5. 環境変数の設定

#### 方法1: 環境変数を直接設定
```bash
# YouTube API キー
export YOUTUBE_API_KEY="your-youtube-api-key-here"

# Google Service Account JSON（ファイル内容全体をコピー）
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'
```

#### 方法2: .env ファイルを使用（推奨）
```bash
# .env ファイルを作成
cat > .env << EOF
# API Keys
YOUTUBE_API_KEY=your-youtube-api-key-here
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

# 地域別設定（オプション）
JP_MAX_SUBS=20000
EN_MAX_SUBS=50000
ES_MAX_SUBS=40000

# 追加 API（オプション）
VIDIQ_API_KEY=your-vidiq-key
TUBEBUDDY_API_KEY=your-tubebuddy-key
EOF
```

### 6. キーワードファイルの準備

`keywords.txt` に検索キーワードを1行1つずつ記載:
```
tutorial
how to
programming
cooking
fitness
gaming
```

## 💻 使い方

### 基本的な使用方法

#### 日本市場のチャンネル検索（デフォルト）
```bash
python main.py
```

#### 英語圏のチャンネル検索
```bash
python main.py --region US --lang en
```

#### スペイン語圏のチャンネル検索
```bash
python main.py --region ES --lang es
```

### 出力形式の指定

```bash
# JSON 形式で出力
python main.py --region EN --output-format json

# CSV 形式で出力  
python main.py --region PT --output-format csv

# Google Sheets に出力（デフォルト）
python main.py --region BR --output-format sheets
```

### カスタムキーワードファイルの使用

```bash
python main.py --region US --keywords-file custom_keywords.txt
```

### コマンドラインオプション一覧

| オプション | 説明 | デフォルト値 | 選択肢 |
|-----------|------|-------------|--------|
| `--region` | 対象地域 | JP | JP, US, EN, ES, PT, BR |
| `--lang` | 言語設定 | 地域に応じて自動設定 | ja, en, es, pt |
| `--output-format` | 出力形式 | sheets | sheets, json, csv |
| `--keywords-file` | キーワードファイル | keywords.txt | 任意のファイルパス |
| `--sheet-url` | Google Sheets URL | 新規作成 | 既存シートのURL |
| `--max-results` | 最大取得チャンネル数 | 50 | 1-100 |

### GitHub Actions による自動実行

`.github/workflows/auto-discover.yml` を作成:

```yaml
name: Auto Discover YouTube Channels

on:
  schedule:
    # 毎週月曜日の UTC 00:00（JST 09:00）に実行
    - cron: '0 0 * * 1'
  workflow_dispatch:
    inputs:
      region:
        description: 'Target region'
        required: true
        default: 'JP'
        type: choice
        options:
          - JP
          - US
          - EN
          - ES
          - PT
          - BR

jobs:
  discover-channels:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        region: [JP, US, EN, ES, PT, BR]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run channel discovery for ${{ matrix.region }}
      env:
        YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
        GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
      run: |
        python main.py --region ${{ matrix.region }}
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: channel-results-${{ matrix.region }}
        path: |
          rising_channels_*.json
          rising_channels_*.csv
          hot_keywords_*.csv
```

## 🧪 開発・テストガイド

### ブランチ戦略

- `main`: 本番環境用の安定版
- `develop`: 開発用のメインブランチ
- `feature/*`: 新機能開発用
- `fix/*`: バグ修正用
- `docs/*`: ドキュメント更新用

### ローカル開発環境のセットアップ

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# pre-commit フックの設定
pre-commit install
```

### テストの実行

```bash
# 単体テストの実行
pytest tests/

# カバレッジ付きテスト
pytest --cov=. --cov-report=html

# 特定のテストのみ実行
pytest tests/test_youtube_scraper.py::test_filter_channels
```

### コードフォーマット・リンティング

```bash
# Black でコードフォーマット
black .

# flake8 でリンティング
flake8 .

# isort でインポート整理
isort .

# mypy で型チェック
mypy .
```

### 新機能の追加手順

1. `develop` ブランチから feature ブランチを作成
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

2. 機能を実装し、テストを追加

3. コミット前にフォーマット・リンティング
   ```bash
   make format  # または個別にツールを実行
   ```

4. プルリクエストを作成

## 🗂️ プロジェクト構成

```
yt-channel-autolist/
├── main.py                 # メインエントリーポイント
├── youtube_scraper.py      # YouTube API 連携・スクレイピング
├── sheets_writer.py        # Google Sheets エクスポート
├── config.py              # 設定管理・環境変数読み込み
├── keyword_extractor.py   # キーワード抽出・分析（NLTK）
├── channel_sources.py     # チャンネル発見メソッド集
├── keyword_research_api.py # 外部キーワード API 連携
├── keywords.txt           # デフォルトキーワードリスト
├── requirements.txt       # Python パッケージ依存関係
├── test_*.py             # 各種テストファイル
├── .github/
│   └── workflows/        # GitHub Actions ワークフロー
├── docs/                 # ドキュメント
└── README.md            # このファイル
```

## 🔧 設定のカスタマイズ

### 地域別デフォルト設定

| 設定項目 | JP | US/EN | ES | PT/BR |
|---------|-----|-------|-----|-------|
| 最小検索ボリューム | 500K | 1M | 750K | 750K |
| 最大登録者数 | 20K | 50K | 40K | 40K |
| 最大動画数 | 30 | 30 | 30 | 30 |
| 拡散率範囲 | 3-8× | 2-6× | 2.5-7× | 2.5-7× |
| チャンネル年齢 | 60日 | 60日 | 60日 | 60日 |

### 環境変数による詳細設定

```bash
# 地域別の詳細設定例（.env ファイル）
# 英語圏の設定
EN_MIN_VOLUME=1000000          # 最小検索ボリューム
EN_MAX_SUBS=50000              # 最大登録者数
EN_MAX_VIDEOS=30               # 最大動画数
EN_SPREAD_RATE_MIN=2           # 最小拡散率
EN_SPREAD_RATE_MAX=6           # 最大拡散率
EN_CHANNEL_AGE_DAYS=60         # チャンネル年齢（日数）

# API レート制限
YOUTUBE_API_MAX_RETRIES=3      # API リトライ回数
YOUTUBE_API_RETRY_DELAY=5      # リトライ間隔（秒）

# 出力設定
DEFAULT_OUTPUT_DIR=./output    # デフォルト出力ディレクトリ
ENABLE_DEBUG_LOG=false         # デバッグログ有効化
```

## 🐛 トラブルシューティング

### よくあるエラーと解決方法

#### 1. API キーエラー
```
Error: Invalid API key / API key not valid
```
**解決方法**:
- 環境変数 `YOUTUBE_API_KEY` が正しく設定されているか確認
- API キーが YouTube Data API v3 で有効になっているか確認
- API キーに IP 制限がある場合は解除

#### 2. Google 認証エラー
```
Error: Could not authenticate with Google Sheets
```
**解決方法**:
- `GOOGLE_SERVICE_ACCOUNT_JSON` が完全な JSON 形式か確認
- JSON の改行やエスケープが正しいか確認
- サービスアカウントに適切な権限があるか確認

#### 3. Google Drive API エラー
```
Error: Google Drive API has not been used in project before
```
**解決方法**:
1. [Google Cloud Console](https://console.cloud.google.com/) で Drive API を有効化
2. 有効化後、5分程度待ってから再実行

#### 4. API クォータ超過
```
Error: Quota exceeded for quota metric
```
**解決方法**:
- YouTube Data API の日次クォータを確認（デフォルト: 10,000ユニット/日）
- 検索キーワード数を減らす
- 実行頻度を調整（1日1回など）

#### 5. プレイリスト取得エラー
```
Error: playlistNotFound (404)
```
**解決方法**:
- チャンネルが動画を非公開にしている可能性
- このエラーは自動的にスキップされるため、通常は対処不要

### デバッグモード

詳細なログを表示するには:
```bash
# デバッグモードで実行
ENABLE_DEBUG_LOG=true python main.py --region JP
```

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🤝 貢献

プルリクエストを歓迎します！貢献する際は以下のガイドラインに従ってください：

1. Issue を作成して変更内容を説明
2. Fork してから feature ブランチを作成
3. コードスタイルガイドに従う（Black, flake8）
4. テストを追加・更新
5. プルリクエストを作成

### コントリビューター行動規範

- 建設的なフィードバックを心がける
- 多様性を尊重し、包括的な環境を維持
- プロジェクトの目的に沿った貢献を行う

## 👥 作者・連絡先

- **作者**: [@Jun2664](https://github.com/Jun2664)
- **プロジェクト**: [yt-channel-autolist](https://github.com/Jun2664/yt-channel-autolist)
- **Issues**: [GitHub Issues](https://github.com/Jun2664/yt-channel-autolist/issues)

## 🔄 更新履歴

最新の更新情報は [Releases](https://github.com/Jun2664/yt-channel-autolist/releases) ページをご覧ください。

---

*最終更新: 2025年6月5日*