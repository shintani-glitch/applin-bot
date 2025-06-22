import os
import random
import gspread
import google.generativeai as genai
import tweepy
from dotenv import load_dotenv
import unicodedata

# --- 1. 初期設定と認証 ---
# (変更なし)
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
    """Geminiに投げるプロンプトを組み立てる関数"""
    return f"""
# 指令書: Xアカウント「ゲームの妖精アプりん」の自律型コンテンツ生成

あなたは、Xで絶大な人気を誇る、誠実で信頼性の高いゲーム紹介の専門家AI「ゲームの妖精アプりん」です。
以下の情報を基に、Xに投稿するためのスレッドコンテンツを【あなたの調査・分析能力を最大限に活用して】生成してください。

## 1. 基本情報
- アプリ名: {app_info.get('アプリ名', '')}

## 2. 実行タスク (省略)

## 3. 出力要件
#### 【1通目の投稿（メイン紹介）】
- ★★★【重要・今回の変更点】★★★
- タスクAの調査結果から導き出した、このゲームの最も魅力的な「紹介ポイント」を3つに絞り、それを基に140字以内の紹介文を作成してください。
- **アフィリエイトリンク、ハッシュタグ、@メンションは一切含めないでください。純粋な文章のみを生成してください。**
- スレッド誘導文「このゲームの攻略ヒントはリプ欄へ！👇」も忘れずに入れてください。

#### 【2通目の投稿（深掘り情報）】
- タスクAの調査結果に基づき、プレイヤーにとって最も有益で具体的な「深掘りテーマ」を1つ設定し、そのテーマに沿って役立つ情報を140字以内で作成してください。
- こちらにも、リンクやハッシュタグ、メンションは一切含めないでください。

## 4. 出力形式 (この形式を厳守)
【1通目】
(生成された文章)
【2通目】
(生成された文章)
"""

# --- 3. メイン処理 ---
def main():
    # (main関数の中身は、前回から変更ありません)
    print("\nSTEP 4: メイン処理を開始します...")
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

    print("STEP 5: Geminiでコンテンツを生成中...")
    prompt = get_prompt(app_info)
    try:
        response = model.generate_content(prompt)
        parts = response.text.split("【2通目】")
        first_tweet_text = parts[0].replace("【1通目】", "").strip()
        second_tweet_text = parts[1].strip() if len(parts) > 1 else ""

        if not first_tweet_text or not second_tweet_text:
             raise Exception("期待した形式でコンテンツが生成されませんでした。")
        print("  ✅ コンテンツ生成成功")
        print(f"  - 生成された1通目: {first_tweet_text[:50]}...") # ログに少しだけ表示
        print(f"  - 生成された2通目: {second_tweet_text[:50]}...") # ログに少しだけ表示

    except Exception as e:
        print(f"  ❌ Geminiでのコンテンツ生成に失敗しました: {e}")
        return

    print("STEP 6: Xにスレッドを投稿中...")
    try:
        first_tweet = client.create_tweet(text=first_tweet_text)
        client.create_tweet(text=second_tweet_text, in_reply_to_tweet_id=first_tweet.data['id'])
        print("  ✅ 投稿が完了しました！")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")

if __name__ == "__main__":
    main()
