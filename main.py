def main():
    print("処理を開始します...")
    try:
        all_apps = worksheet.get_all_records()
    except Exception as e:
        print(f"スプレッドシートのデータ取得でエラーが発生しました: {e}")
        return

    # ★★★ デバッグコードここから ★★★
    print(f"--- シートから全{len(all_apps)}件のデータを読み込みました ---")
    print("--- データの先頭5件をチェックします ---")
    for i, app in enumerate(all_apps[:5]):
        # 紹介可能FLGのキーと値を丁寧に出力
        flag_value = app.get('紹介可能FLG', 'キーが存在しません') # キーがない場合も考慮
        print(f"{i+1}行目: {app.get('アプリ名', '名前なし')} -> 紹介可能FLGの値: '{flag_value}'")
    print("------------------------------------")
    # ★★★ デバッグコードここまで ★★★

    # フィルタリング処理
    eligible_apps = [app for app in all_apps if app.get('紹介可能FLG') == 'OK']

    if not eligible_apps:
        print("投稿可能なアプリがありませんでした。（フィルタリング後の件数: 0）")
        return

    # ランダムに1つ選ぶ
    app_info = random.choice(eligible_apps)
    print(f"選ばれたアプリ: {app_info['アプリ名']}")

    # (以降のGeminiへの処理は変更なし)
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
