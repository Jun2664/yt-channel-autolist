#!/usr/bin/env python3
"""属人性判定機能のテストスクリプト"""

# テスト用のチャンネルデータ
test_channels = [
    {
        'title': 'Tech Tutorial Channel',
        'description': 'Learn programming and technology',
        'videos': [
            {'title': 'Python Tutorial #1'},
            {'title': 'JavaScript Basics'},
            {'title': 'How to use Git'}
        ]
    },
    {
        'title': '太郎の部屋',
        'description': '私の日常生活を配信しています',
        'videos': [
            {'title': '私の朝のルーティン'},
            {'title': '僕の好きな料理'},
            {'title': '自分の部屋紹介'}
        ]
    },
    {
        'title': 'John Vlog Channel',
        'description': 'My daily life and personal experiences',
        'videos': [
            {'title': 'My morning routine'},
            {'title': 'Face reveal!'},
            {'title': 'Day in my life vlog'}
        ]
    },
    {
        'title': 'Science Experiments',
        'description': 'Educational science content for everyone',
        'videos': [
            {'title': 'Chemistry experiment #5'},
            {'title': 'Physics demonstration'},
            {'title': 'Biology facts'}
        ]
    }
]

# YouTubeScraperのcheck_personal_brandingメソッドをテスト
from youtube_scraper import YouTubeScraper

# ダミーのAPIキーでインスタンス作成（実際のAPI呼び出しはしない）
scraper = YouTubeScraper('dummy_key')

print("=== 属人性判定テスト結果 ===\n")

for i, channel_data in enumerate(test_channels, 1):
    print(f"テスト {i}: {channel_data['title']}")
    
    # check_personal_brandingメソッドを呼び出し
    is_low_personal = scraper.check_personal_branding(channel_data, channel_data['videos'])
    
    print(f"  属人性が低い: {is_low_personal}")
    print(f"  スコア: {channel_data.get('personal_branding_score', 0)}")
    print(f"  判定理由: {channel_data.get('personal_branding_reasons', '')}")
    print("-" * 50)

print("\n期待される結果:")
print("- テスト 1 (Tech Tutorial): 属人性が低い（True）")
print("- テスト 2 (太郎の部屋): 属人性が高い（False）")
print("- テスト 3 (John Vlog): 属人性が高い（False）")
print("- テスト 4 (Science Experiments): 属人性が低い（True）")