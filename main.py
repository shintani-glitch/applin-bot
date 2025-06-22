import os
import random
import gspread
import google.generativeai as genai
import tweepy
from dotenv import load_dotenv
import unicodedata # ★★★ この行を追加 ★★★

# --- 1. 初期設定と認証 ---
load_dotenv()

# Google認証
# (変更なし)
# ...

# Gemini認証
# (変更なし)
# ...

# X (Twitter)認証
# (変更なし)
# ...

# --- 2. メイン処理 ---
def get_prompt(app_info):
    # (この関数の中身は変更なし)
    return f"""
# 指令書: (省略)
"""

def main():
    print("処理を開始します...")
    try:
        all_apps = worksheet.get_all_records()
    except Exception as e:
        print(f"スプレッドシートのデータ取得でエラーが発生しました: {e}")
        return

    # ★★★【重要】ここからフィルタリング処理を強化版に変更 ★★★
    print(f"--- 全{len(all_apps)}件のデータから投稿可能なアプリを探します... ---")
    
    eligible_apps = []
    for app in all_apps:
        # スプレッドシートから値を取得し、文字列に変換
        flag_value = str(app.get('紹介可能FLG', '')) 
        
        # 全角を半角に正規化し、前後のスペースを削除し、大文字に変換
        normalized_flag = unicodedata.normalize('NFKC', flag_value).strip().upper()
        
        # 補正後の値が'OK'かどうかをチェック
        if normalized_flag == 'OK':
            eligible_apps.append(app)
            
    # ★★★ フィルタリング処理ここまで ★★★

    if not eligible_apps:
        print("投稿可能なアプリがありませんでした。（フィルタリング後の件数: 0）")
        return

    # ランダムに1つ選ぶ
    app_info = random.choice(eligible_apps)
    print(f"選ばれたアプリ: {app_info['アプリ名']} (投稿可能なアプリ総数: {len(eligible_apps)}件)")

    # (以降のGeminiへの処理とXへの投稿処理は変更なし)
    prompt = get_prompt(app_info)
    try:
        response = model.generate_content(prompt)
        # レスポンスから1通目と2通目のテキストを抽出
        parts = response.text.split("【2通目】")
        first_tweet_text = parts[0].replace("【1通目】", "").strip()
        second_tweet_text = parts[1].strip() if len(parts) > 1 else ""

        if not first_tweet_text or not second_tweet_text:
             raise Exception("期待した形式でコンテンツが生成されませんでした。")

    except Exception as e:
        print(f"Geminiでのコンテンツ生成に失敗しました: {e}")
        return

    # Xにスレッドを投稿
    try:
        print("1通目を投稿中...")
        first_tweet = client.create_tweet(text=first_tweet_text)
        print("2通目を投稿中...")
        client.create_tweet(text=second_tweet_text, in_reply_to_tweet_id=first_tweet.data['id'])
        print("投稿が完了しました！")
    except Exception as e:
        print(f"Xへの投稿に失敗しました: {e}")


if __name__ == "__main__":
    main()
