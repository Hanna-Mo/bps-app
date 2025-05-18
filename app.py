import streamlit as st
import json
import os
import datetime
import random
from openai import OpenAI


client = OpenAI(api_key="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")

def get_gpt_reply(entry, goals):
    # 呼びかけリスト
    greetings = [
        "今日も話してくれてありがとう！",
        "今日も記録できたこと、素晴らしいです！",
        "今日もお疲れ様です😊"
    ]

    # 絵文字リスト
    emojis = ["🌸", "🏃", "☀️", "✨", "📘", "🌈", "😊","😳"]

    # ランダム選択
    greeting = random.choice(greetings)
    emoji = random.choice(emojis)

def get_gpt_reply(entry, goals):
    prompt = f"""
あなたはユーザーをあたたかく励ましたり褒めたりしてくれる優しいチャットボットです。
堅苦しくなく、やわらかい言葉で話してください。口調はフレンドリーですが丁寧にです・ます調でお願いします。絵文字を使っても構いません。
ポジティブな出来事を記録するアプリの一部として、ユーザーが今日書いたポジティブな出来事に対して、温かく励ますような言葉や活動に対する労いを返してください。
以下はユーザーが今日書いたポジティブな出来事です：

「{entry}」

また、ユーザーが設定している将来の目標はこちらです：
身体・心理面：{goals.get('body_mind')}
学業・仕事：{goals.get('career')}
人間関係：{goals.get('relationships')}
その他：{goals.get('others')}

この出来事に対して、温かく励ますような言葉や労いを自然な文章で1〜2文で返してください。
また、出来事がユーザーの目標に関連していた時には、それに気づいてあげてください。
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# ---------- ファイルパス ----------
GOAL_FILE = "goals.json"
LOG_FILE = "logs.json"

# ---------- 初期化 ----------
default_goals = {
    "body_mind": "",
    "career": "",
    "relationships": "",
    "others": ""
}

if not os.path.exists(GOAL_FILE):
    with open(GOAL_FILE, "w") as f:
        json.dump(default_goals, f)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

# ---------- データ操作 ----------
def load_goals():
    with open(GOAL_FILE, "r") as f:
        return json.load(f)

def save_goals(goals):
    with open(GOAL_FILE, "w") as f:
        json.dump(goals, f, indent=2)

def load_logs():
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

# ---------- Streamlit アプリ ----------
st.set_page_config(page_title="ポジティブ習慣アプリ", page_icon="🌟")

st.title("🌟 ポジティブ習慣アプリ")

# --- 1. 将来の目標入力フォーム ---
st.header("🎯 あなたの将来の最も理想的な姿について記入しましょう")
st.subheader("なるべく具体的に記入してみましょう✨\nいくつでも構いません😊 いつでも変更してOKです👌")

goals = load_goals()

with st.form("goal_form"):
    st.subheader("1. 身体・心理面での理想")
    st.caption("例：週に1回は運動し、健康的な生活習慣を続けている。柔軟な考えを持ち、人に優しく接することができる。")
    goals["body_mind"] = st.text_area("", value=goals.get("body_mind", ""), key="goal_body_mind", height=150)

    st.subheader("2. 学業・仕事面での理想")
    st.caption("例：統計学をマスターし、どんな解析でも自信を持ってできるようになっている。丁寧で正確に仕事をこなし、周囲から頼られる先輩である。")
    goals["career"] = st.text_area("", value=goals.get("career", ""), key="goal_career",height=150)

    st.subheader("3. 人間関係の理想")
    st.caption("例：信頼できるパートナーと暮らし、両親ともたまに会って良好な関係を築いている。何らかのコミュニティに参加し、常に新しい人との出会いがある。")
    goals["relationships"] = st.text_area("", value=goals.get("relationships", ""), key="goal_relationships", height=150)

    st.subheader("4. その他の面での理想")
    st.caption("例：趣味のバンド活動を続け、たまにライブを開催している。料理が上手で、家族に美味しいご飯を作っている。")
    goals["others"] = st.text_area("", value=goals.get("others", ""), key="goal_others", height=150)

    if st.form_submit_button("目標を保存する"):
        save_goals(goals)
        st.success("✅ 目標を保存しました！")


# --- 2. 今日のポジティブな出来事を記録 ---
st.header("📖 今日のポジティブな出来事")

today = datetime.date.today().isoformat()
logs = load_logs()

with st.form("log_form"):
    entry = st.text_area("今日嬉しかったこと、できたこと、達成したことなどを自由に書いてください✨", height=150)
    st.caption("例：朝余裕をもって出勤でき、清々しい気持ちがした。友達に偶然出会い、ご飯に行く約束をした。")
    if st.form_submit_button("記録する"):
        new_log = {"date": today, "entry": entry}
        logs.append(new_log)
        save_logs(logs)
        st.success("✅ 記録を保存しました！")
        gpt_reply = get_gpt_reply(entry, goals)
        st.markdown(f"> {gpt_reply}")



# --- 3. 目標の表示（読み取り専用） ---
st.subheader("📌 現在の目標")
st.markdown(f"**1. 身体・心理面：** {goals.get('body_mind', '') or '（未入力）'}")
st.markdown(f"**2. 学業・仕事：** {goals.get('career', '') or '（未入力）'}")
st.markdown(f"**3. 人間関係：** {goals.get('relationships', '') or '（未入力）'}")
st.markdown(f"**4. その他の面：** {goals.get('others', '') or '（未入力）'}")

# --- 4. 最近の記録一覧 ---
st.header("📚 過去の記録（最新5件）")

if logs:
    for log in reversed(logs[-5:]):
        st.markdown(f"📅 **{log['date']}**")
        st.markdown(f"> {log['entry']}")
else:
    st.info("まだ記録がありません。今日からはじめてみましょう！")
