import streamlit as st
import os
import datetime
import random
import uuid
#from dotenv import load_dotenv
from openai import OpenAI
from supabase_helper import supabase

# -------------------- 初期設定 --------------------
st.set_page_config(page_title="ポジティブ習慣アプリ", page_icon="🌟")
#load_dotenv()
client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

# -------------------- ユーザー識別 --------------------
if "user_id" not in st.session_state:
    name = st.text_input("ニックネームを入力してください")
    if name:
        st.session_state["user_name"] = name
        st.session_state["user_id"] = str(uuid.uuid4())
        st.rerun()
    else:
        st.warning("ニックネームを入力してください。")
        st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state["user_name"]

# -------------------- GPT応答生成 --------------------
def get_gpt_reply(entry, goals):
    prompt = f"""
あなたはユーザーをあたたかく励ましたり褒めたりしてくれる優しいチャットボットです。
堅苦しくなく、やわらかい言葉で話してください。口調はフレンドリーですが丁寧にです・ます調でお願いします。絵文字を使っても構いません。
ポジティブな出来事を記録するアプリの一部として、ユーザーが今日書いたポジティブな出来事に対して、温かく励ますような言葉や活動に対する労いを自然な言葉で返してください。
ユーザーのニックネームは「{user_name}」です。
冒頭にユーザーの1日の活動に対する労いの言葉、または記録をしてくれたことへの感謝の言葉を入れてください。
以下はユーザーが今日書いたポジティブな出来事です：
「{entry}」
この出来事に対して、温かく励ますような言葉や労いを自然な文章で1〜2文で返してください。
また、ユーザーが設定している将来の目標はこちらです：
身体・心理面：{goals.get('body_mind')}
学業・仕事：{goals.get('career')}
人間関係：{goals.get('relationships')}
その他：{goals.get('others')}
出来事がユーザーの目標に関連していた時には、それに気づいてあげてください。
ただし、無理に出来事と目標の関連性を指摘する必要はありませんし、必ずしも目標について言及する必要はありません。
ユーザーは一日の疲労もあるので、目標についてはあまり触れず、ポジティブな出来事に対して温かく励ますような言葉を返してください。
"""

    response = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",  # openrouterはモデル名に `openai/` をつける
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
)
    return response.choices[0].message.content.strip()

# -------------------- Supabase連携（目標） --------------------
def load_goals_from_supabase(user_id):
    response = supabase.table("goals").select("*").eq("user_id", user_id).execute()
    if response.data:
        return response.data[0]
    else:
        return {"body_mind": "", "career": "", "relationships": "", "others": ""}

def save_goals_to_supabase(user_id, user_name, goals):
    data = {"user_id": user_id, "user_name": user_name, **goals}
    existing = supabase.table("goals").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("goals").update(data).eq("user_id", user_id).execute()
    else:
        supabase.table("goals").insert(data).execute()

# -------------------- Supabase連携（記録） --------------------
def save_log_to_supabase(user_id, user_name, date, entry):
    data = {"user_id": user_id, "user_name": user_name, "date": date, "entry": entry}
    supabase.table("logs").insert(data).execute()

def load_logs_from_supabase(user_id):
    response = supabase.table("logs").select("*").eq("user_id", user_id).order("date", desc=True).limit(5).execute()
    return response.data if response.data else []

# -------------------- 目標入力フォーム --------------------
st.title("🌟 ポジティブ習慣アプリ")
st.header("🎯 あなたの将来の最も理想的な姿について記入しましょう")
st.subheader("なるべく具体的に記入しましょう✨\nいくつでも構いません😊 いつでも変更してOKです👌")
goals = load_goals_from_supabase(user_id)

with st.form("goal_form"):
    st.subheader("1. 身体・心理面の理想")
    st.caption("例：週に1回は運動し、健康的な生活習慣を続けている。柔軟な考えを持ち、人に優しく接することができる。")
    goals["body_mind"] = st.text_area("", value=goals.get("body_mind", ""), key="body_mind", height=150)

    st.subheader("2. 学業・仕事の理想")
    st.caption("例：統計学をマスターし、どんな解析でも自信を持ってできるようになっている。丁寧で正確に仕事をこなし、周囲から頼られる先輩である。")
    goals["career"] = st.text_area("", value=goals.get("career", ""), key="career", height=150)

    st.subheader("3. 人間関係の理想")
    st.caption("例：信頼できるパートナーと暮らし、両親ともたまに会って良好な関係を築いている。何らかのコミュニティに参加し、常に新しい人との出会いがある。")
    goals["relationships"] = st.text_area("", value=goals.get("relationships", ""), key="relationships", height=150)

    st.subheader("4. その他の理想")
    st.caption("例：趣味のバンド活動を続け、たまにライブを開催している。料理が上手で、家族に美味しいご飯を作っている。")
    goals["others"] = st.text_area("", value=goals.get("others", ""), key="others",height=150)

    if st.form_submit_button("目標を保存する"):
        save_goals_to_supabase(user_id, user_name, goals)
        st.success("✅ 目標を保存しました！")

# -------------------- ポジティブな出来事記録 --------------------
st.header("📖 今日のポジティブな出来事")
today = datetime.date.today().isoformat()

with st.form("log_form"):
    st.subheader("今日嬉しかったこと、できたこと、達成したことなどを自由に書いてください✨")
    st.caption("例：朝余裕をもって出勤でき、清々しい気持ちがした。友達に偶然出会い、ご飯に行く約束をした。")
    entry = st.text_area("", height=150)
    submitted = st.form_submit_button("記録する")

    if submitted and entry:
        save_log_to_supabase(user_id, user_name, today, entry)
        gpt_reply = get_gpt_reply(entry, goals)
        st.markdown(f"> {gpt_reply}")
        st.success("✅ 記録を保存しました！")

# --- 3. 目標の表示（読み取り専用） ---
st.subheader("📌 現在の目標")
st.markdown(f"**1. 身体・心理面：** {goals.get('body_mind', '') or '（未入力）'}")
st.markdown(f"**2. 学業・仕事：** {goals.get('career', '') or '（未入力）'}")
st.markdown(f"**3. 人間関係：** {goals.get('relationships', '') or '（未入力）'}")
st.markdown(f"**4. その他の面：** {goals.get('others', '') or '（未入力）'}")

# -------------------- 過去の記録表示 --------------------
st.header("📚 過去の記録（最新5件）")
logs = load_logs_from_supabase(user_id)
if logs:
    for log in logs:
        st.markdown(f"📅 **{log['date']}**")
        st.markdown(f"> {log['entry']}")
else:
    st.info("まだ記録がありません。今日からはじめてみましょう！")
