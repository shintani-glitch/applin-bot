import os
import random
import gspread
import google.generativeai as genai
import tweepy
from dotenv import load_dotenv
import unicodedata

# --- 1. 初期設定と認証 ---
# (変更なし)
# ... (以前のコードと同じ)
load_dotenv()
gc = gspread.service_account(filename='google_credentials.json')
spreadsheet = gc.open(os.getenv('SPREADSHEET_NAME'))
worksheet = spreadsheet.sheet1
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)

# --- 2. 補助関数 ---
def get_prompt(app_info):
    # (プロンプト内容は変更なし)
    return f"""
# 指令書: (省略)
"""

# --- 3. メイン処理 ---
def main():
    # (main関数の中身を、ログ出力が分かりやすいように一部変更)
    print("\nSTEP 4: メイン処理を開始します...")
    # ... (データ取得、フィルタリング処理は変更なし)
    try:
        all_apps = worksheet.get_all_records()
    except Exception as e:
        print(f"  ❌ スプレッドシートのデータ取得でエラーが発生しました: {e}")
        return

    print(f"  - 全{len(all_apps)}件のデータから投稿可能なアプリを探します...")
    eligible_apps = [app for app in all_apps if unicodedata.normalize('NFKC', str(app.get('紹介可能FLG', ''))).strip().upper() == 'OK']
    if not eligible_apps:
        print("  ❌ 投稿可能なアプリがありませんでした。（フィルタリング後の件数: 0）")
        return

    app_info = random.choice(eligible_apps)
    print(f"  ✅ 選ばれたアプリ: {app_info['アプリ名']} (投稿可能なアプリ総数: {len(eligible_apps)}件)")

    print("STEP 5: Geminiでコンテンツを生成中...")
    prompt = get_prompt(app_info)
    try:
        print("  - Geminiにリクエストを送信...")
        response = model.generate_content(prompt)
        
        # ★★★【重要・今回の変更点】★★★
        # Geminiからの生の応答をログに分かりやすく全文表示する
        print("\n---【Geminiからの生の応答ここから】---")
        print(response.text)
        print("---【Geminiからの生の応答ここまで】---\n")

        # これ以降で解析
        parts = response.text.split("【2通目】")
        first_tweet_text = parts[0].replace("【1通目】", "").strip()
        second_tweet_text = parts[1].strip() if len(parts) > 1 else ""

        if not first_tweet_text or not second_tweet_text:
             raise Exception("期待した形式でコンテンツが生成されませんでした。")
        print("  ✅ コンテンツ生成成功")

    except Exception as e:
        print(f"  ❌ Geminiでのコンテンツ生成に失敗しました: {e}")
        return

    # Xにスレッドを投稿
    print("STEP 6: Xにスレッドを投稿中...")
    # (Xへの投稿処理は変更なし)
    # ...

if __name__ == "__main__":
    main()
