#!/usr/bin/env python3
import os
import sys
from youtube_scraper import YouTubeScraper
from sheets_writer import SheetsWriter

def main():
    """メイン処理"""
    # 環境変数から認証情報を取得
    api_key = os.environ.get('YOUTUBE_API_KEY')
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if not api_key:
        print("エラー: YOUTUBE_API_KEY が設定されていません")
        sys.exit(1)
        
    if not service_account_json:
        print("エラー: GOOGLE_SERVICE_ACCOUNT_JSON が設定されていません")
        sys.exit(1)
    
    # キーワードファイルを読み込む
    try:
        with open('keywords.txt', 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("エラー: keywords.txt が見つかりません")
        sys.exit(1)
    
    print(f"検索キーワード数: {len(keywords)}")
    
    # YouTube スクレイパーを初期化
    scraper = YouTubeScraper(api_key)
    
    # 各キーワードで検索・フィルタリング
    for keyword in keywords:
        try:
            scraper.process_keyword(keyword)
        except Exception as e:
            print(f"キーワード '{keyword}' の処理中にエラーが発生しました: {e}")
            continue
    
    # フィルタリングされたチャンネルを取得
    filtered_channels = scraper.get_filtered_channels()
    print(f"\n条件を満たすチャンネル数: {len(filtered_channels)}")
    
    if filtered_channels:
        # Google スプレッドシートに書き込む
        try:
            writer = SheetsWriter(service_account_json)
            spreadsheet_url = writer.write_channels_data(
                'YouTube チャンネル自動リストアップ',
                filtered_channels
            )
            print(f"\nスプレッドシートに書き込みました: {spreadsheet_url}")
        except Exception as e:
            print(f"スプレッドシートへの書き込みエラー: {e}")
            sys.exit(1)
    else:
        print("条件を満たすチャンネルが見つかりませんでした")

if __name__ == '__main__':
    main()