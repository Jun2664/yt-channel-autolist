import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class SheetsWriter:
    def __init__(self, service_account_json):
        """Google Sheets APIの初期化"""
        # サービスアカウントの認証情報をJSONから読み込む
        creds_dict = json.loads(service_account_json)
        
        # 必要なスコープを定義
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 認証情報を作成
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        
        # gspreadクライアントを初期化
        self.client = gspread.authorize(creds)
        
    def create_or_get_spreadsheet(self, spreadsheet_name):
        """スプレッドシートを作成または取得"""
        try:
            # 既存のスプレッドシートを開く
            spreadsheet = self.client.open(spreadsheet_name)
            print(f"既存のスプレッドシート '{spreadsheet_name}' を使用します")
        except gspread.SpreadsheetNotFound:
            # 新しいスプレッドシートを作成
            spreadsheet = self.client.create(spreadsheet_name)
            print(f"新しいスプレッドシート '{spreadsheet_name}' を作成しました")
            
        return spreadsheet
    
    def prepare_worksheet(self, spreadsheet):
        """ワークシートを準備（ヘッダー行を設定）"""
        worksheet = spreadsheet.get_worksheet(0)
        
        # ヘッダー行を設定
        headers = [
            'チャンネル名',
            'チャンネルURL',
            '登録者数',
            '投稿数',
            '開設日',
            'トップ動画1',
            '拡散率1',
            'トップ動画2',
            '拡散率2',
            'トップ動画3',
            '拡散率3',
            '検索キーワード',
            '属人性判定',
            '更新日時'
        ]
        
        # 最初の行にヘッダーを設定
        worksheet.update('A1:N1', [headers])
        
        # ヘッダー行を太字にする
        worksheet.format('A1:N1', {'textFormat': {'bold': True}})
        
        return worksheet
    
    def calculate_diffusion_rate(self, view_count, subscriber_count):
        """拡散率を計算"""
        if subscriber_count == 0:
            return 0
        return round(view_count / subscriber_count, 2)
    
    def write_channels_data(self, spreadsheet_name, channels_data):
        """チャンネルデータをスプレッドシートに書き込む"""
        # スプレッドシートを取得または作成
        spreadsheet = self.create_or_get_spreadsheet(spreadsheet_name)
        worksheet = self.prepare_worksheet(spreadsheet)
        
        # 既存のデータをクリア（ヘッダー行以外）
        worksheet.delete_rows(2, worksheet.row_count - 1)
        
        # データを準備
        rows_data = []
        for channel in channels_data:
            row = [
                channel['title'],
                f"https://www.youtube.com/channel/{channel['id']}",
                channel['subscriberCount'],
                channel['videoCount'],
                channel['publishedAt'][:10],  # 日付部分のみ
            ]
            
            # トップ3動画の情報を追加
            for i, video in enumerate(channel.get('high_diffusion_videos', [])[:3]):
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                diffusion_rate = self.calculate_diffusion_rate(
                    video['viewCount'],
                    channel['subscriberCount']
                )
                row.extend([video_url, diffusion_rate])
            
            # 3本未満の場合は空欄で埋める
            while len(row) < 11:
                row.extend(['', ''])
            
            # その他の情報を追加
            row.extend([
                channel['search_keyword'],
                '低' if channel.get('is_personal', False) == False else '高',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
            
            rows_data.append(row)
        
        # データを一括で書き込む
        if rows_data:
            worksheet.append_rows(rows_data)
            print(f"{len(rows_data)}件のチャンネルデータを書き込みました")
        else:
            print("書き込むデータがありません")
            
        # スプレッドシートのURLを返す
        return spreadsheet.url