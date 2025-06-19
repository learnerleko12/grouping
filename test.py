import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Streamlit 파일 업로드
json_keyfile = st.file_uploader("🔑 서비스 계정 키(JSON)", type="json")

if json_keyfile is not None:
    with open("temp_key.json", "wb") as f:
        f.write(json_keyfile.read())

    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_key.json", scope)
    client = gspread.authorize(creds)

    # 구글 시트 URL 입력받기
    sheet_url = st.text_input("https://docs.google.com/spreadsheets/d/1QWoRvGJW-QbBwFEdUXlaMyT7QBl7V4PhGpkTdFU6uZU/edit?usp=sharing")

    if sheet_url:
        sheet = client.open_by_url(sheet_url).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.write("📊 시트 데이터 미리보기", df)
