import streamlit as st
import numpy as np
import pandas as pd

# 0. 웹 페이지 레이아웃을 넓게 설정
st.set_page_config(page_title="실시간 공동 픽셀 캔버스", layout="wide", page_icon="🎨")

st.title("🎨 실시간 공동 100x100 픽셀 캔버스")
st.caption("모든 접속자가 하나의 캔버스를 공유합니다. 왼쪽 도구상자에서 색을 고르고 좌표에 칠해 보세요!")

# -------------------------------------------------------------
# 1. 전역 공유 데이터 설정 (@st.cache_resource)
# -------------------------------------------------------------
@st.cache_resource
def get_shared_canvas():
    # 100x100 크기의 흰색('#FFFFFF') 도화지 생성
    return np.full((100, 100), "#FFFFFF", dtype=object)

shared_canvas = get_shared_canvas()


# -------------------------------------------------------------
# 2. 사이드바 도구 상자
# -------------------------------------------------------------
st.sidebar.header("🎨 도구 상자")

# 사용자가 칠할 색상 선택
picked_color = st.sidebar.color_picker("칠할 색상을 고르세요", "#9A00FF")

st.sidebar.markdown("---")
st.sidebar.subheader("📍 좌표 입력 후 색칠")

# 100x100 격자이므로 0~99까지 입력받음
row_input = st.sidebar.number_input("행 (Y축 좌표: 0~99)", min_value=0, max_value=99, value=50)
col_input = st.sidebar.number_input("열 (X축 좌표: 0~99)", min_value=0, max_value=99, value=50)

# 색칠하기 버튼을 누르면 공유 도화지의 해당 좌표 색상을 변경
if st.sidebar.button("🎨 선택한 좌표에 색칠하기"):
    shared_canvas[row_input, col_input] = picked_color
    st.toast(f"({row_input}, {col_input}) 좌표에 색을 칠했습니다!", icon="✅")
    st.rerun()

# 캔버스 초기화 버튼
if st.sidebar.button("🗑️ 캔버스 전체 초기화"):
    shared_canvas[:] = "#FFFFFF" 
    st.toast("캔버스가 초기화되었습니다.", icon="🗑️")
    st.rerun()


# -------------------------------------------------------------
# 3. 시각화 가공 (셀에 진짜 색상 입히기)
# -------------------------------------------------------------
st.subheader("🖼 " + f"현재 캔버스 상황 (실시간 동기화 중)")

# 1. Numpy 배열을 Pandas 데이터프레임으로 변환
df_canvas = pd.DataFrame(shared_canvas)

# 2. 각 셀에 적힌 색상 코드(#숫자)를 읽어서, 해당 셀의 배경색과 글자색을 그 색상으로 일치시키는 함수
def style_pixel_matrix(df):
    # 셀 안의 글자(#숫자)도 배경색과 똑같이 만들어서 글자가 안 보이고 색상만 채워지게 만듭니다.
    return df.map(lambda val: f"background-color: {val}; color: {val};")

# 스타일 적용하기
styled_df = df_canvas.style.apply(style_pixel_matrix, axis=None)


# 3. 화면에 진짜 색칠된 격자판 출력 (st.dataframe 사용)
# st.data_editor 대신 st.dataframe을 쓰면 스타일이 완벽하게 적용됩니다.
st.dataframe(
    styled_df,
    use_container_width=True,
    height=600
)


# -------------------------------------------------------------
# 4. 실시간 동기화 (Auto Refresh)
# -------------------------------------------------------------
st_fragment = st.fragment(run_every=3)

@st_fragment
def auto_refresh():
    pass

auto_refresh()
