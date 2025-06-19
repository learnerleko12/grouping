import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
import random

# 한글 폰트 설정 (윈도우용, 맑은 고딕)
font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rcParams['font.family'] = font_name

# Google Sheets 연동
@st.cache_data
def load_data(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your_google_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("자리배치표데이터").worksheet(sheet_name)
    data = pd.DataFrame(sheet.get_all_records())
    return data

# 조 편성
def group_students(df, group_size):
    df = df.sort_values(by="과학점수", ascending=False).reset_index(drop=True)
    n = len(df)
    groups = []
    if group_size == 2:
        for i in range(n // 2):
            pair = pd.concat([df.iloc[[i]], df.iloc[[-(i+1)]]])
            groups.append(pair)
    elif group_size == 3:
        third = n // 3
        for i in range(third):
            group = pd.concat([df.iloc[[i]], df.iloc[[third+i]], df.iloc[[-(i+1)]]])
            groups.append(group)
    elif group_size == 4:
        quarter = n // 4
        for i in range(quarter):
            group = pd.concat([
                df.iloc[[i]],
                df.iloc[[quarter+i]],
                df.iloc[[2*quarter+i]],
                df.iloc[[-(i+1)]]
            ])
            groups.append(group)
    return groups

# 성별 섞기
def balance_gender(group):
    males = group[group['성별'] == '남']
    females = group[group['성별'] == '여']
    if len(males) == len(females):
        return pd.concat([males, females])
    else:
        return group.sample(frac=1)

# 좌석도 시각화
def draw_seating_chart(groups, rows, cols):
    fig, ax = plt.subplots(figsize=(cols, rows))
    ax.axis("off")

    total_seats = rows * cols
    flat_list = []
    for i, group in enumerate(groups, 1):
        names = "/".join(group['이름'].tolist())
        flat_list.append(f"{i}조\n{names}")
    while len(flat_list) < total_seats:
        flat_list.append("")

    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j
            ax.text(j, -i, flat_list[idx], ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.5", fc="lightblue", ec="gray"))

    ax.set_xlim(-0.5, cols - 0.5)
    ax.set_ylim(-rows + 0.5, 0.5)
    st.pyplot(fig)

# 🌐 Streamlit UI
st.title("🧠 과학 성적 기반 학급별 자리배치표")

sheet_name = st.text_input("구글 시트에서 불러올 반 이름을 입력하세요 (예: 1반)", value="1반")
group_size = st.radio("조 단위 선택", [2, 3, 4], horizontal=True)

cols = st.number_input("좌석 배치 - 열(가로)", min_value=1, max_value=10, value=6)
rows = st.number_input("좌석 배치 - 행(세로)", min_value=1, max_value=10, value=5)

if sheet_name:
    try:
        df = load_data(sheet_name)
        st.success(f"✅ {sheet_name} 데이터 불러오기 성공")
        st.dataframe(df)

        groups = group_students(df, group_size)
        st.markdown("### 📋 조 편성 결과")
        for i, group in enumerate(groups, 1):
            st.write(f"#### {i}조")
            balanced = balance_gender(group)
            st.table(balanced.reset_index(drop=True))

        st.markdown("### 🪑 좌석 배치 시각화")
        draw_seating_chart(groups, rows, cols)

    except Exception as e:
        st.error(f"❌ 오류: {e}")
