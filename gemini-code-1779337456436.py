import streamlit as st
import pandas as pd

# 1. 웹 페이지 제목 및 설명 설정
st.set_page_config(page_title="누구나 쓰는 데이터 분석기", layout="wide")
st.title("📊 누구나 쓰는 데이터 분석 및 시각화 도구")
st.markdown("엑셀(xlsx) 또는 CSV 파일을 업로드하면 자동으로 분석과 시각화를 해줍니다.")

# 2. 파일 업로드 기능 (누구나 파일만 드래그 앤 드롭 하면 됨)
uploaded_file = st.file_uploader("분석할 파일을 선택하세요", type=["csv", "xlsx"])

if uploaded_file is not None:
    # 파일 확장자에 따라 판다스로 읽어오기
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # 화면을 두 칸으로 분할
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 데이터 미리보기")
        st.dataframe(df.head(10)) # 상위 10개 데이터 표로 출력
        
    with col2:
        st.subheader("📈 데이터 기본 통계")
        st.write(df.describe()) # 평균, 최소, 최대 등 자동 계산
        
    st.divider() # 구분선
    
    # 3. 마우스 클릭으로 시각화할 컬럼 선택하기
    st.subheader("📊 맞춤형 그래프 그리기")
    all_columns = df.columns.tolist()
    
    x_axis = st.selectbox("X축으로 사용할 컬럼을 고르세요", all_columns)
    y_axis = st.selectbox("Y축으로 사용할 컬럼을 고르세요 (숫자 데이터)", all_columns)
    
    chart_type = st.radio("그래프 종류", ["선 그래프", "막대 그래프"])
    
    if chart_type == "선 그래프":
        st.line_chart(df[[x_axis, y_axis]].set_index(x_axis))
    elif chart_type == "막대 그래프":
        st.bar_chart(df[[x_axis, y_axis]].set_index(x_axis))

    # 4. 분석된 파일 다시 다운로드하기
    st.divider()
    st.subheader("💾 파일 내보내기")
    
    # 간단한 필터링 예시 (첫 번째 컬럼 기준 정렬)
    sorted_df = df.sort_values(by=all_columns[0])
    
    # 다운로드 버튼 생성
    csv = sorted_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="정렬된 데이터 CSV로 다운로드",
        data=csv,
        file_name="analyzed_data.csv",
        mime="text/csv"
    )

else:
    st.info("💡 좌측 또는 상단의 업로드 창에 파일을 올려주세요.")