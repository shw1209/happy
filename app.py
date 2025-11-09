import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# 페이지 설정
st.set_page_config(page_title="Daily Mood Tracker", page_icon="📅", layout="centered")

# CSV 파일 경로
CSV_FILE = "mood_data.csv"

# CSV 파일이 없으면 생성
def init_csv_file():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['date', 'mood', 'journal'])
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

# CSV 파일에서 데이터 불러오기
def load_data():
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
        # date 컬럼을 datetime으로 변환
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['date', 'mood', 'journal'])

# 데이터 저장하기
def save_entry(date, mood, journal):
    new_row = pd.DataFrame({
        'date': [date.strftime('%Y-%m-%d')],
        'mood': [int(mood)],
        'journal': [journal]
    })
    
    df = load_data()
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')

# 이번 주 평균 기분 계산
def calculate_weekly_average(df):
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)  # 오늘 포함 7일
    
    # 날짜 필터링
    df['date_only'] = df['date'].dt.date
    weekly_data = df[(df['date_only'] >= week_ago) & (df['date_only'] <= today)]
    
    if len(weekly_data) == 0:
        return None
    
    return weekly_data['mood'].mean()

# 앱 초기화
init_csv_file()

# 제목
st.title("Daily Mood Tracker 📅")

# 입력 섹션 (form 사용)
with st.form("mood_entry_form"):
    st.subheader("기분 기록하기")
    
    # 날짜 선택 (기본값: 오늘)
    selected_date = st.date_input("날짜", value=datetime.now().date())
    
    # 기분 선택 (라디오 버튼 사용)
    mood_options = {
        1: "😞",
        2: "😐",
        3: "🙂",
        4: "😊",
        5: "😄"
    }
    
    mood_label = st.radio(
        "기분을 선택하세요",
        options=list(mood_options.keys()),
        format_func=lambda x: f"{mood_options[x]} ({x}점)",
        horizontal=True
    )
    
    # 한 줄 일기 입력
    journal_text = st.text_input("한 줄 일기", placeholder="오늘 하루를 한 줄로 기록해보세요...")
    
    # 저장하기 버튼
    submitted = st.form_submit_button("저장하기", use_container_width=True)
    
    if submitted:
        if journal_text.strip():
            save_entry(selected_date, mood_label, journal_text)
            st.success("저장되었습니다! 🎉")
            st.rerun()
        else:
            st.warning("일기를 입력해주세요!")

# 통계 섹션
st.divider()
st.subheader("📊 이번 주 통계")

df = load_data()

if not df.empty:
    weekly_avg = calculate_weekly_average(df)
    
    if weekly_avg is not None:
        # 평균 기분을 이모지로 변환
        avg_rounded = round(weekly_avg)
        mood_emoji = {
            1: "😞",
            2: "😐",
            3: "🙂",
            4: "😊",
            5: "😄"
        }
        emoji = mood_emoji.get(avg_rounded, "😐")
        
        # st.metric으로 표시
        st.metric(
            label="이번 주 평균 기분",
            value=f"{weekly_avg:.1f} / 5",
            delta=f"{emoji} 평균 {avg_rounded}점"
        )
    else:
        st.info("이번 주 기록이 없습니다.")
else:
    st.info("기록이 없습니다. 첫 기록을 남겨보세요!")

# 기록 목록 섹션
st.divider()
st.subheader("📝 전체 기록")

if not df.empty:
    # 날짜 컬럼을 문자열로 변환 (표시용)
    df_display = df.copy()
    df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')
    
    # 기분 숫자를 이모지로 변환
    mood_emoji_map = {
        1: "😞",
        2: "😐",
        3: "🙂",
        4: "😊",
        5: "😄"
    }
    df_display['mood'] = df_display['mood'].map(mood_emoji_map)
    
    # 컬럼명 한글화
    df_display.columns = ['날짜', '기분', '일기']
    
    # 최신순으로 정렬 (날짜 내림차순)
    df_display = df_display.sort_values('날짜', ascending=False).reset_index(drop=True)
    
    # 표로 표시
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("아직 기록이 없습니다. 첫 기록을 남겨보세요! 📝")

