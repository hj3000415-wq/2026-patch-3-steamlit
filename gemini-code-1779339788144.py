import streamlit as st
import numpy as np
import pandas as pd
from collections import Counter
import time

# 0. 웹 페이지 설정
st.set_page_config(page_title="컬러 픽셀 점령전", layout="wide", page_icon="⚔️")

st.title("⚔️ 실시간 10x10 컬러 픽셀 점령전")
st.caption("팀을 고르고 10x10 영토를 확보하세요! 점령 후에는 1초의 초고속 공격 쿨타임이 적용됩니다.")

# -------------------------------------------------------------
# [게임 규칙 설정] 쿨타임 시간 수정 (1초로 단축 완료 ⚡)
# -------------------------------------------------------------
COOL_DOWN_TIME = 1  # 점령 후 재공격까지 대기 시간 (1초)

# 고유 색상 및 팀 정의
TEAM_OPTIONS = {
    "🔴 빨강 팀": "#FF4B4B",
    "🔵 파랑 팀": "#1C83E1",
    "🟢 초록 팀": "#29B560",
    "🟡 노랑 팀": "#F39C12"
}

# -------------------------------------------------------------
# 1. 전역 공유 데이터 설정 (@st.cache_resource)
# -------------------------------------------------------------
@st.cache_resource
def get_game_system_data():
    return {
        "canvas": np.full((10, 10), "#FFFFFF", dtype=object),
        "owner": np.full((10, 10), "⬜ 빈 땅", dtype=object),
        "game_over": False,
        "end_time": time.time() + 180  # 기본 게임 시간 3분
    }

game_data = get_game_system_data()

# 남은 게임 시간 계산
remaining_time = int(game_data["end_time"] - time.time())
if remaining_time <= 0:
    game_data["game_over"] = True
    remaining_time = 0

# -------------------------------------------------------------
# 2. 개인별 쿨타임 데이터 초기화 (st.session_state)
# -------------------------------------------------------------
if "next_attack_time" not in st.session_state:
    st.session_state.next_attack_time = 0.0  # 처음엔 바로 공격 가능

# 현재 내 쿨타임 남은 시간 계산
current_time = time.time()
cooldown_remaining = int(st.session_state.next_attack_time - current_time)

# -------------------------------------------------------------
# 3. 사이드바: 플레이어 조작창 및 쿨타임 표시
# -------------------------------------------------------------
st.sidebar.header("🎮 게임 참여 설정")

# 팀 선택
selected_team_name = st.sidebar.selectbox("당신의 팀을 선택하세요:", list(TEAM_OPTIONS.keys()))
player_color = TEAM_OPTIONS[selected_team_name]

st.sidebar.markdown("---")
st.sidebar.subheader("⚔️ 영토 확장 (공격)")

row_input = st.sidebar.number_input("행 좌표 (Y축: 0~9)", min_value=0, max_value=9, value=0)
col_input = st.sidebar.number_input("열 좌표 (X축: 0~9)", min_value=0, max_value=9, value=0)

current_owner = game_data["owner"][row_input, col_input]
st.sidebar.markdown(f"🎯 조준 칸 (`{row_input}`, `{col_input}`)의 현재 팀: **{current_owner}**")

st.sidebar.markdown("---")

# 🧊 쿨타임 1초 적용에 따른 버튼 상태 제어
if game_data["game_over"]:
    st.sidebar.error("🚨 게임이 종료되었습니다!")
elif cooldown_remaining > 0:
    # 쿨타임이 남아있으면 버튼을 비활성화하고 1초 대기 메시지 노출
    st.sidebar.button("⏳ 대기 중... (1초)", disabled=True)
else:
    # 쿨타임이 없으면 정상적으로 버튼 활성화
    if st.sidebar.button("⚔️ 이 땅을 점령하기!", type="primary"):
        # 1. 영토 데이터 업데이트
        game_data["canvas"][row_input, col_input] = player_color
        game_data["owner"][row_input, col_input] = selected_team_name
        
        # 2. 개인 쿨타임 적용 (현재 시간 + 1초)
        st.session_state.next_attack_time = time.time() + COOL_DOWN_TIME
        
        st.toast(f"🎉 {selected_team_name}이 ({row_input}, {col_input}) 땅을 점령했습니다!", icon="✅")
        st.rerun()

# 관리자용 리셋
if st.sidebar.button("🔄 새 게임 시작"):
    game_data["canvas"][:] = "#FFFFFF"
    game_data["owner"][:] = "⬜ 빈 땅"
    game_data["game_over"] = False
    game_data["end_time"] = time.time() + 180
    st.session_state.next_attack_time = 0.0  # 내 쿨타임도 초기화
    st.rerun()


# -------------------------------------------------------------
# 4. 메인 화면: 타이머, 점수판 및 맵 시각화
# -------------------------------------------------------------
if not game_data["game_over"]:
    st.subheader(f"⏳ 남은 시간: {remaining_time // 60}분 {remaining_time % 60}초")
    st.progress(min(max(remaining_time / 180, 0.0), 1.0))
else:
    st.error("🏁 게임 종료!! 결과를 확인하세요.")

col_map, col_rank = st.columns([2, 1])

all_owners = game_data["owner"].flatten()
rank_counts = Counter(all_owners)

with col_rank:
    st.subheader("🏆 팀별 영토 순위")
    unowned_count = rank_counts.pop("⬜ 빈 땅", 0)
    st.metric(label="남은 빈 땅", value=f"{unowned_count} / 100")
    
    df_rank = pd.DataFrame(rank_counts.items(), columns=["팀", "점령한 땅 (칸)"])
    df_rank = df_rank.sort_values(by="점령한 땅 (칸)", ascending=False).reset_index(drop=True)
    st.dataframe(df_rank, use_container_width=True)
    
    if game_data["game_over"]:
        st.divider()
        if not df_rank.empty:
            winner = df_rank.iloc[0]["팀"]
            winner_score = df_rank.iloc[0]["점령한 땅 (칸)"]
            st.balloons()
            st.success(f"👑 최종 결과: **{winner}**이 총 **{winner_score}칸**으로 대승리! 🎉")

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
# 5. 1초마다 자동 새로고침 (시간 및 쿨타임 실시간 동기화)
# -------------------------------------------------------------
st_fragment = st.fragment(run_every=1)

@st_fragment
def auto_refresh():
    pass

auto_refresh()
