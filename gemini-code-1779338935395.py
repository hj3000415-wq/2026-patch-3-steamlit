import streamlit as st

# 0. 웹 페이지 설정 및 제목
st.set_page_config(page_title="간단한 텍스트 분석기", page_icon="✍️")
st.title("✍️ 간단한 텍스트 분석기")
st.caption("스트림릿의 '입력 - 처리 - 출력' 구조를 배우기 위한 앱입니다.")

st.divider()

# ----------------------------------------
# 1. 입력 (Input) : 사용자에게 데이터 받기
# ----------------------------------------
st.header("1. 입력 영역")
user_text = st.text_area(
    "분석할 영문 또는 국문 텍스트를 입력하세요:",
    value="Hello Streamlit! 스트림릿 배포를 축하합니다."
)

# 사용자 선택 옵션 입력 (라디오 버튼)
conversion_option = st.radio(
    "영문 대소문자 변환 옵션을 선택하세요:",
    ("변환 없음", "모두 대문자로 (UPPER)", "모두 소문자로 (lower)")
)


# ----------------------------------------
# 2. 처리 (Process) : 파이썬 코드로 데이터 가공하기
# ----------------------------------------
# 글자 수 및 단어 수 계산
char_count = len(user_text)                     # 공백 포함 글자 수
char_count_no_spaces = len(user_text.replace(" ", "")) # 공백 제외 글자 수
word_count = len(user_text.split())             # 단어 수

# 대소문자 변환 처리
if conversion_option == "모두 대문자로 (UPPER)":
    processed_text = user_text.upper()
elif conversion_option == "모두 소문자로 (lower)":
    processed_text = user_text.lower()
else:
    processed_text = user_text


# ----------------------------------------
# 3. 출력 (Output) : 가공된 결과를 웹 화면에 보여주기
# ----------------------------------------
st.divider()
st.header("2. 처리 및 출력 결과")

# 대시보드 형태로 숫자 출력 (st.metric 사용)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="공백 포함 글자 수", value=char_count)
with col2:
    st.metric(label="공백 제외 글자 수", value=char_count_no_spaces)
with col3:
    st.metric(label="단어 수", value=word_count)

# 변환된 텍스트 출력
st.subheader("📝 변환된 텍스트 결과")
st.code(processed_text, language="text")

# 성공 메시지 출력
st.success("텍스트 분석 및 처리가 성공적으로 완료되었습니다! 🎉")