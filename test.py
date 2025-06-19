import streamlit as st

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

json_keyfile = st.file_uploader("🔑 서비스 계정 키(JSON)", type="json")

if json_keyfile is not None:
    with open("temp_key.json", "wb") as f:
        f.write(json_keyfile.read())
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_key.json", scope)
    client = gspread.authorize(creds)



sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1QWoRvGJW-QbBwFEdUXlaMyT7QBl7V4PhGpkTdFU6uZU/edit?usp=sharing").sheet1
data = sheet.get_all_records()
print(data)
