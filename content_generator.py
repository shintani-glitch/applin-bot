# content_generator.py (JSONモード対応・最終安定版)

import google.generativeai as genai
import google.generativeai.types as genai_types # ★★★ 追加 ★★★
import json
import os
from dotenv import load_dotenv

load_dotenv()

def generate_tweet_parts(app_info):
    """Gemini APIのJSONモードを使ってツイートのパーツを生成する"""
    print("STEP 3: Geminiでコンテンツパーツを生成中 (JSONモード)...")
    try:
        # ★★★ ここからが新しい設定です ★★★
        # 応答形式をJSONに指定
        generation_config = genai_types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # モデルに設定を適用
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )
        # ★★★ 新しい設定ここまで ★★★

        # プロンプトもJSONモードに合わせてシンプル化
        prompt = f"""
        # 指令書: X(Twitter)投稿用のゲーム紹介パーツ生成
        あなたは、Xで人気のゲーム紹介アカウント「ゲームの妖精アプりん」の優秀なコピーライターです。
        Webで「{app_info.get('アプリ名', '')}」について調査し、その魅力や特徴を分析してください。
        
        分析結果を基に、あなたのペルソナ（元気なゲーム好きの妖精「アプりん」、一人称「ボク」）を反映させ、以下のキーを持つJSONオブジェクトを生成してください。
        - catchphrase: ユーザーの目を引く、20文字程度の短いキャッチコピー（文字列）
        - benefits: このゲームの魅力的なポイントを2つ（それぞれ25文字以内）まとめた配列（文字列の配列）
        - hashtags: 調査で見つけたゲームのジャンルや特徴を表すハッシュタグを3つ（`#`から始まる文字列）まとめた配列（文字列の配列）
        """
        
        response = model.generate_content(prompt)
        
        # JSONモードなので、応答テキストをそのままJSONとして解析できる
        tweet_parts = json.loads(response.text)
        
        print("  ✅ コンテンツパーツのJSON解析に成功")
        return tweet_parts
        
    except Exception as e:
        print(f"  ❌ Geminiでのコンテンツ生成またはJSON解析に失敗: {e}")
        # エラー時にAIからの応答内容を確認できるようにログ出力
        if 'response' in locals():
            print(f"  - Geminiからの生の応答:\n{response.text}")
        return None
