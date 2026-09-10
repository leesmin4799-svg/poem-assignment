import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# 학생 데이터와 관리자 예시를 저장할 파일명
DATA_FILE = "submissions.csv"
EXAMPLE_FILE = "example_data.csv"

# 관리자 비밀번호
ADMIN_PASSWORD = "hufs1234"

# 웹페이지 기본 설정
st.set_page_config(page_title="生きる 작시 과제", layout="centered")

# ==========================================
# 세션 상태(Session State) 초기화
# 페이지가 새로고침되어도 입력한 데이터를 기억하게 해줍니다.
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'student_id' not in st.session_state:
    st.session_state.student_id = ""
if 'poem' not in st.session_state:
    st.session_state.poem = ""
if 'reason' not in st.session_state:
    st.session_state.reason = ""

st.title("生きる 작시 과제")

# 1. 예시 답안 표시 (관리자가 제출한 기록이 있을 경우)
if os.path.exists(EXAMPLE_FILE):
    example_df = pd.read_csv(EXAMPLE_FILE)
    if not example_df.empty:
        st.info("📖 참고 예시 (관리자 제출)")
        latest_example = example_df.iloc[-1]
        st.write("**[창작한 시]**")
        st.text(latest_example['작성한 시 (5행)'])
        st.write("**['그늘'에 대한 답변]**")
        st.text(latest_example['그늘에 대한 질문 답변'])

st.markdown("---")

# ==========================================
# 2. 단계별 과제 제출 폼
# ==========================================

# [1단계 화면]
if st.session_state.step == 1:
    st.subheader("1단계: 기본 정보 및 시 작성")
    
    # 이전 단계로 돌아왔을 때 값을 유지하기 위해 value 속성 사용
    name = st.text_input("이름 (※ 관리자의 경우 '관리자'라고 입력)", value=st.session_state.name)
    student_id = st.text_input("학번 (예: 20261234)", value=st.session_state.student_id)
    
    st.info("**[과제 지시사항]**\n\n冒頭二行の形式「生きていること、今生きていること」を借りて、自分の「いま」を五行書く。")
    poem = st.text_area("자신의 시 (5행)", height=150, value=st.session_state.poem)
    
    # 다음 단계로 넘어가는 버튼
    if st.button("다음 질문으로 넘어가기", type="primary"):
        if not name or not student_id or not poem:
            st.warning("이름, 학번, 그리고 시를 모두 작성해 주세요.")
        else:
            # 입력된 데이터를 세션에 저장하고 2단계로 이동
            st.session_state.name = name
            st.session_state.student_id = student_id
            st.session_state.poem = poem
            st.session_state.step = 2
            st.rerun() # 화면 새로고침

# [2단계 화면]
elif st.session_state.step == 2:
    st.subheader("2단계: 시에 대한 추가 질문")
    
    # 1단계에서 작성한 시를 다시 보여줌
    st.write("📝 **내가 작성한 시**")
    st.info(st.session_state.poem)
    
    st.write("[추가 질문] 당신의 시 중에 '그늘'에 해당하는 행이 있습니까? 있다면 왜 넣었으며, 넣지 않았다면 왜 넣지 않았습니까?")
    reason = st.text_area("자신의 생각과 이유를 서술해 주세요.", height=150, value=st.session_state.reason)
    
    # 버튼을 양옆으로 배치하기 위해 컬럼 나누기
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("이전 단계로 수정하러 가기"):
            st.session_state.reason = reason # 작성 중이던 내용 임시 저장
            st.session_state.step = 1
            st.rerun()
            
    with col2:
        if st.button("최종 제출하기", type="primary"):
            if not reason:
                st.warning("마지막 질문에 대한 답변을 작성해 주세요.")
            else:
                # 최종 제출할 데이터 묶기
                new_data = pd.DataFrame({
                    "이름": [st.session_state.name],
                    "학번": [st.session_state.student_id],
                    "작성한 시 (5행)": [st.session_state.poem],
                    "그늘에 대한 질문 답변": [reason],
                    "제출시간": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                })

                if st.session_state.name == '관리자':
                    if os.path.exists(EXAMPLE_FILE):
                        existing = pd.read_csv(EXAMPLE_FILE)
                        updated = pd.concat([existing, new_data])
                        updated.to_csv(EXAMPLE_FILE, index=False)
                    else:
                        new_data.to_csv(EXAMPLE_FILE, index=False)
                    st.success("예시 답안이 성공적으로 등록되었습니다!")
                else:
                    if os.path.exists(DATA_FILE):
                        existing = pd.read_csv(DATA_FILE)
                        updated = pd.concat([existing, new_data])
                        updated.to_csv(DATA_FILE, index=False)
                    else:
                        new_data.to_csv(DATA_FILE, index=False)
                    st.success("제출이 완료되었습니다. 수고하셨습니다!")
                    st.balloons() # 제출 성공 축하 애니메이션
                
                # 제출이 끝났으므로 다음 사람을 위해 모든 입력칸과 단계를 초기화
                for key in ['name', 'student_id', 'poem', 'reason']:
                    st.session_state[key] = ""
                st.session_state.step = 1

# ==========================================
# 3. 관리자용 엑셀 다운로드 메뉴 (왼쪽 사이드바)
# ==========================================
st.sidebar.title("👨‍🏫 관리자 메뉴")
st.sidebar.write("결과를 다운로드하려면 비밀번호를 입력하세요.")

input_password = st.sidebar.text_input("관리자 비밀번호", type="password")

if input_password == ADMIN_PASSWORD:
    st.sidebar.success("인증되었습니다.")
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.sidebar.write(f"**현재 제출 인원: {len(df)}명**")
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_data = excel_buffer.getvalue()
        
        st.sidebar.download_button(
            label="📥 학생 제출 결과 다운로드",
            data=excel_data,
            file_name="학생과제_제출결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.sidebar.write("아직 제출한 학생이 없습니다.")
elif input_password != "":
    st.sidebar.error("비밀번호가 일치하지 않습니다.")
