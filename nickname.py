import streamlit as st
from supabase_helper import supabase

def get_or_ask_nickname(user_id: str):
    # Supabaseからニックネーム取得
    result = supabase.table("user_profiles").select("nickname").eq("user_id", user_id).execute()

    # 取得できたが空文字だった場合も再入力対象にする
    if result.data and result.data[0]["nickname"].strip():
        nickname = result.data[0]["nickname"]
        st.session_state["nickname"] = nickname
        return nickname

    # 登録されていない or 空だった場合：再入力
    nickname = st.text_input("ニックネームを入力してください（1回だけでOK）")

    if st.button("保存"):
        if nickname.strip() == "":
            st.warning("ニックネームを空欄にはできません")
            st.stop()
        else:
            # すでにレコードがあるなら update、なければ insert
            existing = supabase.table("user_profiles").select("id").eq("user_id", user_id).execute()
            if existing.data:
                supabase.table("user_profiles").update({"nickname": nickname}).eq("user_id", user_id).execute()
            else:
                supabase.table("user_profiles").insert({
                    "user_id": user_id,
                    "nickname": nickname
                }).execute()
            st.session_state["nickname"] = nickname
            st.success("ニックネームを保存しました！")
            st.rerun()

    st.stop()
