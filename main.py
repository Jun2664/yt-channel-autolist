#!/usr/bin/env python3
"""
YouTube Channel Auto-Lister
属人性のない伸びている海外チャンネルを自動リストアップ
"""

import os
import sys
from datetime import datetime
from youtube_scraper import YouTubeScraper
from sheets_writer import SheetsWriter

def main():
    """メイン処理"""
    print("=== YouTube Channel Auto-Lister ===")
    print(f"実行開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 環境変数から認証情報を取得
    youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
    google_service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if not youtube_api_key:
        print("エラー: YOUTUBE_API_KEY が設定されていません")
        sys.exit(1)
        
    if not google_service_account_json:
        print("エラー: GOOGLE_SERVICE_ACCOUNT_JSON が設定されていません")
        sys.exit(1)
    
    try:
        # YouTube Scraper の初期化
        print("\n1. YouTube API に接続中...")
        scraper = YouTubeScraper(youtube_api_key)
        
        # キーワードファイルからチャンネルを検索
        print("\n2. チャンネルを検索中...")
        channels = scraper.search_channels_by_keywords('keywords.txt')
        print(f"   条件を満たすチャンネル数: {len(channels)}")
        
        if channels:
            # チャンネル情報を表示
            print("\n3. 見つかったチャンネル:")
            for i, channel in enumerate(channels[:5], 1):  # 最初の5件のみ表示
                print(f"   {i}. {channel['channel_name']} (登録者: {channel['subscriber_count']:,}人)")
            
            if len(channels) > 5:
                print(f"   ... 他 {len(channels) - 5} チャンネル")
            
            # Google Sheets に書き込み
            print("\n4. Google スプレッドシートに書き込み中...")
            writer = SheetsWriter(google_service_account_json)
            
            # シート名とワークシート名
            sheet_name = "YouTube Channel Auto List"
            worksheet_name = datetime.now().strftime('%Y-%m-%d')
            
            # データを書き込み
            sheet_url = writer.write_to_sheet(sheet_name, worksheet_name, channels)
            print(f"   書き込み完了: {sheet_url}")
            
        else:
            print("\n条件を満たすチャンネルが見つかりませんでした。")
            print("キーワードや条件を見直してください。")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n実行完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()