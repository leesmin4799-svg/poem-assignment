import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# 학생 데이터와 관리자 예시를 저장할 파일명
DATA_FILE = "submissions.csv"
EXAMPLE_FILE = "example_data.csv"

# 웹페이지 기본 설정
st.set_page_config(page_title="生きる 작시 과제", layout="centered")

st.title("生きる 작시 과제")

# 1. 예시 답안 표시 (관리자가 제출한 기록이 있을 경우)
if os.path.exists(EXAMPLE_FILE):
    example_df = pd.read_csv(EXAMPLE_FILE)
    if not example_df.empty:
        st.info("📖 참고 예시 (관리자 제출)")
        # 가장 최근에 제출한 예시 1개만 보여줌
        latest_example = example_df.iloc[-1]
        st.write("**[창작한 시]**")
        st.text(latest_example['작성한 시 (5행)'])
        st.write("**['그늘'에 대한 답변]**")
        st.text(latest_example['그늘에 대한 질문 답변'])

st.markdown("---")

# 2. 학생 과제 제출 폼
name = st.text_input("이름 (※ 관리자의 경우 '관리자'라고 입력)")
student_id = st.text_input("학번 (예: 20261234)")

st.info("**[과제 지시사항]**\n\n冒頭二行の形式「生きていること、今生きていること」を借りて、自分の「いま」を五行書く。")
poem = st.text_area("자신의 시 (5행)", height=150)

st.write("[추가 질문] 당신의 시 중에 '그늘'에 해당하는 행이 있습니까? 있다면 왜 넣었으며, 넣지 않았다면 왜 넣지 않았습니까?")
reason = st.text_area("자신의 생각과 이유를 서술해 주세요.", height=150)

# 3. 제출 버튼 동작
if st.button("최종 제출하기", type="primary"):
    if not name or not student_id or not poem or not reason:
        st.warning("모든 항목을 입력해 주세요.")
    else:
        # 제출된 데이터를 표 형태로 정리
        new_data = pd.DataFrame({
            "이름": [name],
            "학번": [student_id],
            "작성한 시 (5행)": [poem],
            "그늘에 대한 질문 답변": [reason],
            "제출시간": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })

        if name == '관리자':
            # 관리자 예시로 별도 저장
            if os.path.exists(EXAMPLE_FILE):
                existing = pd.read_csv(EXAMPLE_FILE)
                updated = pd.concat([existing, new_data])
                updated.to_csv(EXAMPLE_FILE, index=False)
            else:
                new_data.to_csv(EXAMPLE_FILE, index=False)
            st.success("예시 답안이 성공적으로 등록되었습니다! 화면을 새로고침 해주세요.")
        else:
            # 일반 학생 과제로 저장
            if os.path.exists(DATA_FILE):
                existing = pd.read_csv(DATA_FILE)
                updated = pd.concat([existing, new_data])
                updated.to_csv(DATA_FILE, index=False)
            else:
                new_data.to_csv(DATA_FILE, index=False)
            st.success("제출이 완료되었습니다. 수고하셨습니다!")

# ==========================================
# 4. 관리자용 엑셀 다운로드 메뉴 (왼쪽 사이드바)
# ==========================================
st.sidebar.title("👨‍🏫 관리자 메뉴")
st.sidebar.write("학생들의 제출 결과를 엑셀로 다운로드합니다.")

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    st.sidebar.write(f"**현재 제출 인원: {len(df)}명**")
    
    # 엑셀 파일로 메모리 상에서 변환
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_data = excel_buffer.getvalue()
    
    # 다운로드 버튼 생성
    st.sidebar.download_button(
        label="📥 학생 제출 결과 다운로드 (Excel)",
        data=excel_data,
        file_name="학생과제_제출결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.sidebar.write("아직 제출한 학생이 없습니다.")