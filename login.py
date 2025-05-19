# login.py
import streamlit as st
from supabase import create_client
import os

# Supabase 初期化
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_ui():
    # ✅ セッション復元（自動ログイン）
    if "user" not in st.session_state and "session" in st.session_state:
        try:
            supabase.auth.set_session(
                st.session_state["session"]["access_token"],
                st.session_state["session"]["refresh_token"]
            )
            user = supabase.auth.get_user()
            st.session_state["user"] = user
            st.success("🔄 セッションから自動ログインしました！")
            st.rerun()
        except Exception as e:
            st.warning("セッション復元に失敗しました…ログインしてください")

    # 🔐 未ログインならログイン／サインアップフォーム表示
    if "user" not in st.session_state:
        st.title("🔐 ログインまたは新規登録")

        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")

        if st.button("ログイン"):
            try:
                user = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state["user"] = user
                st.session_state["session"] = user.session  # ✅ セッション保存！
                st.success("ログイン成功！")
                st.rerun()
            except Exception as e:
                st.error(f"ログイン失敗: {e}")

        if st.button("新規登録（サインアップ）"):
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("登録完了！ログインしてください📩")
                st.stop()
            except Exception as e:
                st.error(f"登録失敗: {e}")

        st.stop()

    # 🔓 ログイン済みならユーザー情報を返す
    user = st.session_state["user"]
    st.write(f"👋 ログイン中：{user.user.email}")
    if st.button("ログアウト"):
        supabase.auth.sign_out()
        for key in ["user", "session"]:
            st.session_state.pop(key, None)
        st.rerun()

    return user
