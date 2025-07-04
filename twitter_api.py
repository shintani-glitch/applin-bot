import tweepy
import requests
import io
import os
from dotenv import load_dotenv

load_dotenv()

def get_clients():
    """X API v1.1 と v2 のクライアントを両方作成して返す"""
    try:
        client_v2 = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
        )
        auth_v1 = tweepy.OAuth1UserHandler(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
        )
        api_v1 = tweepy.API(auth_v1)
        print("  ✅ X (Twitter)認証成功")
        return client_v2, api_v1
    except Exception as e:
        print(f"  ❌ X (Twitter)認証に失敗: {e}")
        return None, None

def upload_image(api_v1, image_url):
    """画像をダウンロードしてXにアップロードし、メディアIDを返す"""
    if not image_url:
        print("  - 画像URLがないため、画像処理をスキップします。")
        return None
        
    print(f"  - 画像をダウンロード中: {image_url}")
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        
        print("  - 画像をXにアップロード中...")
        media = api_v1.media_upload(filename="image.jpg", file=image_data)
        media_id = media.media_id_string
        print(f"  ✅ 画像アップロード成功 (Media ID: {media_id})")
        return media_id
    except Exception as e:
        print(f"  ⚠️ 画像のアップロードに失敗: {e}。テキストのみで投稿を続けます。")
        return None

def post_tweet(client_v2, text, media_id=None):
    """ツイートを投稿する"""
    print("STEP 5: Xにツイートを投稿中...")
    try:
        if media_id:
            client_v2.create_tweet(text=text, media_ids=[media_id])
        else:
            client_v2.create_tweet(text=text)
        print("\n  ✅✅✅ 投稿が完了しました！ ★★★")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")
