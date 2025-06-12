import streamlit as st
import pandas as pd

def generate_groups(df, group_size):
    df_sorted = df.sort_values(by='등수').reset_index(drop=True)
    num_students = len(df_sorted)
    groups = []
    for i in range(0, num_students, group_size):
        group = df_sorted.iloc[i:i+group_size]['이름'].tolist()
        # 부족한 인원은 '빈 자리'로 채움
        while len(group) < group_size:
            group.append("빈 자리")
        groups.append(group)
    # 열 이름 동적으로 설정
    columns = [f"학생 {i+1}" for i in range(group_size)]
    return pd.DataFrame(groups, columns=columns)

st.title("학생 이름과 석차 기반 다인 조편성 웹앱")

st.markdown("""
1. 학생 이름, 등수, 학급 정보가 포함된 엑셀 파일을 업로드하세요.
2. 파일에는 반드시 '이름', '등수', '학급' 열이 있어야 합니다.
3. 원하는 조 구성 인원을 선택하면 학급별로 전교석차를 기준으로 조를 나눕니다.
""")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
group_size = st.selectbox("몇 명이 한 조인가요?", options=[2, 3, 4], index=0)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        if all(col in df.columns for col in ['이름', '등수', '학급']):
            st.success("파일이 성공적으로 업로드되었습니다.")
            if st.button("조편성 결과 보기"):
                result_all = []
                for class_name, group in df.groupby('학급'):
                    grouped = generate_groups(group, group_size)
                    grouped.insert(0, '학급', class_name)
                    result_all.append(grouped)
                result_df = pd.concat(result_all, ignore_index=True)
                st.dataframe(result_df, use_container_width=True)
        else:
            st.error("엑셀 파일에 '이름', '등수', '학급' 열이 있어야 합니다.")
    except Exception as e:
        st.error(f"파일을 읽는 중 오류 발생: {e}")
