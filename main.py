import os

def check_environment_variables():
    """Renderに設定された環境変数を一つずつチェックする関数"""
    print("STEP 3: 環境変数のチェック開始")
    
    # チェックするべきキーのリスト
    required_keys = [
        'SPREADSHEET_NAME',
        'GOOGLE_API_KEY',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET'
    ]
    
    all_ok = True
    for key in required_keys:
        value = os.getenv(key)
        if value:
            # 値の最初と最後の数文字だけ表示して、設定されていることを確認
            # （完全なキーはセキュリティのため表示しない）
            display_value = f"{value[:2]}...{value[-2:]}" if len(value) > 4 else value
            print(f"  ✅ {key}: 設定されています (値: {display_value})")
        else:
            print(f"  ❌ {key}: 未設定です！これが原因の可能性があります。")
            all_ok = False
            
    if all_ok:
        print("STEP 4: 全ての環境変数が正常に読み込めています。")
    else:
        print("STEP 4: 環境変数に未設定の項目がありました。")
        
    return all_ok

def check_secret_file():
    """Renderに設定されたSecret Fileが存在するかチェックする関数"""
    print("STEP 5: Secret Fileのチェック開始")
    
    secret_file_path = 'google_credentials.json'
    
    if os.path.exists(secret_file_path):
        print(f"  ✅ {secret_file_path}: ファイルが見つかりました！")
        # ファイルの中身が空でないかも念のためチェック
        if os.path.getsize(secret_file_path) > 0:
            print("  ✅ ファイルの中身も空ではありません。")
            print("STEP 6: Secret Fileは正常に設定されています。")
            return True
        else:
            print(f"  ❌ {secret_file_path}: ファイルは存在しますが、中身が空です！")
            return False
    else:
        print(f"  ❌ {secret_file_path}: ファイルが見つかりません！これが原因です。")
        print("STEP 6: Secret Fileの設定に問題があります。")
        return False

def main():
    """デバッグ用のメイン処理"""
    print("--- デバッグモード開始 ---")
    print("STEP 1: スクリプトが正常に開始されました。")
    print("STEP 2: ライブラリのインポートは成功しています。")
    
    env_ok = check_environment_variables()
    secret_ok = check_secret_file()
    
    print("--- デバッグモード終了 ---")
    
    if env_ok and secret_ok:
        print("\n結論: 全ての環境設定は、プログラムから正常に認識できています。")
        print("もしこれでも動作しない場合、他の原因（GitHub連携など）が考えられます。")
    else:
        print("\n結論: 上記の「❌」マークの部分が、プログラムが停止していた原因です。")
        print("Renderのダッシュボードで、該当する設定を再度丁寧にご確認ください。")

if __name__ == "__main__":
    main()
