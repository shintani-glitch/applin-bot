# sheets.py

import gspread
import random
import unicodedata
import os
from dotenv import load_dotenv

load_dotenv()

def get_eligible_app():
    print("STEP 1: スプレッドシートに接続し、データを取得中...")
    try:
        gc = gspread.service_account(filename='google_credentials.json')
        spreadsheet = gc.open(os.getenv('SPREADSHEET_NAME'))
        worksheet = spreadsheet.sheet1
        all_apps = worksheet.get_all_records()
        print(f"  ✅ 全{len(all_apps)}件のデータを取得完了")
    except Exception as e:
        print(f"  ❌ スプレッドシートへの接続またはデータ取得に失敗: {e}")
        return None

    print("  - 投稿可能なアプリをフィルタリング中...")
    eligible_apps = [
        app for app in all_apps 
        if unicodedata.normalize('NFKC', str(app.get('紹介可能FLG', ''))).strip().upper() == 'OK'
    ]

    if not eligible_apps:
        print("  ❌ 投稿可能なアプリが見つかりませんでした。")
        return None

    app_info = random.choice(eligible_apps)
    print(f"  ✅ 選ばれたアプリ: {app_info.get('アプリ名')} (対象: {len(eligible_apps)}件)")
    return app_info
