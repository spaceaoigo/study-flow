import streamlit as st
from streamlit_option_menu import option_menu
import time
import datetime
import pandas as pd

# --- ページ設定と基本設計 ---
st.set_page_config(page_title="StudyPress", page_icon="🍎", layout="centered")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('style.css')

# --- データ初期化 (B-1, B-4, B-5, C-1, C-2 etc.) ---
# 本来はデータベースで管理するが、Streamlitのデモとしてsession_stateを使用
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest User"
if "user_icon" not in st.session_state:
    st.session_state.user_icon = "👤"
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "decks" not in st.session_state:
    st.session_state.decks = [{"name": "数学 青チャート", "total_pages": 300}, {"name": "システム英単語", "total_pages": 400}]
if "active_task" not in st.session_state:
    st.session_state.active_task = None
if "posts" not in st.session_state:
    st.session_state.posts = []
if "followers" not in st.session_state:
    st.session_state.followers = 120
if "following" not in st.session_state:
    st.session_state.following = 85

# --- ログイン画面 (B-1) ---
def login_page():
    st.title("🍎 StudyPress")
    st.subheader("Welcome Back")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            # ダミーのログイン処理
            if email and password:
                with st.spinner("Logging in..."): # A-8
                    time.sleep(1)
                st.session_state.logged_in = True
                st.session_state.user_name = email.split('@')[0].capitalize()
                st.rerun()
            else:
                st.error("Please enter both email and password.") # A-14

