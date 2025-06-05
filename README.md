# YouTube Channel Auto-List 🚀

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Google APIs](https://img.shields.io/badge/API-YouTube%20%7C%20Sheets-red.svg)](https://developers.google.com/apis-explorer)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 新興YouTubeチャンネルを自動検出・分析し、ビジネスパートナーシップに適したチャンネルを発見するPythonツール

## 📋 目次

- [概要](#-概要)
- [主要機能](#-主要機能)
- [動作環境](#-動作環境)
- [セットアップ](#-セットアップ)
- [使い方](#-使い方)
- [開発・テスト](#-開発テスト)
- [プロジェクト構成](#-プロジェクト構成)
- [トラブルシューティング](#-トラブルシューティング)
- [コントリビューション](#-コントリビューション)
- [ライセンス](#-ライセンス)

## 🎯 概要

YouTube Channel Auto-Listは、キーワードベースでYouTubeチャンネルを検索し、成長ポテンシャルの高い新興チャンネルを自動的に発見するツールです。地域別の閾値設定、キーワード分析、個人ブランディング検出などの高度な機能により、ビジネスパートナーシップに適したチャンネルを効率的に特定します。

### ユースケース

- **マーケティング担当者**: インフルエンサーマーケティングの候補チャンネル発見
- **コンテンツクリエイター**: コラボレーション相手の探索
- **ビジネス開発**: 成長中のニッチチャンネルとのパートナーシップ機会の特定
- **市場調査**: 特定分野の新興トレンドとクリエイターの把握

## ✨ 主要機能

### 🌍 マルチリージョン対応
- **対応地域**: JP（日本）、US（米国）、EN（英語圏）、ES（スペイン語圏）、PT（ポルトガル語圏）、BR（ブラジル）
- 地域別に最適化された検索パラメータと閾値設定

### 🔍 スマートフィルタリング
- **地域別購読者数上限**: JP ≤20k、EN ≤50k など
- **動画数**: ≤30本（新興チャンネルに特化）
- **チャンネル年齢**: 60日以内
- **拡散率計算**: 視聴回数/購読者数比で viral potential を評価

### 📊 高度な分析機能
- **キーワード抽出**: 成功動画から頻出キーワードを自動抽出
- **個人ブランディング検出**: vlog/個人チャンネルを識別し、ビジネス向けチャンネルを優先
- **トレンドスコアリング**: キーワードの出現頻度と関連性を数値化

### 📤 柔軟な出力形式
- **Google Sheets**: リアルタイム共有と共同編集に対応
- **JSON**: プログラマティックな処理やAPI連携用
- **CSV**: Excel等での詳細分析用

### 🤖 自動化対応
- **GitHub Actions統合**: 定期的な自動実行設定
- **バッチ処理**: 複数キーワードの連続処理
- **環境変数対応**: CI/CD環境での柔軟な設定

## 💻 動作環境

### 必須要件

- **Python**: 3.11 以上
- **OS**: Linux, macOS, Windows
- **メモリ**: 512MB 以上推奨

### 必要なAPIとサービス

1. **YouTube Data API v3**
   - APIキーが必要
   - デフォルトクォータ: 10,000ユニット/日

2. **Google Sheets API** (Sheets出力を使用する場合)
   - サービスアカウント認証情報が必要
   - Google Cloud Projectの設定が必要

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/Jun2664/yt-channel-autolist.git
cd yt-channel-autolist
```

### 2. Python仮想環境の作成（推奨）

```bash
# venvの作成
python -m venv venv

# 仮想環境の有効化
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. YouTube Data API の設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成 or 既存プロジェクトを選択
3. 「APIとサービス」→「ライブラリ」から **YouTube Data API v3** を検索して有効化
4. 「認証情報」→「認証情報を作成」→「APIキー」でキーを生成
5. 必要に応じてAPIキーに制限を設定（推奨）

### 5. Google Sheets API の設定（オプション）

Google Sheetsへの出力を使用する場合：

1. 同じGoogle Cloud Projectで **Google Sheets API** を有効化
2. サービスアカウントの作成:
   ```
   「認証情報」→「認証情報を作成」→「サービスアカウント」
   - 名前: yt-channel-autolist-service (任意)
   - ロール: 編集者
   ```
3. JSONキーの生成:
   ```
   作成したサービスアカウント → 「キー」タブ → 「鍵を追加」→ 「新しい鍵を作成」→ JSON形式
   ```
4. ダウンロードしたJSONファイルを安全に保管

### 6. 環境変数の設定

#### 方法1: 環境変数を直接設定

```bash
# YouTube API キー
export YOUTUBE_API_KEY="your-youtube-api-key-here"

# Google Service Account JSON（JSONファイルの内容全体）
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'
```

#### 方法2: .envファイルを使用（推奨）

プロジェクトルートに `.env` ファイルを作成:

```env
# API Keys
YOUTUBE_API_KEY=your-youtube-api-key-here
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'

# Optional: Default region
DEFAULT_REGION=JP
```

### 7. キーワードファイルの準備

`keywords.txt` を編集し、検索キーワードを1行に1つずつ記載:

```text
tutorial
how to
programming
machine learning
```

## 📖 使い方

### 基本的な使用方法

```bash
# 日本市場のチャンネルを検索（デフォルト）
python main.py

# 米国市場のチャンネルを検索
python main.py --region US

# カスタムキーワードファイルを使用
python main.py --keywords-file custom_keywords.txt
```

### コマンドライン引数

| 引数 | 説明 | デフォルト | 選択肢 |
|------|------|------------|--------|
| `--region` | 対象地域 | JP | JP, US, EN, ES, PT, BR |
| `--lang` | 言語コード | 地域から自動検出 | 任意の言語コード |
| `--keywords-file` | キーワードファイルパス | keywords.txt | 任意のファイルパス |
| `--output-format` | 出力形式 | sheets | sheets, json, csv |

### 使用例

```bash
# スペイン語圏のチャンネルをJSON形式で出力
python main.py --region ES --output-format json

# ブラジル市場をカスタムキーワードでCSV出力
python main.py --region BR --keywords-file keywords_br.txt --output-format csv

# 英語圏チャンネルをGoogle Sheetsに出力（デフォルト）
python main.py --region EN
```

### GitHub Actions での自動実行

`.github/workflows/youtube-scraper.yml` を作成:

```yaml
name: YouTube Channel Discovery

on:
  schedule:
    # 毎週月曜日 9:00 JST (0:00 UTC) に実行
    - cron: '0 0 * * 1'
  workflow_dispatch:

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
```

## 🧪 開発・テスト

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt  # 存在する場合

# コードフォーマッター（Black）のインストール
pip install black

# リンター（Flake8）のインストール
pip install flake8
```

### テストの実行

```bash
# 単体テストの実行
python -m pytest

# 特定機能のテスト
python test_overseas_features.py
python test_personal_branding.py

# カバレッジ付きテスト実行
python -m pytest --cov=. --cov-report=html
```

### コーディング規約

- **フォーマッター**: Black（行長88文字）
- **リンター**: Flake8
- **型ヒント**: 可能な限り使用を推奨
- **Docstring**: Google スタイル

```bash
# コードフォーマット
black .

# リントチェック
flake8 .
```

### ブランチ戦略

- `main`: 本番環境用の安定版
- `develop`: 開発用ブランチ
- `feature/*`: 新機能開発
- `bugfix/*`: バグ修正
- `docs/*`: ドキュメント更新

## 📁 プロジェクト構成

```
yt-channel-autolist/
├── README.md               # このファイル
├── requirements.txt        # Python依存関係
├── .env.example           # 環境変数テンプレート
├── keywords.txt           # デフォルトキーワードリスト
│
├── main.py                # エントリーポイント
├── config.py              # 設定管理
├── youtube_scraper.py     # YouTube API連携とスクレイピング
├── sheets_writer.py       # Google Sheets出力
├── keyword_extractor.py   # キーワード分析
├── keyword_research_api.py # 外部キーワードAPI連携
│
├── test_overseas_features.py  # 海外市場機能テスト
├── test_personal_branding.py  # 個人ブランディング検出テスト
│
└── .github/
    └── workflows/         # GitHub Actions設定
```

### 主要モジュールの説明

- **main.py**: CLIインターフェースとメイン処理フロー
- **config.py**: 地域別設定と環境変数管理
- **youtube_scraper.py**: YouTube Data API呼び出しとチャンネルフィルタリング
- **keyword_extractor.py**: NLTK使用のキーワード抽出と頻度分析
- **sheets_writer.py**: Google Sheets APIを使用したデータ出力

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. APIキーエラー
```
Error: Invalid API key
```
**解決方法**:
- 環境変数 `YOUTUBE_API_KEY` が正しく設定されているか確認
- APIキーがYouTube Data API v3で有効になっているか確認
- APIキーの制限設定を確認

#### 2. Google認証エラー
```
Error: Could not authenticate with Google Sheets
```
**解決方法**:
- `GOOGLE_SERVICE_ACCOUNT_JSON` が正しいJSON形式か確認
- サービスアカウントにGoogle Sheets APIアクセス権限があるか確認
- Google Cloudプロジェクトで Sheets API が有効か確認

#### 3. APIクォータ超過
```
Error: Quota exceeded
```
**解決方法**:
- YouTube API の日次クォータを確認（デフォルト10,000ユニット）
- キーワード数を減らすか、実行頻度を調整
- 必要に応じてGoogle Cloudコンソールでクォータ増加をリクエスト

#### 4. 依存関係エラー
```
ModuleNotFoundError: No module named 'xxx'
```
**解決方法**:
```bash
pip install -r requirements.txt --upgrade
```

### デバッグモード

詳細なログ出力を有効にする:

```bash
# 環境変数でデバッグモードを有効化
export DEBUG=true
python main.py
```

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

### 貢献の方法

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 開発ガイドライン

- コードは Black でフォーマット
- テストを追加/更新
- ドキュメントを更新
- コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/) に従う

### 報告・提案

- **バグ報告**: [Issues](https://github.com/Jun2664/yt-channel-autolist/issues)
- **機能提案**: [Discussions](https://github.com/Jun2664/yt-channel-autolist/discussions)
- **セキュリティ問題**: メールで直接連絡

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

```
MIT License

Copyright (c) 2024 Jun2664

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <p>
    <strong>開発者:</strong> <a href="https://github.com/Jun2664">@Jun2664</a>
  </p>
  <p>
    <a href="https://github.com/Jun2664/yt-channel-autolist/issues">Issues</a> •
    <a href="https://github.com/Jun2664/yt-channel-autolist/pulls">Pull Requests</a> •
    <a href="https://github.com/Jun2664/yt-channel-autolist/discussions">Discussions</a>
  </p>
</div>

<!-- Last updated: 2025-06-05 -->