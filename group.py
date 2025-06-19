import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

st.title("📚 학급별 학생 좌석표 생성기 (그림 포함)")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_keyfile = st.file_uploader("🔑 서비스 계정 키(JSON) 업로드", type="json")

if json_keyfile is not None:
    with open("temp_key.json", "wb") as f:
        f.write(json_keyfile.read())

    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_key.json", scope)
    client = gspread.authorize(creds)

    sheet_url = st.text_input("📄 구글 시트 URL 입력")

    if sheet_url:
        try:
            sheet = client.open_by_url(sheet_url).sheet1
            data = sheet.get_all_records()
            if not data:
                st.warning("시트에 데이터가 없습니다.")
            else:
                df = pd.DataFrame(data)
                st.write("🎓 불러온 학생 데이터", df)

                if "학급" not in df.columns or "성적" not in df.columns or "이름" not in df.columns:
                    st.error("'학급', '성적', '이름' 컬럼이 모두 있어야 합니다.")
                else:
                    group_size = st.selectbox("👥 몇 명씩 조로 묶을까요?", [2, 3, 4], index=0)

                    classes = df["학급"].unique()
                    st.write(f"총 학급 수: {len(classes)}")

                    def make_pairs(df_sorted, group_size):
                        students = df_sorted["이름"].tolist()
                        n = len(students)
                        groups = []
                        left, right = 0, n - 1
                        while left <= right:
                            group = []
                            for _ in range(group_size):
                                if left <= right:
                                    group.append(students[left])
                                    left += 1
                                if len(group) < group_size and left <= right:
                                    group.append(students[right])
                                    right -= 1
                            groups.append(group)
                        return groups

                    for cls in classes:
                        st.subheader(f"🏫 학급: {cls}")
                        df_cls = df[df["학급"] == cls].sort_values(by="성적", ascending=False).reset_index(drop=True)

                        groups = make_pairs(df_cls, group_size)

                        # 좌석 배치 시각화
                        fig, ax = plt.subplots(figsize=(group_size*2, len(groups)*1.5))
                        ax.set_xlim(0, group_size)
                        ax.set_ylim(0, len(groups))
                        ax.invert_yaxis()
                        ax.axis('off')

                        for row_i, group in enumerate(groups):
                            for col_i, student in enumerate(group):
                                # 사각형 박스 그리기
                                rect = plt.Rectangle((col_i, row_i), 1, 1, fill=True, edgecolor='black', facecolor='lightblue')
                                ax.add_patch(rect)
                                # 학생 이름 텍스트 중앙 배치
                                ax.text(col_i + 0.5, row_i + 0.5, student, ha='center', va='center', fontsize=10)

                        plt.title(f"{cls} 학급 좌석 배치 ({group_size}명씩 조)", fontsize=14)
                        st.pyplot(fig)

        except Exception as e:
            st.error(f"시트 데이터 불러오기 중 오류: {e}")
else:
    st.info("서비스 계정 키(JSON) 파일을 업로드해주세요.")
