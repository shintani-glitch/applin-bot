import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime

print("--- X API 書き込み権限 最終テスト開始 ---")

# .envファイルから環境変数を読み込み
load_dotenv()

# X (Twitter)認証
try:
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
    )
    print("✅ 認証クライアントの作成に成功")
except Exception as e:
    print(f"❌ 認証クライアントの作成でエラー: {e}")
    exit()

# スパム判定を避けるため、現在時刻を入れて毎回違う内容のツイートを作成
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S JST")
tweet_text = f"これはAPIからの自動テスト投稿です。({timestamp}) This is an automated test post from the API."

# 投稿を実行
try:
    print(f"以下の内容で投稿を試みます: '{tweet_text}'")
    response = client.create_tweet(text=tweet_text)
    print("\n✅✅✅ 投稿に成功しました！ ✅✅✅")
    # 成功した場合、投稿へのリンクを表示します（'user'の部分はあなたのXのユーザー名に置き換えてください）
    print(f"投稿URL: https://twitter.com/user/status/{response.data['id']}")

except Exception as e:
    print("\n❌❌❌ 投稿に失敗しました ❌❌❌")
    print(f"受信したエラー: {e}")

print("\n--- テスト終了 ---")
