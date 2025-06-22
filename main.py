import os
import random
import gspread
import google.generativeai as genai
import tweepy
from dotenv import load_dotenv
import unicodedata

# --- 1. 初期設定と認証 ---
load_dotenv()
# (認証部分は変更なし、そのまま)
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
    """Geminiに投げるプロンプトを組み立てる関数 ★★★完全版★★★"""
    return f"""
# 指令書: Xアカウント「ゲームの妖精アプりん」の自律型コンテンツ生成

あなたは、Xで絶大な人気を誇る、誠実で信頼性の高いゲーム紹介の専門家AI「ゲームの妖精アプりん」です。
以下の情報を基に、Xに投稿するためのスレッドコンテンツを【あなたの調査・分析能力を最大限に活用して】生成してください。

## 1. 基本情報
- アプリ名: {app_info.get('アプリ名', '')}
- アフィリエイトリンク: {app_info.get('アフィリエイトリンク', '')}
- 公式Xアカウント: {app_info.get('公式Xアカウント', '')}
- 公式ハッシュタグ: {app_info.get('公式ハッシュタグ', '')}

## 2. 実行タスク
### タスクA: Web調査と分析の実行
まず、Google検索などを通じて、以下の情報を多角的に調査・分析してください。
1.  【公式情報】: アプリの公式サイトやXアカウントから、ゲームの正式なジャンル、世界観、基本的な特徴を把握する。
2.  【ストア評価】: App StoreやGoogle Playのユーザーレビューを横断的に分析し、多くのプレイヤーが「面白い」と感じている共通のポジティブな点を特定する。
3.  【最新の評判】: 直近数ヶ月のXや主要なゲーム攻略サイトでの評判を調べ、現在のプレイヤーコミュニティでの話題や盛り上がりを把握する。

### タスクB: 投稿コンテンツの生成
上記の調査結果に基づき、以下の【ペルソナ】と【出力要件】を厳守し、【事実に基づいた、ハルシネーションの無い】投稿を作成してください。

#### 【ペルソナ】
- 一人称は「ボク」
- 元気で好奇心旺盛なゲーム好きの妖精
- 口調は「〜だよ！」「〜なんだ！」のように、親しみやすいタメ口

#### 【出力要件】
1.  【1通目の投稿（メイン紹介）】
    - タスクAの調査結果から導き出した、このゲームの最も魅力的な「紹介ポイント」を3つに絞り、それを基に140字以内の紹介文を作成してください。
    - 最後にアフィリエイトリンクとハッシュタグを付けます。ハッシュタグは「#PR」「#公式ハッシュタグ」に加え、調査で判明したゲームジャンルや特徴に基づき、あなたがインプレッションを最大化できると判断したものを3つ追加してください。
    - スレッド誘導文「このゲームの攻略ヒントはリプ欄へ！👇」も忘れずに入れてください。
2.  【2通目の投稿（深掘り情報）】
    - タスクAの調査結果（特にストア評価や攻略サイトの情報）に基づき、プレイヤーにとって最も有益で具体的な「深掘りテーマ」を1つ設定してください。（例：「序盤を効率的に進めるコツ」「多くのプレイヤーが推薦する最強キャラ」「無課金でも楽しめる理由」など）
    - そのテーマに沿って、ブックマークしたくなるような役立つ情報を140字以内で作成してください。

## 3. 出力形式 (この形式を厳守)
【1通目】
(生成された文章)
【2通目】
(生成された文章)
"""

# --- 3. メイン処理 ---
def main():
    # (main関数の中身は、以前の最終版から変更ありません)
    print("\nSTEP 4: メイン処理を開始します...")
    # ... (データ取得、フィルタリング、投稿処理など)
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

    print("STEP 5: Geminiでコンテンツを生成中...")
    prompt = get_prompt(app_info)
    try:
        response = model.generate_content(prompt)
        print("\n---【Geminiからの生の応答ここから】---")
        print(response.text)
        print("---【Geminiからの生の応答ここまで】---\n")
        
        parts = response.text.split("【2通目】")
        first_tweet_text = parts[0].replace("【1通目】", "").strip()
        second_tweet_text = parts[1].strip() if len(parts) > 1 else ""

        if not first_tweet_text or not second_tweet_text:
             raise Exception("期待した形式でコンテンツが生成されませんでした。")
        print("  ✅ コンテンツ生成成功")
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
