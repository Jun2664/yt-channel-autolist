import json
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from datetime import datetime

class SheetsWriter:
    def __init__(self, service_account_json):
        """Google Sheets APIの初期化"""
        try:
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
        except Exception as e:
            raise Exception(f"Failed to initialize Google Sheets API: {str(e)}")
        
    def create_or_get_spreadsheet(self, spreadsheet_name):
        """スプレッドシートを作成または取得"""
        try:
            # 既存のスプレッドシートを開く
            spreadsheet = self.client.open(spreadsheet_name)
            print(f"既存のスプレッドシート '{spreadsheet_name}' を使用します")
        except gspread.SpreadsheetNotFound:
            try:
                # 新しいスプレッドシートを作成
                spreadsheet = self.client.create(spreadsheet_name)
                print(f"新しいスプレッドシート '{spreadsheet_name}' を作成しました")
            except Exception as e:
                # Handle Drive API disabled error
                if 'SERVICE_DISABLED' in str(e) or '403' in str(e):
                    raise Exception(
                        "Google Drive API is not enabled for this project. "
                        "Please enable it in the Google Cloud Console: "
                        "https://console.cloud.google.com/apis/library/drive.googleapis.com"
                    )
                else:
                    raise Exception(f"Failed to create spreadsheet: {str(e)}")
        except Exception as e:
            if not isinstance(e, gspread.SpreadsheetNotFound):
                raise Exception(f"Error accessing Google Sheets: {str(e)}")
            
        return spreadsheet
    
    def prepare_worksheet(self, spreadsheet):
        """Prepare worksheet with headers"""
        worksheet = spreadsheet.get_worksheet(0)
        
        # Set headers (bilingual support)
        headers = [
            'Channel Name',
            'Channel URL',
            'Subscribers',
            'Video Count',
            'Created Date',
            'Top Video 1',
            'Spread Rate 1',
            'Top Video 2', 
            'Spread Rate 2',
            'Top Video 3',
            'Spread Rate 3',
            'Search Keyword',
            'Personal Branding',
            'Reasons',
            'Top Keywords',
            'Region',
            'Update Time'
        ]
        
        # Set headers in first row
        worksheet.update('A1:Q1', [headers])
        
        # Make header row bold
        worksheet.format('A1:Q1', {'textFormat': {'bold': True}})
        
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
                f"https://www.youtube.com/channel/{channel.get('channelId', channel.get('id', ''))}",
                channel['subscriberCount'],
                channel['videoCount'],
                channel.get('publishedAt', '')[:10] if channel.get('publishedAt') else '',  # 日付部分のみ
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
            
            # Add other information
            row.extend([
                channel['search_keyword'],
                'High' if channel.get('is_personal', False) else 'Low',
                channel.get('personal_branding_reasons', ''),
                ', '.join(channel.get('top_keywords', [])[:5]) if 'top_keywords' in channel else '',
                channel.get('region', 'JP'),
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