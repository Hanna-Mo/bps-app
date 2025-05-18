import json
import os
import datetime

# 通知を表示する関数（Mac専用）
def notify_mac(message):
    os.system(f'terminal-notifier -title "ポジティブ記録リマインダー" -message "{message}"')

# ログファイルの読み込み
LOG_FILE = "/Users/morimotohannna/Desktop/chatbot-app/logs.json"  

def load_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

# 今日書いてるか？
def has_written_today(logs):
    today = datetime.date.today().isoformat()
    return any(log.get("date") == today for log in logs)

# メイン処理
if __name__ == "__main__":
    logs = load_logs()
    if not has_written_today(logs):
        notify_mac("今日はまだ記録がありません。よかったら今、1日のポジティブなことを書いてみませんか？🌱")
