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
    """Geminiに投げるプロンプトを組み立てる関数 ★★★シングルツイート版★★★"""
    return f"""
# 指令書: Xアカウント「ゲームの妖精アプりん」の自律型コンテンツ生成

あなたは、Xで絶大な人気を誇る、誠実で信頼性の高いゲーム紹介の専門家AI「ゲームの妖精アプりん」です。
以下の情報を基に、Xに投稿するための【1つの完結したツイート】用の文章を生成してください。

## 1. 基本情報
- アプリ名: {app_info.get('アプリ名', '')}

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
- タスクAの調査結果を基に、このゲームの【魅力的な紹介文】と【役立つワンポイント情報（序盤攻略のコツなど）】を自然に組み合わせ、1つの魅力的な投稿文を作成してください。
- ★★★【最重要制約】★★★
- **生成するのは【紹介文の原稿】のみです。**
- **文章は、必ず日本語で【180文字】以内に厳密に収めてください。これは絶対のルールです。**
- **アフィリエイトリンク、ハッシュタグ、@メンションは一切含めないでください。純粋な文章のブロックだけを生成してください。**
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
        tweet_body = response.text.strip() # ★★★変更点：1つの文章として受け取る★★★

        if not tweet_body:
             raise Exception("Geminiが空のコンテンツを生成しました。")
        print("  ✅ コンテンツ原稿の生成成功")

        # プログラムによる文字数チェックと強制カット
        MAX_CHARS = 180
        if len(tweet_body) > MAX_CHARS:
            print(f"  ⚠️ Geminiが文字数制限({MAX_CHARS}字)を超過！プログラムで強制的にカットします。")
            tweet_body = tweet_body[:MAX_CHARS] + "…"
        
        # プログラムによる最終的なツイートの組み立て
        hashtags = f"#PR {app_info.get('公式ハッシュタグ', '')} #ゲーム紹介 #スマホゲーム #おすすめゲーム"
        # ★★★変更点：スレッド誘導文を削除し、ダウンロード誘導文に変更★★★
        final_tweet_text = f"{tweet_body}\n\n▼ダウンロードはこちら\n{app_info.get('アフィリエイトリンク', '')}\n{hashtags}"

        print(f"  - 組み立て後のツイート: {final_tweet_text[:70]}...")

    except Exception as e:
        print(f"  ❌ Geminiでのコンテンツ生成または組み立てに失敗しました: {e}")
        return

    print("STEP 6: Xにシングルツイートを投稿中...")
    try:
        # ★★★変更点：投稿処理を1回だけにする★★★
        client.create_tweet(text=final_tweet_text)
        print("  ✅ 投稿が完了しました！")
    except Exception as e:
        print(f"  ❌ Xへの投稿に失敗しました: {e}")


if __name__ == "__main__":
    main()
