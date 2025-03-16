import streamlit as st
import pyrebase
from datetime import datetime

# 🔥 Firebaseの設定
firebase_config = {
    "apiKey": "AIzaSyBaUiz3YobYBzSPA7BdOc7k_Ko3QvckK10",
    "authDomain": "training-app-44260.firebaseapp.com",
    "databaseURL": "https://training-app-44260-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "training-app-44260",
    "storageBucket": "training-app-44260.appspot.com",
    "messagingSenderId": "58405608544",
    "appId": "1:58405608544:web:eeb933c646c798a6873705",
    "measurementId": "G-7MQ5WVC8Z2"
}

# Firebaseを初期化
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

# 🔹 セッション状態を管理
for key in ["logged_in", "user_email", "id_token", "is_admin"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "user_email" else ""

# 🔹 管理者設定
ADMIN_EMAILS = ["rkoto2810@gmail.com"]

# 🔹 ログインページ
def login_page():
    st.title("トレーニング動画アプリ - ログイン")
    choice = st.radio("ログインまたは登録", ["ログイン", "新規登録"])

    email = st.text_input("メールアドレス", autocomplete="email")
    password = st.text_input("パスワード", type="password", autocomplete="current-password")

    if choice == "新規登録":
        if st.button("アカウント作成"):
            if not email or not password:
                st.error("メールアドレスとパスワードを入力してください")
            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("アカウント作成成功！ログインしてください。")
                except Exception as e:
                    st.error(f"アカウント作成に失敗しました: {e}")

    if choice == "ログイン":
        if st.button("ログイン"):
            if not email or not password:
                st.error("メールアドレスとパスワードを入力してください")
            else:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state.update({
                        "logged_in": True,
                        "user_email": user["email"],
                        "id_token": user["idToken"],
                        "is_admin": user["email"] in ADMIN_EMAILS
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"ログインに失敗しました: {e}")

# 🔹 画面遷移
if st.session_state["logged_in"]:
    admin_page() if st.session_state["is_admin"] else my_page()
else:
    login_page()
