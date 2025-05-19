# login.py

import streamlit as st
from supabase import create_client, Client
import os

# Supabase 初期化（再利用のため関数の外に置く）
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_ui():
    """
    Streamlitのログイン／新規登録 UI。
    ログイン済みの場合はユーザー情報（supabase.auth.user）を返す。
    未ログイン時はUIを表示してst.stop()。
    """
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
                st.success("ログイン成功！")
                st.rerun()
            except Exception as e:
                st.error(f"ログイン失敗: {e}")

        if st.button("新規登録（サインアップ）"):
            try:
                user = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.session_state["user"] = user
                st.success("登録完了！メールを確認してね📩")
                st.rerun()
            except Exception as e:
                st.error(f"登録失敗: {e}")

        st.stop()

    # ログイン済み
    user = st.session_state["user"]
    st.success(f"ようこそ！ログイン中です：{user.user.email}")
    st.write("ユーザーID（ログ保存に使えます）:", user.user.id)

    if st.button("ログアウト"):
        supabase.auth.sign_out()
        del st.session_state["user"]
        st.rerun()

    return user  # ユーザー情報を返す
