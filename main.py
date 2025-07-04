# main.py

import pyshorteners
import sheets
import content_generator
import twitter_api

def main():
    # STEP 1: スプレッドシートから投稿対象のアプリを1つ取得
    app_info = sheets.get_eligible_app()
    if not app_info:
        print("本日の処理を終了します。")
        return

    # STEP 2: 画像の準備
    print("STEP 2: X APIクライアントの準備と画像処理中...")
    client_v2, api_v1 = twitter_api.get_clients()
    if not client_v2 or not api_v1:
        print("本日の処理を終了します。")
        return
    media_id = twitter_api.upload_image(api_v1, app_info.get('画像URL'))

    # STEP 3: ツイート内容のAI生成
    tweet_parts = content_generator.generate_tweet_parts(app_info)
    if not tweet_parts:
        print("本日の処理を終了します。")
        return

    # STEP 4: 最終的なツイートの組み立て
    print("STEP 4: 最終的なツイートを組み立て中...")
    # (以前のコードから変更なし)
    # ...
    
    # STEP 5: ツイート投稿
    twitter_api.post_tweet(client_v2, final_tweet, media_id)
    print("\n全ての処理が完了しました。")

if __name__ == "__main__":
    main()
