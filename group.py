import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.title("📚 학생 좌석표 생성기")

# 1. 구글 시트 인증 범위
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 2. 서비스 계정 JSON 업로드
json_keyfile = st.file_uploader("🔑 서비스 계정 키(JSON) 업로드", type="json")

if json_keyfile is not None:
    # 임시로 저장
    with open("temp_key.json", "wb") as f:
        f.write(json_keyfile.read())

    # 구글 인증 및 클라이언트 생성
    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_key.json", scope)
    client = gspread.authorize(creds)

    # 3. 구글 시트 URL 입력
    sheet_url = st.text_input("📄 구글 시트 URL 입력")

    if sheet_url:
        try:
            sheet = client.open_by_url(sheet_url).sheet1
            data = sheet.get_all_records()

            if len(data) == 0:
                st.warning("시트에 데이터가 없습니다.")
            else:
                df = pd.DataFrame(data)
                st.write("🎓 불러온 학생 성적 데이터", df)

                # 4. 조 크기 선택
                group_size = st.selectbox("👥 몇 명씩 조로 묶을까요?", [2, 3, 4], index=0)

                # 5. 성적 순으로 정렬 (내림차순, 1등이 위)
                # 성적 컬럼명은 데이터에 따라 조정 필요 (예: '점수', '성적', 'score')
                # 여기서는 '성적' 컬럼명 가정
                if "score" not in df.columns:
                    st.error("데이터에 'score' 컬럼이 없습니다. 컬럼명을 확인해주세요.")
                else:
                    df_sorted = df.sort_values(by="score", ascending=False).reset_index(drop=True)

                    # 6. 좌석표 짝짓기 함수
                    def make_pairs(df_sorted, group_size):
                        students = df_sorted["이름"].tolist()
                        scores = df_sorted["score"].tolist()

                        n = len(students)
                        groups = []

                        # 기본 아이디어: 1등 ↔ 꼴찌, 2등 ↔ 꼴찌 2번째, 3등 ↔ 꼴찌 3번째 ...
                        # 다만 group_size마다 그룹 묶기 다르게 처리

                        # 그룹 수
                        group_count = n // group_size
                        remainder = n % group_size

                        # 인덱스 포인터
                        left = 0
                        right = n - 1

                        while left <= right:
                            group = []
                            # 그룹에 한 명씩 왼쪽(높은 성적)에서, 오른쪽(낮은 성적)에서 채우기
                            for _ in range(group_size):
                                if left <= right:
                                    group.append(students[left])
                                    left += 1
                                if len(group) < group_size and left <= right:
                                    group.append(students[right])
                                    right -= 1
                            groups.append(group)

                        # 만약 잉여 학생이 있으면 마지막 그룹에 추가
                        if remainder > 0 and groups:
                            last_group = groups[-1]
                            if len(last_group) < group_size:
                                # 이미 처리함, 어차피 last group은 다 차있을 수 있음
                                pass

                        return groups

                    groups = make_pairs(df_sorted, group_size)

                    # 7. 좌석표 출력
                    st.subheader("🪑 좌석표 결과")

                    for i, group in enumerate(groups):
                        st.write(f"**조 {i+1}**: {', '.join(group)}")

        except Exception as e:
            st.error(f"시트 데이터 불러오기 중 오류 발생: {e}")

else:
    st.info("서비스 계정 키(JSON) 파일을 업로드해주세요.")
