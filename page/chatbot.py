# page/ragchatbot.py
import streamlit as st
from rag.rag_core import answer


def is_crisis_message(text: str) -> bool:
    t = (text or "").lower()
    keywords = [
        # 한국어
        "죽고 싶", "자살", "자해", "목숨", "끝내고 싶", "극단적 선택",
        "살기 싫", "죽을래", "죽어버", "죽고싶", "살기 힘들", "죽을까",
        # 영어
        "suicide", "kill myself", "end my life", "self-harm", "self harm",
    ]
    return any(k in t for k in keywords)


def crisis_banner():
    st.error(
        "지금 스스로를 해치고 싶은 생각이 든다면, 혼자 버티지 말고 **즉시 도움을 요청**해줘.\n\n"
        "- **지금 당장 위험하면:** 119(구급/화재) 또는 112(경찰)\n"
        "- **한국 정신건강 위기상담(24시간):** 1577-0199\n"
        "- **한국 생명의 전화(24시간):** 1588-9191\n"
    )


def handle_question(q: str):
    """
    - 위기 문구면: chat_history에 쌓고, '배너 표시 상태'를 session_state로 저장
      (rerun 이후에도 배너 유지)
    - 정상 문구면: 배너 숨김 + RAG 답변 생성
    """
    q = (q or "").strip()
    if not q:
        st.warning("질문을 입력해주세요.")
        return

    # 위기 상황 처리
    if is_crisis_message(q):
        st.session_state.chat_history.append(("user", q))
        st.session_state.chat_history.append(
            ("bot", "위기 상황일 수 있어요. 지금은 안전 안내를 먼저 제공할게요.")
        )
        st.session_state.show_crisis_banner = True  # ✅ rerun에도 유지
        return

    # 정상 질문이면 배너 숨김
    st.session_state.show_crisis_banner = False

    st.session_state.chat_history.append(("user", q))
    with st.spinner("답변 생성 중..."):
        result = answer(q, k=4)
        bot_answer = result.get("answer", "")

    st.session_state.chat_history.append(("bot", bot_answer))


def render_sample_questions():
    """채팅이 비어있을 때, 입력창 바로 위에 예시 질문 버튼을 보여줌"""
    st.markdown("#### 💡 예시 질문 (눌러서 바로 전송)")
    samples = [
        "우울증이 뭐예요?",
        "스트레스는 왜 생기나요?",
        "불안 장애에는 어떤 종류가 있나요?",
        "ADHD는 어떤 증상이 있나요?",
        "PTSD는 시간이 지나면 나아지나요?",
    ]

    cols = st.columns(2)
    for i, q in enumerate(samples):
        with cols[i % 2]:
            if st.button(q, use_container_width=True, key=f"sample_{i}"):
                handle_question(q)
                st.rerun()

    st.caption("※ 예시 버튼도 일반 질문과 동일하게 RAG 파이프라인으로 처리돼요.")


def app():
    
     # --- 사이드바 안내 문구 ---
    st.sidebar.markdown(
        "<small>💬 예시 질문: <br/>"
        "<i>우울증 치료에 가장 효과적인 약은 뭐야?</i>"
        "<i>스트레스랑 불안은 무슨 관계가 있어?</i></small>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
<div style="
    padding: 18px 24px;
    background: linear-gradient(90deg, #e8f5e9, #f1f8e9);
    border-radius: 14px;
    margin-bottom: 20px;
">
  <h2 style="margin:0;">🧠 정신 건강 정보 AI 챗봇</h2>
  <p style="margin:6px 0 0 0; color:#555;">
    WHO · NIMH 공신력 자료 기반 | 진단·치료 목적 아님
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # --- CSS (채팅 UI 유지) ---
    st.markdown(
        """
        <style>
          .chat-scroll {
            background: #f6f7f9;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 14px;
            padding: 14px;
            height: 520px;
            overflow-y: auto;
          }

          .row { display:flex; margin: 8px 0; }
          .row.user { justify-content:flex-end; }
          .row.bot  { justify-content:flex-start; }

          .bubble {
            max-width: 78%;
            padding: 10px 12px;
            border-radius: 14px;
            line-height: 1.5;
            border: 1px solid rgba(49, 51, 63, 0.12);
            word-break: break-word;
            white-space: pre-wrap;
          }
          .bubble.user { background: #dcf8c6; }
          .bubble.bot  { background: #ffffff; }

          .stForm { margin-top: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- session init ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ✅ rerun에도 유지되는 배너 상태
    if "show_crisis_banner" not in st.session_state:
        st.session_state.show_crisis_banner = False

    # --- 채팅 영역 렌더링 ---
    chat_html = ['<div class="chat-scroll">']

    # 채팅이 비어있으면 빈 화면 느낌 줄이기(선택)
    if len(st.session_state.chat_history) == 0:
        chat_html.append(
            '<div style="color:#777; padding:10px; line-height:1.6;">'
            "아래에서 예시 질문을 눌러 시작하거나, 직접 질문을 입력해보세요."
            "</div>"
        )

    for role, msg in st.session_state.chat_history:
        if role == "user":
            chat_html.append(
                f'<div class="row user"><div class="bubble user">{msg}</div></div>'
            )
        else:
            chat_html.append(
                f'<div class="row bot"><div class="bubble bot">{msg}</div></div>'
            )

    chat_html.append("</div>")
    st.markdown("\n".join(chat_html), unsafe_allow_html=True)

    # ✅ 예시 질문 위치: 채팅 아래 + 입력 위 (처음 진입/대화 없을 때만)
    if len(st.session_state.chat_history) == 0:
        render_sample_questions()

    # --- 입력 폼 (Enter 전송) ---
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([6, 1])

        with col_input:
            user_question = st.text_input(
                "질문 입력",
                placeholder="질문하세요…",
                label_visibility="collapsed",
            )

        with col_btn:
            submitted = st.form_submit_button("전송", use_container_width=True)

    # ✅ (중요) 배너는 "질문 입력칸 아래"에서 렌더링되도록 여기서 처리
    # rerun 이후에도 상태가 유지되므로, 위기 플래그가 True면 계속 보임
    if st.session_state.show_crisis_banner:
        crisis_banner()

    if not submitted:
        return

    handle_question(user_question)
    st.rerun()
