# main.py (最終バグ修正版)

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

    # ★★★ STEP 4: ツイートの組み立てと投稿（処理を統合） ★★★
    print("STEP 4: 最終的なツイートの組み立てと投稿...")
    try:
        # --- ツイートの組み立て ---
        print("  - ツイートを組み立て中...")
        s = pyshorteners.Shortener()
        short_link = s.tinyurl.short(app_info.get('アフィリエイトリンク', ''))
        
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
        tweet_lines.append("▼ダウンロードはこちらから👇")
        tweet_lines.append(short_link)
        tweet_lines.append("")

        base_hashtags = ["#PR", app_info.get('公式ハッシュタグ', '')]
        all_hashtags = base_hashtags + generated_hashtags
        hashtag_string = " ".join(filter(None, all_hashtags))
        tweet_lines.append(hashtag_string)

        final_tweet = "\n".join(filter(None, tweet_lines))
        print(f"  - 組み立て完了:\n{final_tweet}")
        
        # --- ツイート投稿 ---
        print("  - Xにツイートを投稿中...")
        twitter_api.post_tweet(client_v2, final_tweet, media_id)

    except Exception as e:
        print(f"  ❌ ツイートの組み立てまたは投稿に失敗しました: {e}")
        return

    print("\n全ての処理が完了しました。")

if __name__ == "__main__":
    main()
