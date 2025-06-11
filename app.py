import streamlit as st
from streamlit_option_menu import option_menu
import time
import datetime
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="StudyPress", page_icon="🍎", layout="centered")

# --- CSS読み込み ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('style.css')

# --- データ初期化 (本来はデータベース) ---
if "users" not in st.session_state:
    # デモ用に初期ユーザーを登録しておく
    st.session_state.users = {"test@test.com": {"password": "test", "name": "Test User", "icon": "👤"}}
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
# ユーザーごとのデータを管理するためのキーを準備
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# --- ユーザーデータアクセス関数 ---
# ログイン中のユーザーのデータを簡単に取得・設定するためのヘルパー
def get_user_data(key, default_value):
    email = st.session_state.logged_in_user
    if email not in st.session_state.user_data:
        st.session_state.user_data[email] = {}
    return st.session_state.user_data[email].get(key, default_value)

def set_user_data(key, value):
    email = st.session_state.logged_in_user
    if email not in st.session_state.user_data:
        st.session_state.user_data[email] = {}
    st.session_state.user_data[email][key] = value

# --- ログイン/登録ページ ---
def auth_page():
    st.title("🍎 StudyPress")
    st.write("あなたの学習を、スマートに、そして継続的に。")

    choice = st.radio("選択してください", ["ログイン", "新規登録"], horizontal=True, label_visibility="collapsed")

    if choice == "ログイン":
        with st.form("login_form"):
            email = st.text_input("メールアドレス")
            password = st.text_input("パスワード", type="password")
            submitted = st.form_submit_button("ログイン")
            if submitted:
                if email in st.session_state.users and st.session_state.users[email]['password'] == password:
                    with st.spinner("ログイン中..."):
                        time.sleep(1)
                    st.session_state.logged_in_user = email
                    st.rerun()
                else:
                    st.error("メールアドレスまたはパスワードが正しくありません。")

    elif choice == "新規登録":
        with st.form("signup_form"):
            name = st.text_input("ユーザー名")
            email = st.text_input("メールアドレス")
            password = st.text_input("パスワード", type="password")
            password_confirm = st.text_input("パスワード（確認用）", type="password")
            submitted = st.form_submit_button("登録する")
            if submitted:
                if not all([name, email, password, password_confirm]):
                    st.error("すべての項目を入力してください。")
                elif password != password_confirm:
                    st.error("パスワードが一致しません。")
                elif email in st.session_state.users:
                    st.error("このメールアドレスは既に使用されています。")
                else:
                    st.session_state.users[email] = {"password": password, "name": name, "icon": "👤"}
                    st.success("登録が完了しました！ログインしてください。")
                    st.info("※これはデモ実装です。実際のサービスではパスワードは安全にハッシュ化されます。")


# --- メインアプリケーション ---
def main_app():
    user_name = st.session_state.users[st.session_state.logged_in_user]['name']

    # データの初期化（ユーザーごと）
    if get_user_data("tasks", None) is None: set_user_data("tasks", [])
    if get_user_data("decks", None) is None: set_user_data("decks", [{"name": "数学 青チャート", "total_pages": 300}])
    if get_user_data("active_task", None) is None: set_user_data("active_task", None)
    if get_user_data("posts", None) is None: set_user_data("posts", [])

    # フッターナビゲーション
    selected_page = option_menu(
        menu_title=None,
        options=["ホーム", "計画", "記録", "分析", "SNS", "設定"],
        icons=['house-fill', 'calendar-check-fill', 'play-circle-fill', 'bar-chart-fill', 'people-fill', 'gear-fill'],
        default_index=0,
        orientation="horizontal",
    )
    
    # ページごとの表示（各関数は下に定義）
    if selected_page == "ホーム":
        page_home(user_name)
    elif selected_page == "計画":
        page_plan()
    elif selected_page == "記録":
        page_record()
    elif selected_page == "分析":
        page_analytics()
    elif selected_page == "SNS":
        page_sns()
    elif selected_page == "設定":
        page_settings()

