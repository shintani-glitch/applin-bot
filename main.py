import os
import random
import gspread
import google.generativeai as genai
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

# Gemini認証
print("STEP 2: Gemini APIで認証中...")
try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("  ✅ Gemini認証成功")
except Exception as e:
    print(f"  ❌ Gemini認証に失敗しました: {e}")
    exit()

# X (Twitter)認証
print("STEP 3: X (Twitter) APIで認証中...")
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


# --- 2. 補助関数 ---
def get_prompt(app_info):
    """Geminiに投げるプロンプトを組み立てる関数 ★★★シンプル・最終版★★★"""
    return f"""
# 指令書: X(Twitter)投稿用のゲーム紹介ツイート生成

あなたは、Xで人気のゲーム紹介アカウント「ゲームの妖精アプりん」です。
以下の情報を基に、Xに投稿するための【1つの完結したツイート】を生成してください。

## 1. 基本情報
- アプリ名: {app_info.get('アプリ名', '')}
- アフィリエイトリンク: {app_info.get('アフィリエイトリンク', '')}
- 公式ハッシュタグ: {app_info.get('公式ハッシュタグ', '')}

## 2. 実行タスク
Webで上記のアプリ名について調査し、その魅力、特徴、簡単な攻略のヒントなどを分析してください。

## 3. 生成ルール
- あなたのペルソナ（元気なゲーム好きの妖精「アプりん」、一人称「ボク」）を反映させてください。
- 調査結果に基づき、ゲームの魅力と役立つヒントを組み合わせた、自然で魅力的な文章を作成してください。
- **ツイート全体の文字数がXの制限（280文字）に収まるようにしてください。**
- 必ず、受け取ったアフィリエイトリンクと、`#PR`、そして公式ハッシュタグを含めてください。
- その他にも、インプレッションが増えそうなハッシュタグを2〜3個追加してください。
- 宣伝色が強すぎず、ユーザーに親しみやすく、かつ魅力的に伝わるように工夫してください。
- 箇条書きや絵文字（✨, ✅, 👇など）を効果的に使って、視覚的に分かりやすいツイートを作成してください。
"""

# --- 3. メイン処理 ---
def main():
    print("\nSTEP 4: メイン処理を開始します...")
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

    print("STEP 5: Geminiでツイート全体を生成中...")
    prompt = get_prompt(app_info)
    try:
        response = model.generate_content(prompt)
        final_tweet_text = response.text.strip()

        if not final_tweet_text:
             raise Exception("Geminiが空のコンテンツを生成しました。")
        print("  ✅ コンテンツ生成成功")
        print(f"  - 生成されたツイート:\n{final_tweet_text}")

    except Exception as e:
        print(f"  ❌ Geminiでのコンテンツ生成に失敗しました: {e}")
        return

    print("STEP 6: Xにツイートを投稿中...")
    try:
        client.create_tweet(text=final_tweet_text)
        print("\n  ✅✅✅ 投稿が完了しました！ ★★★")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")


if __name__ == "__main__":
    main()
