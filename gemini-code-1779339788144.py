import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter
import time

# 0. 웹 페이지 설정
st.set_page_config(page_title="컬러 픽셀 점령전", layout="wide", page_icon="⚔️")

st.title("⚔️ 실시간 10x10 컬러 픽셀 점령전")
st.caption("팀을 고르고 10x10 영토를 가장 많이 확보하세요! 게임이 끝나면 가장 많은 영역을 차지한 팀이 승리합니다.")

# -------------------------------------------------------------
# 1. 고유 색상 및 팀 정의 (초기 고정 설정)
# -------------------------------------------------------------
TEAM_OPTIONS = {
    "🔴 빨강 팀": "#FF4B4B",
    "🔵 파랑 팀": "#1C83E1",
    "🟢 초록 팀": "#29B560",
    "🟡 노랑 팀": "#F39C12"
}

# -------------------------------------------------------------
# 2. 전역 공유 데이터 설정 (@st.cache_resource)
# -------------------------------------------------------------
@st.cache_resource
def get_game_system_data():
    return {
        "canvas": np.full((10, 10), "#FFFFFF", dtype=object),
        "owner": np.full((10, 10), "⬜ 빈 땅", dtype=object),
        "game_over": False,
        "end_time": time.time() + 180  # 기본 게임 시간 설정 (예: 앱 시작/초기화 후 3분)
    }

game_data = get_game_system_data()

# 남은 시간 계산 (초 단위)
remaining_time = int(game_data["end_time"] - time.time())
if remaining_time <= 0:
    game_data["game_over"] = True
    remaining_time = 0

# -------------------------------------------------------------
# 3. 사이드바: 플레이어 조작창
# -------------------------------------------------------------
st.sidebar.header("🎮 게임 참여 설정")

# 닉네임 대신 정해진 색상 팀 선택하기
selected_team_name = st.sidebar.selectbox("당신의 팀을 선택하세요:", list(TEAM_OPTIONS.keys()))
player_color = TEAM_OPTIONS[selected_team_name]

st.sidebar.markdown("---")
st.sidebar.subheader("⚔️ 영토 확장 (공격)")

row_input = st.sidebar.number_input("행 좌표 (Y축: 0~9)", min_value=0, max_value=9, value=0)
col_input = st.sidebar.number_input("열 좌표 (X축: 0~9)", min_value=0, max_value=9, value=0)

# 현재 칸 상태 조회
current_owner = game_data["owner"][row_input, col_input]
st.sidebar.markdown(f"🎯 조준 칸 (`{row_input}`, `{col_input}`)의 현재 팀: **{current_owner}**")

# 게임 진행 중일 때만 점령 가능
if not game_data["game_over"]:
    if st.sidebar.button("⚔️ 이 땅을 점령하기!"):
        game_data["canvas"][row_input, col_input] = player_color
        game_data["owner"][row_input, col_input] = selected_team_name
        st.toast(f"🎉 {selected_team_name}이 ({row_input}, {col_input}) 땅을 점령했습니다!", icon="✅")
        st.rerun()
else:
    st.sidebar.error("🚨 게임이 종료되었습니다! 조작할 수 없습니다.")

# 관리자용 리셋 및 새 게임 시작 버튼
st.sidebar.markdown("---")
if st.sidebar.button("🔄 새 게임 시작 (타이머 리셋)"):
    game_data["canvas"][:] = "#FFFFFF"
    game_data["owner"][:] = "⬜ 빈 땅"
    game_data["game_over"] = False
    game_data["end_time"] = time.time() + 120  # 새로 시작 시 2분(120초) 제공
    st.rerun()


# -------------------------------------------------------------
# 4. 메인 화면: 타이머, 점수판 및 맵 시각화
# -------------------------------------------------------------
# 타이머 및 게임 상태 출력
if not game_data["game_over"]:
    st.subheader(f"⏳ 남은 시간: {remaining_time // 60}분 {remaining_time % 60}초")
    st.progress(min(max(remaining_time / 120, 0.0), 1.0)) # 게이지 바 출력
else:
    st.error("🏁 게임 종료!! 결과를 확인하세요.")

col_map, col_rank = st.columns([2, 1])

# 전체 100개 칸 집계
all_owners = game_data["owner"].flatten()
rank_counts = Counter(all_owners)

with col_rank:
    st.subheader("🏆 팀별 영토 순위")
    
    unowned_count = rank_counts.pop("⬜ 빈 땅", 0)
    st.metric(label="남은 빈 땅", value=f"{unowned_count} / 100")
    
    # 랭킹 데이터프레임 가공
    df_rank = pd.DataFrame(rank_counts.items(), columns=["팀", "점령한 땅 (칸)"])
    df_rank = df_rank.sort_values(by="점령한 땅 (칸)", ascending=False).reset_index(drop=True)
    st.dataframe(df_rank, use_container_width=True)
    
    # 게임 종료 시 최종 승리자 판정문 출력
    if game_data["game_over"]:
        st.divider()
        if not df_rank.empty:
            winner = df_rank.iloc[0]["팀"]
            winner_score = df_rank.iloc[0]["점령한 땅 (칸)"]
            st.balloons() # 축하 효과 생성
            st.success(f"👑 최종 결과: **{winner}**이 총 **{winner_score}칸**을 차지하여 대승리를 거두었습니다! 🎉")
        else:
            st.warning("아무도 땅을 차지하지 못해 무승부로 끝났습니다! 🏳️")

with col_map:
    st.subheader("🗺️ 10x10 실시간 정세 지도")
    
    df_canvas = pd.DataFrame(game_data["canvas"])
    df_canvas.index = [f"행{i}" for i in range(10)]
    df_canvas.columns = [f"열{i}" for i in range(10)]
    
    def style_pixel_matrix(df):
        return df.map(lambda val: f"background-color: {val}; color: {val};")
    
    styled_df = df_canvas.style.apply(style_pixel_matrix, axis=None)
    
    st.dataframe(styled_df, use_container_width=True, height=400)


# -------------------------------------------------------------
# 5. 1초마다 자동 새로고침 (시간 카운트다운을 위해 1초로 단축)
# -------------------------------------------------------------
st_fragment = st.fragment(run_every=1)

@st_fragment
def auto_refresh():
    pass

auto_refresh()
