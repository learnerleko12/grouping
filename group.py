import streamlit as st
import pandas as pd
import random

def generate_balanced_pairs(df):
    df_sorted = df.sort_values(by='등수').reset_index(drop=True)
    half = len(df_sorted) // 2
    top_half = df_sorted.iloc[:half].copy()
    bottom_half = df_sorted.iloc[-half:].copy().reset_index(drop=True)

    pairs = []
    used_bottom_indices = set()

    for idx, top_row in top_half.iterrows():
        candidate = None
        for b_idx, bottom_row in bottom_half.iterrows():
            if b_idx in used_bottom_indices:
                continue
            if top_row.get('성별') != bottom_row.get('성별'):
                candidate = bottom_row
                used_bottom_indices.add(b_idx)
                break
        if candidate is None:
            for b_idx, bottom_row in bottom_half.iterrows():
                if b_idx not in used_bottom_indices:
                    candidate = bottom_row
                    used_bottom_indices.add(b_idx)
                    break
        if candidate is not None:
            pairs.append((top_row['이름'], candidate['이름']))

    if len(df_sorted) % 2 == 1:
        pairs.append((df_sorted.iloc[half]['이름'], "짝 없음"))

    return pd.DataFrame(pairs, columns=["학생 1 (이름)", "학생 2 (이름)"])

def generate_balanced_trios(df):
    df_sorted = df.sort_values(by='등수').reset_index(drop=True)
    n = len(df_sorted)
    group_size = 3
    third = n // group_size

    top = df_sorted.iloc[:third].copy().reset_index(drop=True)
    middle = df_sorted.iloc[third:2*third].copy().reset_index(drop=True)
    bottom = df_sorted.iloc[2*third:3*third].copy().reset_index(drop=True)

    trios = []
    for i in range(third):
        trio = [top.loc[i, '이름'], middle.loc[i, '이름'], bottom.loc[i, '이름']]
        genders = [top.loc[i, '성별'], middle.loc[i, '성별'], bottom.loc[i, '성별']]
        if genders.count(genders[0]) == 3:
            if i + 1 < third:
                middle.loc[i], middle.loc[i+1] = middle.loc[i+1].copy(), middle.loc[i].copy()
                trio[1] = middle.loc[i, '이름']
                genders[1] = middle.loc[i, '성별']
        trios.append(trio)

    remaining = df_sorted.iloc[third*3:].copy()
    for i in range(0, len(remaining), group_size):
        trio = remaining.iloc[i:i+group_size]['이름'].tolist()
        while len(trio) < group_size:
            trio.append("빈 자리")
        trios.append(trio)

    columns = [f"학생 {i+1}" for i in range(group_size)]
    return pd.DataFrame(trios, columns=columns)

def generate_balanced_quads(df):
    df_sorted = df.sort_values(by='등수').reset_index(drop=True)
    n = len(df_sorted)
    quarter = n // 4

    g1 = df_sorted.iloc[:quarter].copy().reset_index(drop=True)
    g2 = df_sorted.iloc[quarter:2*quarter].copy().reset_index(drop=True)
    g3 = df_sorted.iloc[2*quarter:3*quarter].copy().reset_index(drop=True)
    g4 = df_sorted.iloc[3*quarter:4*quarter].copy().reset_index(drop=True)

    quads = []
    for i in range(min(len(g1), len(g2), len(g3), len(g4))):
        members = [g1.loc[i], g2.loc[i], g3.loc[i], g4.loc[i]]
        names = [m['이름'] for m in members]
        genders = [m['성별'] for m in members]
        if genders.count('남') == 4 or genders.count('여') == 4:
            for j in range(1, 4):
                if i + 1 < len(g1):
                    g2.loc[i], g2.loc[i+1] = g2.loc[i+1].copy(), g2.loc[i].copy()
                    names[1] = g2.loc[i, '이름']
                    genders[1] = g2.loc[i, '성별']
                    break
        quads.append(names)

    remaining = df_sorted.iloc[quarter*4:].copy()
    for i in range(0, len(remaining), 4):
        quad = remaining.iloc[i:i+4]['이름'].tolist()
        while len(quad) < 4:
            quad.append("빈 자리")
        quads.append(quad)

    columns = [f"학생 {i+1}" for i in range(4)]
    return pd.DataFrame(quads, columns=columns)

st.title(" 마장중 조편성 ")

st.markdown("""
1. 학생 이름, 등수, 학급, 성별 정보가 포함된 엑셀 파일을 업로드하세요.
2. 파일에는 반드시 '이름', '등수', '학급', '성별' 열이 있어야 합니다.
3. 2인 1조는 상하위 그룹에서 성별 다르게, 3인 1조는 상중하 그룹에서 성별 다양하게, 4인 1조는 4등분된 그룹에서 성별 다양하게 조를 구성합니다.
""")

uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
group_size = st.selectbox("몇 명이 한 조인가요?", options=[2, 3, 4], index=0)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        required_cols = ['이름', '등수', '학급', '성별']
        if all(col in df.columns for col in required_cols):
            st.success("파일이 성공적으로 업로드되었습니다.")
            if st.button("조편성 결과 보기"):
                result_all = []
                for class_name, group in df.groupby('학급'):
                    if group_size == 2:
                        grouped = generate_balanced_pairs(group)
                    elif group_size == 3:
                        grouped = generate_balanced_trios(group)
                    elif group_size == 4:
                        grouped = generate_balanced_quads(group)
                    grouped.insert(0, '학급', class_name)
                    result_all.append(grouped)
                result_df = pd.concat(result_all, ignore_index=True)
                st.dataframe(result_df, use_container_width=True)
        else:
            st.error(f"엑셀 파일에 {required_cols} 열이 있어야 합니다.")
    except Exception as e:
        st.error(f"파일을 읽는 중 오류 발생: {e}")
