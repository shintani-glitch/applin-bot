import os
import random
import gspread
import tweepy
from dotenv import load_dotenv
import unicodedata
import requests # ★★★ 追加 ★★★
import io       # ★★★ 追加 ★★★

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

# ★★★ X API v1.1 と v2 の両方を認証（v1.1は画像アップロード用）★★★
print("STEP 2: X (Twitter) APIで認証中...")
try:
    # v2 API Client (ツイート投稿用)
    client_v2 = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
    
    # v1.1 API (メディアアップロード用)
    auth_v1 = tweepy.OAuth1UserHandler(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
    api_v1 = tweepy.API(auth_v1)
    
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
    eligible_apps = [app for app in all_apps if unicodedata.normalize('NFKC', str(app.get('紹介可能FLG', ''))).strip().upper() == 'OK']
    if not eligible_apps:
        print("  ❌ 投稿可能なアプリがありませんでした。（フィルタリング後の件数: 0）")
        return

    app_info = random.choice(eligible_apps)
    print(f"  ✅ 選ばれたアプリ: {app_info['アプリ名']} (投稿可能なアプリ総数: {len(eligible_apps)}件)")

    # ★★★ STEP 4: 画像のアップロード処理 ★★★
    media_id = None
    image_url = app_info.get('画像URL', '')
    if image_url:
        print("STEP 4: 画像を処理中...")
        try:
            print(f"  - 画像をダウンロード中: {image_url}")
            response = requests.get(image_url)
            response.raise_for_status() # エラーがあればここで例外発生
            
            image_data = io.BytesIO(response.content)
            
            print("  - 画像をXにアップロード中...")
            # media_uploadはファイル名を必須とするため、ダミーの名前を渡す
            media = api_v1.media_upload(filename="image.jpg", file=image_data)
            media_id = media.media_id_string
            print(f"  ✅ 画像アップロード成功 (Media ID: {media_id})")
        except Exception as e:
            print(f"  ⚠️ 画像のアップロードに失敗しました: {e}。テキストのみで投稿を続けます。")
            media_id = None
    else:
        print("STEP 4: 画像URLがないため、画像処理をスキップします。")


    print("STEP 5: ツイート内容を組み立て中 (AI不使用)...")
    try:
        app_name = app_info.get('アプリ名', '')
        affiliate_link = app_info.get('アフィリエイトリンク', '')
        official_account = app_info.get('公式Xアカウント', '')
        official_hashtag = app_info.get('公式ハッシュタグ', '')

        if not app_name or not affiliate_link:
            raise ValueError("スプレッドシートの「アプリ名」または「アフィリエイトリンク」が空です。")

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
        
        final_tweet_text = "\n".join(filter(None, tweet_lines))
        print(f"  ✅ 組み立て完了:\n{final_tweet_text}")

    except Exception as e:
        print(f"  ❌ ツイートの組み立てに失敗しました: {e}")
        return

    print("STEP 6: Xにツイートを投稿中...")
    try:
        # media_idがある場合は、ツイートに添付する
        if media_id:
            client_v2.create_tweet(text=final_tweet_text, media_ids=[media_id])
        else:
            client_v2.create_tweet(text=final_tweet_text)
            
        print("\n  ✅✅✅ 投稿が完了しました！ ★★★")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")


if __name__ == "__main__":
    main()
