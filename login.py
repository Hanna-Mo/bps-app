# login.py
import streamlit as st
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_ui():
    # ✅ セッション復元
    if "user" not in st.session_state and "session" in st.session_state:
        try:
            supabase.auth.set_session(
                st.session_state["session"]["access_token"],
                st.session_state["session"]["refresh_token"]
            )
            user = supabase.auth.get_user()
            st.session_state["user"] = user
            st.rerun()
        except Exception as e:
            st.warning("セッション復元失敗。ログインし直してください。")

    # 🔓 すでにログイン済み
    if "user" in st.session_state:
        user = st.session_state["user"]
        st.write(f"👋 ログイン中：{user.user.email}")
        if st.button("ログアウト"):
            supabase.auth.sign_out()
            for k in ["user", "session"]:
                st.session_state.pop(k, None)
            st.rerun()
        return user

    # 🔐 未ログイン：ログインフォームと登録フォームを分ける
    st.title("🔐 ログインまたは新規登録")

    tab_login, tab_signup = st.tabs(["ログイン", "新規登録"])

    with tab_login:
        email = st.text_input("メールアドレス（ログイン用）", key="login_email")
        password = st.text_input("パスワード", type="password", key="login_pass")
        if st.button("ログイン"):
            try:
                user = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state["user"] = user
                st.session_state["session"] = user.session
                st.success("ログイン成功！")
                st.rerun()
            except Exception as e:
                st.error(f"ログイン失敗: {e}")

    with tab_signup:
        email = st.text_input("メールアドレス（登録用）", key="signup_email")
        password = st.text_input("パスワード（6文字以上）", type="password", key="signup_pass")
        if st.button("新規登録（サインアップ）"):
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("登録したアドレスにメールを送信しました📩\nconfirm your emailを押して登録を完了させてください✨\nその後、ログインすることができます😊👌 ")
            except Exception as e:
                st.error(f"登録失敗: {e}")

    st.stop()
