import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SheetsWriter:
    def __init__(self, credentials_json):
        """Google Sheetsの認証と初期化"""
        # JSON文字列から認証情報を作成
        creds_dict = json.loads(credentials_json)
        
        # スコープの設定
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # 認証
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        self.client = gspread.authorize(creds)
        
    def write_to_sheet(self, sheet_name, worksheet_name, channels):
        """チャンネル情報をスプレッドシートに書き込み"""
        try:
            # スプレッドシートを開く（なければ作成）
            try:
                sheet = self.client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                sheet = self.client.create(sheet_name)
                # 作成したシートを共有設定（任意のメールアドレスと共有する場合）
                # sheet.share('your-email@example.com', perm_type='user', role='writer')
            
            # ワークシートを取得（なければ作成）
            try:
                worksheet = sheet.worksheet(worksheet_name)
                # 既存のデータをクリア
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            
            # ヘッダー行を作成
            headers = [
                'チャンネル名',
                'チャンネルURL',
                '登録者数',
                '投稿数',
                'チャンネル開設日',
                'トップ動画1 URL',
                'トップ動画1 拡散率',
                'トップ動画2 URL',
                'トップ動画2 拡散率',
                'トップ動画3 URL',
                'トップ動画3 拡散率',
                'キーワード',
                '属人性判定',
                '更新日時'
            ]
            
            # データ行を作成
            rows = [headers]
            
            for channel in channels:
                row = [
                    channel['channel_name'],
                    channel['channel_url'],
                    channel['subscriber_count'],
                    channel['video_count'],
                    self.format_date(channel['created_date']),
                ]
                
                # トップ3動画の情報を追加
                for i in range(3):
                    if i < len(channel['high_spread_videos']):
                        video = channel['high_spread_videos'][i]
                        row.extend([
                            video['url'],
                            f"{video['spread_rate']:.2f}"
                        ])
                    else:
                        row.extend(['', ''])
                
                # その他の情報を追加
                row.extend([
                    channel.get('keyword', ''),
                    '顔出しなし' if channel.get('is_faceless', False) else '顔出しあり',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])
                
                rows.append(row)
            
            # 一括でデータを書き込み
            worksheet.update('A1', rows)
            
            # 列幅を自動調整（オプション）
            worksheet.format('A1:N1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            print(f"スプレッドシート '{sheet_name}' に {len(channels)} 件のチャンネルを書き込みました。")
            
            return sheet.url
            
        except Exception as e:
            print(f"スプレッドシート書き込みエラー: {e}")
            raise
    
    def format_date(self, date_string):
        """日付を読みやすい形式に変換"""
        try:
            date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return date.strftime('%Y-%m-%d')
        except:
            return date_string