def page_home(user_name):
    st.header(f"ようこそ、{user_name}さん")
    st.markdown("今日のタスクをこなして、目標に一歩近づこう。")

    # タイマー表示
    active_task = get_user_data("active_task", None)
    if active_task:
        task = active_task
        elapsed_time = time.time() - task['start_time']
        display_time = str(datetime.timedelta(seconds=int(elapsed_time)))
        
        st.markdown(f"""
        <div class="timer-box">
            <p><strong>{task['name']}</strong> ({task['deck_name']})</p>
            <h2>⏳ {display_time}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        concentration = st.slider("集中度 (1:低い ~ 10:高い)", 1, 10, 7)
        memo = st.text_area("学習メモ", placeholder="気づいたことや要点を記録...")
        
        if st.button("⏹️ 記録して終了", use_container_width=True, type="primary"):
            task['duration'] = time.time() - task['start_time']
            task['concentration'] = concentration
            task['memo'] = memo
            
            tasks = get_user_data("tasks", [])
            for i, t in enumerate(tasks):
                if t['id'] == task['id']:
                    tasks[i].update(task)
                    break
            set_user_data("tasks", tasks)
            
            posts = get_user_data("posts", [])
            post_text = f"{task['name']} を {int(task['duration']/60)}分 勉強しました！"
            posts.insert(0, {"user": user_name, "text": post_text, "time": datetime.datetime.now()})
            set_user_data("posts", posts)
            
            set_user_data("active_task", None)
            st.success("お疲れ様でした！学習を記録しました。")
            st.rerun()
    else:
        st.info("「記録」ページからタスクを選択して、学習を開始できます。")

    st.subheader("今日のTODOリスト")
    tasks = get_user_data("tasks", [])
    today_tasks = [t for t in tasks if t.get('due_date') == datetime.date.today().isoformat() and not t.get('completed')]
    if not today_tasks:
        st.write("今日のタスクはありません。「計画」ページでタスクを追加しましょう。")
    for task in today_tasks:
        st.checkbox(f"{task['name']} ({task['deck_name']})", key=f"today_task_{task['id']}")

def page_plan():
    st.header("計画管理")
    tab1, tab2, tab3 = st.tabs(["タスクリスト", "タスク追加", "デッキ管理"])
    tasks = get_user_data("tasks", [])
    decks = get_user_data("decks", [])

    with tab1:
        st.subheader("全てのタスク")
        if not tasks:
            st.info("タスクがありません。「タスク追加」タブから新しいタスクを作成してください。")
        else:
            for task in tasks:
                with st.container(border=True):
                    st.write(f"**{task['name']}**")
                    st.caption(f"Deck: {task['deck_name']} | 期限: {task.get('due_date', '未設定')}")
                    # ... (以下、計画ページのタスク表示ロジック)

    with tab2:
        st.subheader("新しいタスクを追加")
        with st.form("new_task_form"):
            task_name = st.text_input("タスク名")
            selected_deck = st.selectbox("デッキを選択", decks, format_func=lambda x: x['name'])
            due_date = st.date_input("期限日")
            # ... (以下、タスク追加ロジック)
            submitted = st.form_submit_button("タスクを追加")
            if submitted:
                # タスク追加処理
                pass

    with tab3:
        st.subheader("デッキ（参考書）の管理")
        # ... (以下、デッキ管理ロジック)
        
def page_record():
    st.header("学習を開始")
    active_task = get_user_data("active_task", None)
    tasks = get_user_data("tasks", [])
    
    if active_task:
        st.warning("現在、学習中のタスクがあります。「ホーム」画面でタスクを完了してください。")
    else:
        uncompleted_tasks = [t for t in tasks if not t.get('completed')]
        if not uncompleted_tasks:
            st.info("完了すべきタスクがありません。「計画」ページで新しいタスクを追加してください。")
        else:
            task_to_start = st.selectbox("開始するタスクを選択", uncompleted_tasks, format_func=lambda x: f"{x['name']} ({x['deck_name']})")
            
            if st.button("▶️ 学習を開始", use_container_width=True, type="primary"):
                active_task_data = {
                    "id": task_to_start['id'],
                    "name": task_to_start['name'],
                    "deck_name": task_to_start['deck_name'],
                    "start_time": time.time(),
                }
                set_user_data("active_task", active_task_data)
                st.rerun()

def page_analytics():
    st.header("学習分析")
    tasks = get_user_data("tasks", [])
    completed_tasks = [t for t in tasks if t.get('duration')]
    
    if not completed_tasks:
        st.info("分析できる学習記録がまだありません。タスクを完了してデータを蓄積しましょう。")
        return
    
    df = pd.DataFrame(completed_tasks)
    # ... (以下、分析ページのロジック)

def page_sns():
    st.header("タイムライン")
    # ... (SNSページのロジック)

def page_settings():
    st.header("設定")
    email = st.session_state.logged_in_user
    user_info = st.session_state.users[email]

    with st.expander("プロフィール設定", expanded=True):
        new_name = st.text_input("ユーザー名", user_info['name'])
        new_icon = st.selectbox("アイコン", ["👤", "👩‍🎓", "👨‍🎓", "🧑‍💻", "🦉", "🚀"], index=["👤", "👩‍🎓", "👨‍🎓", "🧑‍💻", "🦉", "🚀"].index(user_info['icon']))
        if st.button("更新する"):
            st.session_state.users[email]['name'] = new_name
            st.session_state.users[email]['icon'] = new_icon
            st.success("プロフィールを更新しました。")
    
    if st.button("ログアウト", type="secondary"):
        st.session_state.logged_in_user = None
        st.rerun()

# --- メインルーチン ---
if st.session_state.logged_in_user:
    main_app()
else:
    auth_page()
