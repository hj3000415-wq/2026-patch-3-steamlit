import streamlit as st
import numpy as np
import pandas as pd

# 0. 웹 페이지 레이아웃을 넓게 설정
st.set_page_config(page_title="실시간 공동 픽셀 캔버스", layout="wide", page_icon="🎨")

st.title("🎨 실시간 공동 100x100 픽셀 캔버스")
st.caption("모든 접속자가 하나의 캔버스를 공유합니다. 왼쪽 도구상자에서 색을 고르고 좌표에 칠해 보세요!")

# -------------------------------------------------------------
# 1. 전역 공유 데이터 설정 (@st.cache_resource)
# 이 내부에 저장되는 데이터는 모든 사용자가 공유하며, 앱이 재실행되어도 유지됩니다.
# -------------------------------------------------------------
@st.cache_resource
def get_shared_canvas():
    # 100x100 크기의 흰색('#FFFFFF') 도화지 생성
    return np.full((100, 100), "#FFFFFF", dtype=object)

# 공유 캔버스 가져오기
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
    shared_canvas[:] = "#FFFFFF" # 기존 배열 내용을 모두 흰색으로 덮어씀
    st.toast("캔버스가 초기화되었습니다.", icon="🗑️")
    st.rerun()


# -------------------------------------------------------------
# 3. 데이터 시각화 및 편집 (캔버스 그리기)
# -------------------------------------------------------------
st.subheader("🖼️ 현재 캔버스 상황")
st.info("💡 팁: 왼쪽 도구상자에서 좌표를 입력해 색을 칠하거나, 아래 표의 셀을 더블클릭해 색상 코드(예: #FF0000)를 직접 수정할 수도 있습니다.")

# Numpy 배열을 Pandas 데이터프레임으로 변환하여 출력
df_canvas = pd.DataFrame(shared_canvas)

# 사용자가 표를 직접 수정하는 경우를 위한 에디터
edited_data = st.data_editor(
    df_canvas,
    hide_index=False,
    use_container_width=True,
    height=550
)

# 사용자가 화면의 표를 직접 수정했다면 공유 도화지에 즉시 동기화
if edited_data is not None:
    shared_canvas[:] = edited_data.values


# -------------------------------------------------------------
# 4. 실시간 동기화 (Auto Refresh)
# 다른 사람이 그린 내용을 3초마다 자동으로 감지하여 내 화면에 업데이트합니다.
# -------------------------------------------------------------
st_fragment = st.fragment(run_every=3)

@st_fragment
def auto_refresh():
    # 3초마다 이 백그라운드 함수가 돌면서 화면을 최신 공유 데이터 상태로 유지합니다.
    pass

auto_refresh()
