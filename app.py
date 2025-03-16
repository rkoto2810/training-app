import streamlit as st
import pyrebase

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
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("アカウント作成成功！ログインしてください。")
            except Exception as e:
                st.error(f"アカウント作成に失敗しました: {e}")

    if choice == "ログイン":
        if st.button("ログイン"):
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

# 🔹 一般ユーザー用マイページ（お気に入りフォルダ機能追加）
def my_page():
    st.title("マイページ（一般ユーザー用）")
    st.write(f"ようこそ！ {st.session_state['user_email']} さん")

    genre = st.selectbox("ジャンルを選択", ["スプリント", "ハードル", "投てき", "跳躍", "コンディショニング"])
    videos = db.child("videos").child(genre).get(st.session_state["id_token"])

    if videos.val():
        cols = st.columns(3)
        for idx, vid in enumerate(videos.each()):
            video_data = vid.val()
            with cols[idx % 3]:
                st.write(video_data["title"])
                st.video(video_data["url"])
                if st.button("お気に入り追加", key=f"fav_{vid.key()}"):
                    folder_name = st.selectbox("お気に入りフォルダを選択", get_folders() + ["新規作成"], key=f"folder_select_{vid.key()}")
                    if folder_name == "新規作成":
                        new_folder_name = st.text_input("新しいフォルダ名", key=f"new_folder_{vid.key()}")
                        if st.button("フォルダ作成", key=f"create_folder_{vid.key()}"):
                            folder_name = new_folder_name
                            db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").child(new_folder_name).push(video_data, st.session_state["id_token"])
                            st.success("フォルダとお気に入りを作成しました！")
                    elif st.button("お気に入り追加", key=f"add_{vid.key()}"):
                        db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").child(folder_name).push(video_data, st.session_state["id_token"])
                        st.success("お気に入りに追加しました！")

    # 📌 お気に入りフォルダ別一覧
    st.subheader("お気に入り動画一覧")
    user_fav = db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").get(st.session_state["id_token"]).val()

    if user_fav:
        for folder, vids in user_fav.items():
            st.write(f"📁 {folder}")
            cols = st.columns(3)
            for idx, (vid_key, video_data) in enumerate(user_fav[folder].items()):
                with cols[idx % 3]:
                    st.write(video_data["title"])
                    st.video(video_data["url"])
                    if st.button("削除", key=f"del_{vid.key()}"):
                        db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").child(folder_name).child(vid.key()).remove(st.session_state["id_token"])
                        st.success("お気に入りから削除しました！")
                        st.rerun()

# 🔹 管理者ページ（変更なし）

# フォルダ名取得用関数
def get_folder_names():
    folders = db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").shallow().get(st.session_state["id_token"]).val()
    return list(folders) if folders else []

# 🔹 画面遷移
if st.session_state["logged_in"]:
    admin_page() if st.session_state["is_admin"] else my_page()
else:
    login_page()
