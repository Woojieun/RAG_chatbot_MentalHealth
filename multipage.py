# Streamlit 라이브러리를 불러온다.
# 이 파일에서 사이드바(selectbox)를 만들기 위해 필요하다.
import streamlit as st

# MultiPage라는 클래스를 정의한다.
# 이 클래스의 역할은 "여러 페이지를 관리하고 전환"하는 것이다.
class MultiPage:
    # 클래스가 생성될 때 자동으로 실행되는 초기화 함수
    # MultiPage()를 호출하면 가장 먼저 실행된다.
    def __init__(self) -> None:
        # self.pages는 페이지 정보를 저장할 리스트
        # 각 페이지는 딕셔너리 형태로 저장된다.
        # 예: {'title': '개발환경구축', 'function': intro.app}
        self.pages = []
        
    # 페이지를 하나 추가하는 메서드
    # title: 사이드바에 표시될 페이지 이름 (문자열)
    # func: 해당 페이지를 그리는 함수 (보통 app 함수)
    def add_page(self, title, func) -> None:
        # pages 리스트에 딕셔너리 하나를 추가한다.
        # func()가 아니라 func 자체를 저장하는 것이 중요하다.
        # (지금 실행하지 않고, 나중에 실행하기 위해서)
        self.pages.append({'title':title, 'function':func})
        
    # 실제로 멀티페이지 앱을 실행하는 메서드
    # 사이드바 UI를 만들고, 선택된 페이지를 실행한다.
    def run(self):
        # Streamlit 사이드바에 selectbox(드롭다운 메뉴)를 만든다.
        # '메뉴'는 selectbox 위에 표시되는 라벨 텍스트
        
        # self.pages 리스트가 선택지로 들어간다.
        # 하지만 리스트 안의 값은 딕셔너리이므로,
        # 그대로 표시하면 복잡하게 보인다.
        page = st.sidebar.selectbox('메뉴', self.pages,
                                    # format_func는 "화면에 어떻게 보여줄지"를 정하는 함수
                                    # 각 원소(page)는 딕셔너리이므로
                                    # page['title'] 값만 꺼내서 보여주도록 한다.
                                    format_func=lambda page:page['title'])
        # selectbox에서 선택된 값은
        # self.pages 안에 있던 딕셔너리 하나다.
        
        # page['function']에는 실행할 함수(app)가 들어 있다.
        # 뒤에 ()를 붙여서 실제로 그 함수를 실행한다.
        page['function']()