# --- メインアプリケーション ---
def main_app():
    # --- モバイルフレンドリーなフッターナビゲーション (A-5) ---
    selected_page = option_menu(
        menu_title=None,
        options=["ホーム", "計画", "記録", "分析", "SNS", "設定"],
        icons=['house-fill', 'calendar-check-fill', 'play-circle-fill', 'bar-chart-fill', 'people-fill', 'gear-fill'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff", "border-radius": "12px", "box-shadow": "0 4px 12px rgba(0,0,0,0.05)"},
            "icon": {"color": "#6e6e73", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#f5f5f7"},
            "nav-link-selected": {"background-color": "#0071e3", "color": "white", "font-weight": "600"},
        }
    )

    # --- ページごとの表示 ---
    if selected_page == "ホーム":
        page_home()
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

def page_home():
    st.header(f"Welcome, {st.session_state.user_name}!")
    st.markdown("今日のタスクをこなして、目標に一歩近づこう。")

    # --- タイマー表示 (D-1, D-7, D-8) ---
    if st.session_state.active_task:
        task = st.session_state.active_task
        elapsed_time = time.time() - task['start_time']
        display_time = str(datetime.timedelta(seconds=int(elapsed_time)))
        
        with st.container():
            st.markdown(f"""
            <div class="timer-box">
                <p><strong>{task['name']}</strong> ({task['deck_name']})</p>
                <h2>⏳ {display_time}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            concentration = st.slider("集中度 (1:低い ~ 10:高い)", 1, 10, 7, key="active_concentration") # D-5
            memo = st.text_area("学習メモ", key="active_memo", placeholder="気づいたことや要点を記録...") # D-6
            
            if st.button("⏹️ 記録して終了", use_container_width=True, type="primary"):
                task['end_time'] = time.time()
                task['duration'] = task['end_time'] - task['start_time']
                task['concentration'] = concentration
                task['memo'] = memo
                
                # タスクリストを更新
                for t in st.session_state.tasks:
                    if t['id'] == task['id']:
                        t.update(task)
                        break
                
                # タイムラインに投稿 (F-1, F-6)
                post_text = f"{task['name']} を {int(task['duration']/60)}分 勉強しました！"
                st.session_state.posts.insert(0, {"user": st.session_state.user_name, "icon": st.session_state.user_icon, "text": post_text, "time": datetime.datetime.now(), "likes": 0, "comments": []})
                
                st.session_state.active_task = None
                st.success("お疲れ様でした！学習を記録しました。") # A-9
                st.rerun()
    else:
        st.info("「記録」ページからタスクを選択して、学習を開始できます。")

    st.subheader("今日のTODOリスト")
    today_tasks = [t for t in st.session_state.tasks if t.get('due_date') == datetime.date.today().isoformat() and not t.get('completed')]
    if not today_tasks:
        st.write("今日のタスクはありません。「計画」ページでタスクを追加しましょう。")
    for task in today_tasks:
        st.checkbox(f"{task['name']} ({task['deck_name']})", key=f"today_task_{task['id']}")


def page_plan():
    st.header("計画管理")
    
    tab1, tab2, tab3 = st.tabs(["タスクリスト", "タスク追加", "デッキ管理"])

    with tab1: # C-3, C-4, C-7
        st.subheader("全てのタスク")
        if not st.session_state.tasks:
            st.info("タスクがありません。「タスク追加」タブから新しいタスクを作成してください。")
        else:
            for task in st.session_state.tasks:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{task['name']}**")
                        st.caption(f"Deck: {task['deck_name']} | 期限: {task.get('due_date', '未設定')}")
                        progress = task.get('progress', 0)
                        st.progress(progress, text=f"進捗: {progress}%")
                    with col2:
                        # C-8 タスクのアーカイブ（完了）
                        if st.button("完了", key=f"complete_{task['id']}", use_container_width=True):
                            task['completed'] = True
                            st.rerun()
                        # C-15 タスク削除
                        if st.button("🗑️", key=f"del_plan_{task['id']}", use_container_width=True):
                            st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                            st.rerun()
                        

    with tab2: # C-5, C-11
        st.subheader("新しいタスクを追加")
        with st.form("new_task_form"):
            task_name = st.text_input("タスク名", placeholder="例: Chapter 3 演習問題")
            selected_deck_dict = st.selectbox("デッキを選択", st.session_state.decks, format_func=lambda x: x['name'])
            due_date = st.date_input("期限日") # C-5
            
            # C-11: 達成度の数値化
            st.write(f"**進捗管理（{selected_deck_dict['name']}）**")
            start_page = st.number_input("開始ページ", 1, selected_deck_dict['total_pages'], 1)
            end_page = st.number_input("終了ページ", start_page, selected_deck_dict['total_pages'], start_page + 10)
            
            submitted = st.form_submit_button("タスクを追加")
            if submitted:
                if task_name and selected_deck_dict:
                    new_task = {
                        "id": time.time(),
                        "name": task_name,
                        "deck_name": selected_deck_dict['name'],
                        "due_date": due_date.isoformat(),
                        "start_page": start_page,
                        "end_page": end_page,
                        "current_page": start_page,
                        "progress": 0, # 初期進捗
                        "completed": False
                    }
                    st.session_state.tasks.append(new_task)
                    st.success(f"タスク「{task_name}」を追加しました。")
                else:
                    st.error("タスク名とデッキを選択してください。")
    
    with tab3:
        st.subheader("デッキ（参考書）の管理")
        for deck in st.session_state.decks:
            st.write(f"- {deck['name']} (全{deck['total_pages']}ページ)")
        with st.form("new_deck_form"):
            deck_name = st.text_input("新しいデッキ名")
            total_pages = st.number_input("総ページ数", min_value=1, value=100)
            if st.form_submit_button("デッキを追加"):
                st.session_state.decks.append({"name": deck_name, "total_pages": total_pages})
                st.rerun()

def page_record():
    st.header("学習を開始")
    
    if st.session_state.active_task:
        st.warning("現在、学習中のタスクがあります。「ホーム」画面でタスクを完了してください。")
    else:
        uncompleted_tasks = [t for t in st.session_state.tasks if not t.get('completed')]
        if not uncompleted_tasks:
            st.info("完了すべきタスクがありません。「計画」ページで新しいタスクを追加してください。")
        else:
            task_to_start = st.selectbox("開始するタスクを選択", uncompleted_tasks, format_func=lambda x: f"{x['name']} ({x['deck_name']})")
            
            # ポモドーロタイマー設定 (D-1)
            is_pomo = st.toggle("ポモドーロタイマーを使う")
            if is_pomo:
                pomo_duration = st.slider("集中時間 (分)", 5, 60, 25)
            
            if st.button("▶️ 学習を開始", use_container_width=True, type="primary"):
                st.session_state.active_task = {
                    "id": task_to_start['id'],
                    "name": task_to_start['name'],
                    "deck_name": task_to_start['deck_name'],
                    "start_time": time.time(),
                    "is_pomo": is_pomo,
                    "pomo_duration": pomo_duration * 60 if is_pomo else None
                }
                st.rerun()

def page_analytics(): # E-1, E-2, E-3, E-4, E-5
    st.header("学習分析")

    if not any(t.get('duration') for t in st.session_state.tasks):
        st.info("分析できる学習記録がまだありません。タスクを完了してデータを蓄積しましょう。")
        return

    df = pd.DataFrame([t for t in st.session_state.tasks if t.get('duration')])
    df['date'] = pd.to_datetime(df['start_time'], unit='s').dt.date

    # E-5, E-6
    col1, col2, col3 = st.columns(3)
    total_time_sec = df['duration'].sum()
    total_time_str = str(datetime.timedelta(seconds=int(total_time_sec)))
    col1.metric("総学習時間", total_time_str)
    
    avg_concentration = df['concentration'].mean() # E-4
    col2.metric("平均集中度", f"{avg_concentration:.1f} / 10")
    
    completed_tasks = len([t for t in st.session_state.tasks if t.get('completed')])
    col3.metric("完了タスク数", f"{completed_tasks} 件")
    
    st.markdown("---")
    
    # E-2 日別学習時間
    st.subheader("日別学習時間 (分)")
    daily_study = df.groupby('date')['duration'].sum() / 60
    st.bar_chart(daily_study)
    
    # E-3 科目別学習バランス
    st.subheader("科目（デッキ）別学習バランス")
    deck_study = df.groupby('deck_name')['duration'].sum() / 3600
    st.bar_chart(deck_study.rename("学習時間 (h)"))
    
    # E-1 学習ヒートマップ (簡易版)
    st.subheader("学習カレンダー")
    st.write("学習した日に色が付きます。（本格的なヒートマップはライブラリ追加で実装可）")
    study_dates = df['date'].unique()
    st.date_input("学習日", value=list(study_dates), disabled=True)


def page_sns(): # F-1, F-2, F-3, F-4
    st.header("タイムライン")

    # F-1, F-6
    with st.form("new_post_form"):
        post_content = st.text_area("今なにしてる？", placeholder="今日の目標や進捗をシェアしよう")
        if st.form_submit_button("投稿する", use_container_width=True, type="primary"):
            if post_content:
                st.session_state.posts.insert(0, {"user": st.session_state.user_name, "icon": st.session_state.user_icon, "text": post_content, "time": datetime.datetime.now(), "likes": 0, "comments": []})
                st.success("投稿しました！")

    st.markdown("---")

    for i, post in enumerate(st.session_state.posts):
        with st.container(border=True):
            col1, col2 = st.columns([1, 8])
            with col1:
                st.write(post['icon'])
            with col2:
                st.write(f"**{post['user']}** · <small>{post['time'].strftime('%Y-%m-%d %H:%M')}</small>", unsafe_allow_html=True)
                st.write(post['text'])
                
                # F-2, F-3
                btn_col1, btn_col2, _ = st.columns([1, 1, 4])
                if btn_col1.button(f"👍 {post['likes']}", key=f"like_{i}"):
                    post['likes'] += 1
                    st.rerun()
                if btn_col2.button("💬", key=f"comment_{i}"):
                    st.text_input("コメント", key=f"comment_text_{i}", on_change=lambda: post['comments'].append(st.session_state[f"comment_text_{i}"]))
                for comment in post['comments']:
                    st.write(f"└ {comment}")

def page_settings(): # A-12, B-8, B-9
    st.header("設定")
    
    with st.expander("プロフィール設定", expanded=True):
        st.session_state.user_name = st.text_input("ユーザー名", st.session_state.user_name)
        st.session_state.user_icon = st.selectbox("アイコン", ["👤", "👩‍🎓", "👨‍🎓", "🧑‍💻", "🦉", "🚀"])
    
    with st.expander("アカウント", expanded=True):
        # B-8 プライバシー設定 (ダミー)
        st.selectbox("プロフィールの公開範囲", ["全体に公開", "フォロワーのみ", "非公開"])
        # B-9 アカウント削除 (ダミー)
        if st.button("アカウントを削除する", type="secondary"):
            st.error("この操作は元に戻せません。本当に削除しますか？")
    
    if st.button("ログアウト"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --- メインルーチン ---
if st.session_state.logged_in:
    main_app()
else:
    login_page()
