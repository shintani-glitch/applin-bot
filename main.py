import pyshorteners
import sheets
import content_generator
import twitter_api
from datetime import datetime
import pytz

def is_post_time():
    """現在が投稿すべき時間かを判定する"""
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    weekday = now.weekday()  # 月曜=0, ..., 日曜=6
    hour = now.hour

    # 平日 (月曜〜金曜) の投稿時間
    if 0 <= weekday <= 4 and hour in [0, 7, 9, 12, 15, 18, 19, 20, 21, 22, 23]:
        return True
        
    # 休日 (土曜・日曜) の投稿時間
    if weekday >= 5 and hour in [0, 9, 11, 12, 14, 16, 18, 19, 20, 21, 22, 23]:
        return True
            
    return False

def main():
    if not is_post_time():
        jst = pytz.timezone('Asia/Tokyo')
        print(f"現在時刻 ({datetime.now(jst).strftime('%H:%M')}) は投稿時間外です。処理をスキップします。")
        return

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

    # STEP 4: 最終的なツイートの組み立てと投稿
    print("STEP 4: 最終的なツイートの組み立てと投稿...")
    try:
        # --- URL短縮 ---
        print("  - URLを短縮中...")
        original_link = app_info.get('アフィリエイトリンク', '')
        short_link = original_link 
        if original_link:
            try:
                s = pyshorteners.Shortener()
                short_link = s.tinyurl.short(original_link)
                print(f"  ✅ URLを短縮しました: {short_link}")
            except Exception as e:
                print(f"  ⚠️ URLの短縮に失敗しました: {e}。元のリンクを使用します。")
                short_link = original_link
        
        # --- ツイートの組み立て ---
        print("  - ツイートを組み立て中...")
        catchphrase = tweet_parts.get("catchphrase", "おすすめゲーム見つけたよ！")
        benefits = tweet_parts.get("benefits", [])
        generated_hashtags = tweet_parts.get("hashtags", [])

        tweet_lines = []
        if catchphrase:
            tweet_lines.append(f"✨ {catchphrase} ✨")
        tweet_lines.append(f"【{app_info.get('アプリ名', '')}】")
        tweet_lines.append("")
        for benefit in benefits:
            tweet_lines.append(f"✅ {benefit}")
        tweet_lines.append("")
        
        # ★★★ ここが今回の修正点です ★★★
        tweet_lines.append("▽アプリストアでチェック👇")
        
        tweet_lines.append(short_link)
        tweet_lines.append("")

        base_hashtags = ["#PR", app_info.get('公式ハッシュタグ', '')]
        all_hashtags = base_hashtags + generated_hashtags
        hashtag_string = " ".join(filter(None, all_hashtags))
        tweet_lines.append(hashtag_string)

        final_tweet = "\n".join(filter(None, tweet_lines))
        print(f"  - 組み立て完了:\n{final_tweet}")
        
        # --- ツイート投稿 ---
        twitter_api.post_tweet(client_v2, final_tweet, media_id)

    except Exception as e:
        print(f"  ❌ ツイートの組み立てまたは投稿で予期せぬエラーが発生しました: {e}")
        return

    print("\n全ての処理が完了しました。")

if __name__ == "__main__":
    main()
