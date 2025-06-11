import streamlit as st
import time
import datetime

# --- 初期設定 ---
st.set_page_config(
    page_title="StudyFlow",
    page_icon="📚",
    layout="wide"
)

# --- CSS読み込み ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"'{file_name}' が見つかりません。GitHubにアップロードされているか確認してください。")

local_css("style.css")

# --- セッションデータの初期化 ---
if 'long_term_goal' not in st.session_state:
    st.session_state.long_term_goal = ""
if 'short_term_goal' not in st.session_state:
    st.session_state.short_term_goal = ""
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'decks' not in st.session_state:
    st.session_state.decks = ["数学 青チャート", "英文解釈の技術100", "システム英単語"]
if 'active_task_id' not in st.session_state:
    st.session_state.active_task_id = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

# --- サイドバー (入力系) ---
with st.sidebar:
    st.header("🎯 目標設定")
    st.session_state.long_term_goal = st.text_input("長期目標 (例: 〇〇大学合格)", st.session_state.long_term_goal)
    st.session_state.short_term_goal = st.text_input("短期目標 (例: 今月中に基礎問題集を完走)", st.session_state.short_term_goal)
    
    st.markdown("---")
    
    st.header("📖 デッキとタスク")
    
    st.subheader("デッキの管理")
    new_deck = st.text_input("新しい参考書・デッキ名を追加")
    if st.button("デッキを追加"):
        if new_deck and new_deck not in st.session_state.decks:
            st.session_state.decks.append(new_deck)
            st.success(f"「{new_deck}」を追加しました。")
        else:
            st.warning("入力が空か、既に追加されています。")

    st.subheader("タスクの追加")
    selected_deck = st.selectbox("デッキを選択", st.session_state.decks)
    new_task_name = st.text_input("新しいタスク名（例: p.10-15）")

    if st.button("タスクを追加"):
        if new_task_name:
            new_task = {
                'id': time.time(),
                'deck': selected_deck,
                'name': new_task_name,
                'total_time': 0,
            }
            st.session_state.tasks.append(new_task)
            st.success(f"「{new_task_name}」を追加しました。")
            st.rerun()
        else:
            st.warning("タスク名を入力してください。")

# --- メイン画面 (表示系) ---
st.title("📚 StudyFlow")
st.markdown("### `今、やるべきことに集中する`")

# --- タイマー表示エリア ---
timer_placeholder = st.empty()
if st.session_state.active_task_id:
    for task in st.session_state.tasks:
        if task['id'] == st.session_state.active_task_id:
            active_task = task
            break
    
    elapsed_time = time.time() - st.session_state.start_time
    display_time = str(datetime.timedelta(seconds=int(elapsed_time))).split('.')[0]

    with timer_placeholder.container():
        st.markdown(f"""
        <div class="timer-box">
            <p>実行中: {active_task['name']} ({active_task['deck']})</p>
            <h2>⏳ {display_time}</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"■ 停止する", key="stop_button"):
            task['total_time'] += elapsed_time
            st.session_state.active_task_id = None
            st.session_state.start_time = 0
            st.rerun()

# --- 目標表示エリア ---
if st.session_state.long_term_goal or st.session_state.short_term_goal:
    with st.expander("🎯 現在の目標を見る", expanded=True):
        if st.session_state.long_term_goal:
            st.markdown(f"**長期目標:** {st.session_state.long_term_goal}")
        if st.session_state.short_term_goal:
            st.markdown(f"**短期目標:** {st.session_state.short_term_goal}")

st.markdown("---")

# --- タスクカード表示エリア ---
st.header("タスクリスト")
if not st.session_state.tasks:
    st.info("サイドバーからタスクを追加してください。")
else:
    cols = st.columns(3)
    col_index = 0
    for task in sorted(st.session_state.tasks, key=lambda x: x['id'], reverse=True):
        with cols[col_index]:
            total_hms = str(datetime.timedelta(seconds=int(task['total_time']))).split('.')[0]
            with st.container(border=True):
                st.markdown(f"**{task['name']}**")
                st.markdown(f"<small style='color: gray;'>Deck: {task['deck']}</small>", unsafe_allow_html=True)
                st.markdown(f"🕒 累計: **{total_hms}**")

                # タイマーが動いていないときだけ「開始」ボタンを表示
                if not st.session_state.active_task_id:
                    if st.button("▶️ 開始", key=f"start_{task['id']}", use_container_width=True):
                        st.session_state.active_task_id = task['id']
                        st.session_state.start_time = time.time()
                        st.rerun()
        col_index = (col_index + 1) % 3
