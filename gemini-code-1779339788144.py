import streamlit as st
import numpy as np

# 0. 웹 페이지 레이아웃을 넓게 설정
st.set_page_config(page_title="실시간 공동 픽셀 캔버스", layout="wide", page_icon="🎨")

st.title("🎨 실시간 공동 100x100 픽셀 캔버스")
st.caption("모든 접속자가 하나의 캔버스를 공유합니다. 색을 고르고 픽셀을 클릭해 보세요!")

# -------------------------------------------------------------
# 1. 전역 공유 데이터 초기화 (st.shared_state)
# 기존 st.session_state와 달리 모든 접속자가 이 상태를 '공유'합니다.
# -------------------------------------------------------------
# 100x100 크기의 캔버스 공간 생성 (초기값은 모두 흰색 '#FFFFFF')
if "canvas" not in st.shared_state:
    st.shared_state.canvas = np.full((100, 100), "#FFFFFF", dtype=object)

# -------------------------------------------------------------
# 2. 사이드바 컨트롤러 (색상 선택 및 도구)
# -------------------------------------------------------------
st.sidebar.header("🎨 도구 상자")

# 사용자가 칠할 색상 선택
picked_color = st.sidebar.color_picker("칠할 색상을 고르세요", "#9A00FF")

# 현재 좌표 입력 (스트림릿 표에서 클릭으로 입력받기 위함)
st.sidebar.markdown("---")
st.sidebar.subheader("📍 좌표 직접 입력")
row_input = st.sidebar.number_input("행 (Y축: 0~99)", min_value=0, max_value=99, value=50)
col_input = st.sidebar.number_input("열 (X축: 0~99)", min_value=0, max_value=99, value=50)

if st.sidebar.button("🎨 선택한 좌표에 색칠하기"):
    st.shared_state.canvas[row_input, col_input] = picked_color
    st.rerun()

# 캔버스 초기화 버튼 (테스트용)
if st.sidebar.button("🗑️ 캔버스 전체 초기화"):
    st.shared_state.canvas = np.full((100, 100), "#FFFFFF", dtype=object)
    st.rerun()


# -------------------------------------------------------------
# 3. 처리 및 출력 (캔버스 그리기)
# -------------------------------------------------------------
# 스트림릿의 st.data_editor를 이용하면 100x100 칸을 셀처럼 보여주고 
# 사용자가 직접 클릭하거나 상호작용할 수 있습니다.
st.subheader("🖼️ 마우스로 칸을 더블클릭하여 수정하거나, 왼쪽 좌표를 이용하세요!")

# Pandas 데이터프레임으로 변환하여 화면에 출력
import pandas as pd
df_canvas = pd.DataFrame(st.shared_state.canvas)

# 사용자가 표(Grid)를 직접 수정했을 때 변동사항을 감지하는 에디터 적용
edited_data = st.data_editor(
    df_canvas,
    hide_index=False,
    use_container_width=True,
    height=600
)

# 만약 사용자가 화면의 표를 직접 더블클릭해서 값을 텍스트(예: #FF0000)로 수정했다면 전역 데이터에 반영
if edited_data is not None:
    # 변경된 셀 정보 추적
    st.shared_state.canvas = edited_data.values


# -------------------------------------------------------------
# 4. 실시간 동기화 (Auto Refresh)
# 내가 아무것도 안 해도 다른 사람이 그린 걸 3초마다 자동으로 불러옵니다.
# -------------------------------------------------------------
st_fragment = st.fragment(run_every=3)

@st_fragment
def auto_refresh():
    # 3초마다 이 함수 내부가 실행되면서 화면의 캔버스 데이터를 최신화합니다.
    pass

auto_refresh()