# app.py
import streamlit as st

st.set_page_config(
    page_title="StudyFlow",
    page_icon="📚",
    layout="wide"
)

st.title("📚 StudyFlow - 学習管理アプリ")

st.header("長期目標")
long_term_goal = st.text_input("例：〇〇大学合格！", key="long_goal")

st.header("短期目標")
short_term_goal = st.text_input("例：今月中に数学の基礎問題集を終わらせる", key="short_goal")

st.header("タスク")
st.info("ここにタスクカードやタイマー機能を作っていきます。")

# 画面下部に著作権表示など
st.markdown("---")
st.write("© 2024 Your Name. All Rights Reserved.")
