import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
import random

# ✅ Windows에서 한글 깨짐 방지: 사용 가능한 한글 폰트 자동 설정

def set_korean_font():
    font_candidates = ['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'Noto Sans CJK KR']
    available_fonts = set(f.name for f in fm.fontManager.ttflist)
    for font in font_candidates:
        if font in available_fonts:
            matplotlib.rcParams['font.family'] = font
            return font
    return None

set_korean_font()

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

# ... (생략된 나머지 함수는 동일하게 유지)

# draw_seating_chart 및 main 함수는 유지
