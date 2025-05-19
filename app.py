import streamlit as st
import os
import datetime
import random
import uuid
#from dotenv import load_dotenv
from openai import OpenAI
from supabase_helper import supabase
from login import login_ui

# -------------------- 初期設定 --------------------
st.set_page_config(page_title="ポジティブ習慣アプリ", page_icon="🌟")
#load_dotenv()
client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
st.write("🔑 APIキー確認:", os.getenv("OPENROUTER_API_KEY")[:10] + "..." if os.getenv("OPENROUTER_API_KEY") else "❌ None!!")


# ログインUIを表示し、ユーザー情報を取得
user = login_ui()

# Supabase上の一意のユーザーID
user_id = user.user.id
user_email = user.user.email

# -------------------- ユーザー識別 --------------------
#if "user_id" not in st.session_state:
 #   name = st.text_input("ニックネームを入力してください")
  #  if name:
   #     st.session_state["user_name"] = name
    #    st.session_state["user_id"] = str(uuid.uuid4())
     #   st.rerun()
#    else:
 #       st.warning("ニックネームを入力してください。")
  #      st.stop()

#user_id = st.session_state["user_id"]
#user_name = st.session_state["user_name"]

# -------------------- GPT応答生成 --------------------
def get_gpt_reply(entry, goals):
    prompt = f"""
あなたはユーザーをあたたかく励ましたり褒めたりしてくれる前向きで優しいチャットボットです。
堅苦しくなく、やわらかい言葉で話してください。口調はフレンドリーですが丁寧にです・ます調でお願いします。絵文字や！なども使ってください。
一日の出来事を記録するアプリの一部として、ユーザーが今日書いた出来事に対して、活動に対する褒めや労い、ポジティブなフィードバックを自然な言葉で返してください。
ただし直接的な褒め言葉は避け、ユーザーの行動や出来事に対して共感を示しながら自然に褒めてください。
もしもユーザーが落ち込んでいるような内容を書いていた場合には、無理に励まさず、共感を示しつつ、一日を過ごしたことに対して褒めてあげてください。
挨拶として冒頭にユーザーが記録をしてくれたことへの感謝の言葉を敬語で入れてください。
例えば、「今日も記録してくれてありがとうございます！😊」が挙げられます。
以下はユーザーが今日書いた出来事です：
「{entry}」
また、もしも出来事がユーザーの目標に関連していた時には、それに自然に気づいてあげてください。
ただし、無理に出来事と目標の関連性を指摘する必要はありませんし、必ずしも目標について言及する必要はありません。
ユーザーが設定している将来の目標はこちらです：
身体・心理面：{goals.get('body_mind')}
学業・仕事：{goals.get('career')}
人間関係：{goals.get('relationships')}
その他：{goals.get('others')}
将来の目標に関連する内容がもしあれば、さりげなく触れてあげてください。関連がなければ、無理に目標について言及する必要はないです。
将来の目標に関連する内容がなければ、ユーザーが今日書いた出来事に対するフィードバックだけしてください。
全体があまり長くならないように、200文字程度に収めてください。
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

def save_goals_to_supabase(user_id, goals):
    data = {"user_id": user_id, **goals}
    existing = supabase.table("goals").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("goals").update(data).eq("user_id", user_id).execute()
    else:
        supabase.table("goals").insert(data).execute()

# -------------------- Supabase連携（記録） --------------------
def save_log_to_supabase(user_id, date, entry):
    data = {"user_id": user_id, "date": date, "entry": entry}
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
        save_goals_to_supabase(user_id, goals)
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
        save_log_to_supabase(user_id, today, entry)
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
