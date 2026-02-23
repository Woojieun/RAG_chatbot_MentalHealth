import streamlit as st
from utils import project1_desc as p1d

def app():
    st.set_page_config(
        page_title="Streamlit 매뉴얼 (Project)",
        page_icon="📘",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ---- Simple styling ----
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1100px; }
          .badge { display:inline-block; padding: .18rem .55rem; border-radius: 999px;
                   border: 1px solid rgba(0,0,0,.12); font-size: .85rem; margin-right:.35rem; }
          .subtle { color: rgba(0,0,0,.6); }
          .card {
              padding: 1rem 1.1rem; border-radius: 16px; border: 1px solid rgba(0,0,0,.08);
              background: rgba(255,255,255,.7);
              box-shadow: 0 6px 22px rgba(0,0,0,.06);
          }
          hr { margin: 1.2rem 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header ----
    st.markdown(
        """
        <div class="card">
          <div style="display:flex; align-items:center; gap:.6rem; flex-wrap:wrap;">
            <div style="font-size:1.6rem; font-weight:800;">📘 Streamlit 매뉴얼</div>
            <span class="badge">RAG 기반 정신 건강 정보 지원 챗봇</span>
            <span class="badge">프로젝트 전용</span>
          </div>
          <div class="subtle" style="margin-top:.2rem;">
            이 문서는 프로젝트 코드에서 실제로 사용한 Streamlit 기능만 요약합니다.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # ---- Sidebar navigation ----
    sections = [
        "0. 개요",
        "1. 실행 방법",
        "2. 프로젝트 UI 구조",
        "3. Streamlit 명령어 사전",
        "4. 설계 패턴",
        "5. 트러블슈팅",
        "6. 정리",
    ]
    nav = st.sidebar.radio("📌 목차", sections, index=0)

    st.sidebar.markdown("---")
    st.sidebar.caption("Tip) 섹션을 바꿔가며 빠르게 확인할 수 있어요.")

    # ---- Section renderers ----
    def section_overview():
        st.header("0. 매뉴얼 개요")
        st.markdown(
            """
이 매뉴얼은 **RAG 기반 정신 건강 정보 지원 챗봇 프로젝트**에서 실제로 사용된 Streamlit 기능만 정리한 문서입니다.

- Streamlit의 전체 기능을 다루지 않습니다.
- **본 프로젝트 UI 구성 · 페이지 이동 · 상태 관리 · 채팅 UX 구현에 사용된 핵심 API만** 설명합니다.
            """
        )

    def section_run():
        st.header("1. 실행 방법")
        st.markdown("엔트리 포인트 파일을 기준으로 다음과 같이 실행합니다.")
        st.code("streamlit run app.py", language="bash")
        st.markdown(
            """
- 멀티페이지 구조는 내부에서 페이지 라우팅을 수행합니다.
- OpenAI API Key 등 환경 변수는 사전에 설정되어 있어야 합니다.
            """
        )

    def section_structure():
        st.header("2. 프로젝트 UI 구조 개요")
        st.markdown("본 프로젝트는 **멀티페이지 Streamlit 앱**이며, 페이지 전환을 다음 방식으로 구성할 수 있습니다.")

        st.subheader("2.1 사이드바 선택 기반 페이지 전환")
        st.code(
            """menu = st.sidebar.selectbox("Menu", ["Intro", "Project 1", "Project 2"])

if menu == "Intro":
    intro.app()
elif menu == "Project 1":
    project1.app()
else:
    project2.app()
""",
            language="python",
        )
        st.markdown(
            """
- `st.sidebar.selectbox()`로 사용자가 페이지를 선택
- 선택값에 따라 조건문으로 페이지 렌더링
- 구조가 단순해서 소규모 프로젝트에 적합
            """
        )

        st.subheader("2.2 MultiPage 클래스 기반 페이지 관리")
        st.code(
            """app = MultiPage()
app.add_page("Intro", intro.app)
app.add_page("Chatbot", chatbot.app)
app.run()
""",
            language="python",
        )
        st.markdown(
            """
- 페이지를 객체 단위로 등록
- 페이지 수가 늘어도 관리가 쉬움
- 서비스 구조에 가까운 방식
            """
        )

    def cmd_entry(title, role, where, snippet, tips=None):
        with st.expander(f"✅ {title}", expanded=False):
            st.markdown(f"**역할:** {role}")
            st.markdown(f"**프로젝트에서의 사용:** {where}")
            st.markdown("**예시 코드:**")
            st.code(snippet, language="python")
            if tips:
                st.markdown("**주의사항 / 팁:**")
                st.markdown(tips)

    def section_commands():
        st.header("3. Streamlit 명령어 사전 (프로젝트 사용 기준)")

        st.subheader("3.1 화면 출력")
        cmd_entry(
            "st.title()",
            "페이지의 최상단 제목 표시",
            "각 페이지 메인 헤더",
            """st.title("Mental Health Support Chatbot")""",
            "- 제목은 페이지당 1회 정도가 가장 깔끔해요.",
        )
        cmd_entry(
            "st.write()",
            "텍스트/리스트/Markdown/수식 등 범용 출력",
            "페이지 설명, 안내문, 결과 출력",
            """st.write("이 챗봇은 신뢰 가능한 정신 건강 정보를 제공합니다.")""",
            "- 타입에 따라 자동 렌더링이 달라져서 편하지만, 레이아웃을 통제하고 싶으면 `st.markdown()`을 같이 써요.",
        )
        cmd_entry(
            "st.markdown()",
            "Markdown 렌더링 + (옵션) HTML/CSS 삽입",
            "헤더 스타일, 채팅 UI CSS",
            """st.markdown(
    "<h3 style='color:#5A5;'>Chat</h3>",
    unsafe_allow_html=True
)""",
            "- `unsafe_allow_html=True`는 강력하지만 HTML/CSS 깨짐/보안 이슈 가능성이 있어요.\n- 내부 데모/프로토타입 용도로 제한 사용 권장.",
        )

        st.subheader("3.2 레이아웃")
        cmd_entry(
            "st.columns()",
            "화면을 가로로 분할하여 컴포넌트 배치",
            "채팅 입력창 + 전송 버튼 같은 UI",
            """col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("질문")
with col2:
    st.button("전송")""",
            "- 비율 배열로 레이아웃 감각적으로 잡기 좋아요.",
        )

        st.subheader("3.3 사이드바 / 페이지 이동")
        cmd_entry(
            "st.sidebar.selectbox()",
            "사이드바에서 항목 선택",
            "메뉴/페이지 전환",
            """menu = st.sidebar.selectbox("Menu", ["Intro", "Project 1", "Project 2"])""",
            "- 페이지가 늘어나면 `MultiPage` 구조로 넘어가는 게 유지보수에 좋아요.",
        )

        st.subheader("3.4 입력 처리")
        cmd_entry(
    "st.text_input()",
    "사용자 텍스트 입력",
    "질문 입력",
    """user_input = st.text_input(
    "질문을 입력하세요",
    placeholder="Enter를 눌러 전송",
    label_visibility="collapsed"
)""",
    '- `label_visibility="collapsed"`로 라벨을 숨기면 화면이 더 깔끔해요.',
)
        cmd_entry(
            "st.form() + st.form_submit_button()",
            "제출 시점(Enter/버튼 클릭)을 기준으로 입력 처리",
            "채팅 UX(입력할 때마다 리렌더링 방지)",
            """with st.form("chat_form"):
    user_input = st.text_input("질문")
    submitted = st.form_submit_button("전송")
if submitted:
    st.write(user_input)""",
            "- 기본 동작은 입력할 때마다 스크립트가 다시 실행되기 때문에, 채팅에는 `form`이 매우 유리해요.",
        )

        st.subheader("3.5 상태 관리")
        cmd_entry(
            "st.session_state",
            "리렌더링 사이에 값/데이터 유지",
            "채팅 히스토리, 사용자 선택값 유지",
            """if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.messages.append({"role": "user", "content": user_input})""",
            "- Streamlit은 상호작용마다 스크립트를 다시 실행하므로 상태 저장이 필수예요.",
        )
        cmd_entry(
            "st.rerun()",
            "상태 변경 후 즉시 화면 갱신",
            "메시지 추가 후 바로 채팅 UI 업데이트",
            """st.session_state.messages.append(new_message)
st.rerun()""",
            "- rerun을 남발하면 UX가 과하게 깜빡일 수 있어요. 필요한 지점에만 사용!",
        )

        st.subheader("3.6 사용자 피드백 (UX)")
        cmd_entry(
            "st.spinner()",
            "처리 중 로딩 표시",
            "RAG 답변 생성 중 표시",
            """with st.spinner("답변 생성 중..."):
    answer = generate_answer()""",
            "- 사용자 입장에서 “멈춘 거 아님”을 알려주는 핵심 UX예요.",
        )
        cmd_entry(
            "st.warning()",
            "경고 메시지 표시",
            "입력값 누락 안내",
            """if not user_input:
    st.warning("질문을 입력해주세요.")""",
        )
        cmd_entry(
            "st.error()",
            "오류/중요 안내 표시",
            "위기 상황 안내 문구 강조",
            """st.error("위기 상황 시 전문 기관에 연락하세요.")""",
            "- 정신건강 서비스 맥락에서는 ‘긴급 안내’를 눈에 띄게 하는 데 좋아요.",
        )

    def section_patterns():
        st.header("4. Streamlit 설계 패턴 (프로젝트 적용)")
        st.subheader("4.1 채팅 UI 패턴")
        st.markdown(
            """
- `st.form` + `st.session_state` 조합으로 **메신저형 UX**를 구현합니다.
- 흐름: **입력(Submit) → 메시지 상태 저장 → 화면 갱신(`st.rerun`)**
            """
        )
        st.code(
            """if "messages" not in st.session_state:
    st.session_state.messages = []

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("질문", label_visibility="collapsed")
    submitted = st.form_submit_button("전송")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

for m in st.session_state.messages:
    st.write(f"{m['role']}: {m['content']}")
""",
            language="python",
        )

        st.subheader("4.2 멀티페이지 확장 패턴")
        st.markdown(
            """
- 초기에는 `sidebar.selectbox`로 빠르게 시작  
- 페이지/기능이 늘어나면 `MultiPage.add_page()` 구조로 확장
            """
        )

    def section_troubleshooting():
        st.header("5. 자주 발생하는 문제 & 해결")
        st.markdown(
            """
**Q1. 입력했는데 화면이 안 바뀐다**  
- `st.session_state` 업데이트 후 `st.rerun()` 호출 여부 확인

**Q2. 입력할 때마다 페이지가 새로 그려져서 UX가 별로다**  
- `st.form()`을 사용해 제출 시점(Enter/버튼 클릭)으로 제어

**Q3. CSS가 깨지거나 레이아웃이 이상하다**  
- `unsafe_allow_html=True` 사용 범위를 점검  
- 브라우저/테마(다크모드)에 따라 CSS가 다르게 보일 수 있음
            """
        )

    def section_wrapup():
        st.header("6. 정리")
        st.markdown(
            """
이 프로젝트에서 Streamlit은 다음 목적에 최적화되어 사용되었습니다.

- **빠른 UI 프로토타이핑**
- **채팅 인터페이스 구성**
- **RAG 결과를 사용자에게 보기 좋게 제공**

프론트엔드 프레임워크 없이도, 비교적 짧은 코드로 **서비스 시연 가능한 수준의 앱**을 구성할 수 있습니다.
            """
        )

    # ---- Render selected section ----
    if nav == "0. 개요":
        section_overview()
    elif nav == "1. 실행 방법":
        section_run()
    elif nav == "2. 프로젝트 UI 구조":
        section_structure()
    elif nav == "3. Streamlit 명령어 사전":
        section_commands()
    elif nav == "4. 설계 패턴":
        section_patterns()
    elif nav == "5. 트러블슈팅":
        section_troubleshooting()
    else:
        section_wrapup()


# 이 파일을 단독 실행해도 페이지가 뜨게 하고 싶으면 아래를 유지하세요.
if __name__ == "__main__":
    app()
