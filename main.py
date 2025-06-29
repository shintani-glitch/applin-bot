import os
import random
import gspread
import tweepy
from dotenv import load_dotenv
import unicodedata

# --- 1. 初期設定と認証 ---
load_dotenv()

# Google認証
print("STEP 1: Googleサービスアカウントで認証中...")
try:
    gc = gspread.service_account(filename='google_credentials.json')
    spreadsheet = gc.open(os.getenv('SPREADSHEET_NAME'))
    worksheet = spreadsheet.sheet1
    print("  ✅ Google認証成功")
except Exception as e:
    print(f"  ❌ Google認証またはスプレッドシートのオープンに失敗しました: {e}")
    exit()

# X (Twitter)認証
print("STEP 2: X (Twitter) APIで認証中...")
try:
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
    print("  ✅ X (Twitter)認証成功")
except Exception as e:
    print(f"  ❌ X (Twitter)認証に失敗しました: {e}")
    exit()


# --- 2. メイン処理 ---
def main():
    print("\nSTEP 3: メイン処理を開始します...")
    try:
        all_apps = worksheet.get_all_records()
    except Exception as e:
        print(f"  ❌ スプレッドシートのデータ取得でエラーが発生しました: {e}")
        return

    print(f"  - 全{len(all_apps)}件のデータから投稿可能なアプリを探します...")
    
    eligible_apps = []
    for app in all_apps:
        flag_value = str(app.get('紹介可能FLG', '')) 
        normalized_flag = unicodedata.normalize('NFKC', flag_value).strip().upper()
        if normalized_flag == 'OK':
            eligible_apps.append(app)
            
    if not eligible_apps:
        print("  ❌ 投稿可能なアプリがありませんでした。（フィルタリング後の件数: 0）")
        return

    app_info = random.choice(eligible_apps)
    print(f"  ✅ 選ばれたアプリ: {app_info['アプリ名']} (投稿可能なアプリ総数: {len(eligible_apps)}件)")

    print("STEP 4: ツイート内容を組み立て中 (AI不使用)...")
    try:
        # スプレッドシートから情報を取得
        app_name = app_info.get('アプリ名', '')
        affiliate_link = app_info.get('アフィリエイトリンク', '')
        official_account = app_info.get('公式Xアカウント', '')
        official_hashtag = app_info.get('公式ハッシュタグ', '')

        # 必須項目が空でないかチェック
        if not app_name or not affiliate_link:
            raise ValueError("スプレッドシートの「アプリ名」または「アフィリエイトリンク」が空です。")

        # ツイートの各行を作成
        tweet_lines = [
            f"【✨ゲーム紹介✨】",
            f"「{app_name}」",
            "",
            f"公式アカウントはこちら👉 {official_account}" if official_account else "",
            "",
            "▼ダウンロードはこちら",
            affiliate_link,
            "",
            f"#PR {official_hashtag}"
        ]
        
        # 空の行をフィルタリングして、改行で結合
        final_tweet_text = "\n".join(filter(None, tweet_lines))
        print(f"  ✅ 組み立て完了:\n{final_tweet_text}")

    except Exception as e:
        print(f"  ❌ ツイートの組み立てに失敗しました: {e}")
        return

    print("STEP 5: Xにツイートを投稿中...")
    try:
        client.create_tweet(text=final_tweet_text)
        print("\n  ✅✅✅ 投稿が完了しました！ ★★★")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")


if __name__ == "__main__":
    main()
