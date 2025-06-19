import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("streamlit-seating-app-91760f4712ae.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1QWoRvGJW-QbBwFEdUXlaMyT7QBl7V4PhGpkTdFU6uZU/edit?usp=sharing").sheet1
data = sheet.get_all_records()
print(data)
