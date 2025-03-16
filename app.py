import streamlit as st
import pyrebase  # <- 修正（pyrebase4ではなくpyrebaseを指定）

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
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "id_token" not in st.session_state:
    st.session_state["id_token"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# 🔹 管理者設定
ADMIN_EMAILS = ["rkoto2810@gmail.com"]

# 🔹 ログインページ
def login_page():
    st.title("トレーニング動画アプリ - ログイン")

    choice = st.radio("ログインまたは登録", ["ログイン", "新規登録"])

    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")

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
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["id_token"] = user["idToken"]
                st.session_state["is_admin"] = user["email"] in ADMIN_EMAILS
                st.rerun()
            except Exception as e:
                st.error(f"ログインに失敗しました: {e}")

# 🔹 一般ユーザー用マイページ
def my_page():
    st.title("マイページ（一般ユーザー用）")
    st.write(f"ようこそ！ {st.session_state['user_email']} さん")

    # ジャンル別動画表示
    st.subheader("トレーニング動画を検索")
    genre = st.selectbox("ジャンルを選択", ["スプリント", "ハードル", "投てき", "跳躍", "コンディショニング"])

    videos = db.child("videos").child(genre).get(st.session_state["id_token"])
    if videos.val():
        cols = st.columns(3)
        for idx, vid in enumerate(videos.each()):
            video_data = vid.val()
            with cols[idx % 3]:
                st.write(video_data.get("title", "タイトルなし"))
                st.video(video_data["url"])
                if st.button("お気に入り追加", key=f"fav_{vid.key()}"):
                    db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").push(video_data, st.session_state["id_token"])
                    st.success("お気に入りに追加しました！")

    # お気に入り一覧（3列）
    st.subheader("お気に入り動画一覧")
    favorites = db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").get(st.session_state["id_token"])
    if favorites.val():
        cols = st.columns(3)
        for idx, fav in enumerate(favorites.each()):
            video_data = fav.val()
            with cols[idx % 3]:
                st.write(video_data.get("title", "No Title"))
                st.video(video_data["url"])
                if st.button("削除", key=f"del_fav_{fav.key()}"):
                    db.child("users").child(st.session_state["user_email"].replace(".", "_")).child("favorites").child(fav.key()).remove(st.session_state["id_token"])
                    st.success("お気に入りから削除しました！")
                    st.rerun()

# 🔹 管理者画面
def admin_page():
    st.title("管理者画面")
    genre = st.selectbox("ジャンルを選択", ["スプリント", "ハードル", "投てき", "跳躍", "コンディショニング"])

    video_title = st.text_input("動画タイトル")
    youtube_url = st.text_input("動画URL")

    if st.button("追加"):
        db.child("videos").child(genre).push({"title": video_title, "url": youtube_url}, st.session_state["id_token"])
        st.success("動画を追加しました！")
        st.rerun()

    # 動画一覧
    videos = db.child("videos").child(genre).get(st.session_state["id_token"])
    if videos.val():
        cols = st.columns(3)
        for idx, vid in enumerate(videos.each()):
            video_data = vid.val()
            with cols[idx % 3]:
                st.write(video_data.get("title", "No Title"))
                st.video(video_data["url"])
                if st.button("削除", key=f"del_{vid.key()}"):
                    db.child("videos").child(genre).child(vid.key()).remove(st.session_state["id_token"])
                    st.success("動画を削除しました！")
                    st.rerun()

    if st.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

# 🔹 画面遷移
if st.session_state["logged_in"]:
    admin_page() if st.session_state["is_admin"] else my_page()
else:
    login_page()
