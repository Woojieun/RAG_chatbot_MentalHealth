# Streamlit(웹앱) 라이브러리를 불러온다.
# st.write(), st.sidebar.selectbox() 같은 Streamlit 기능을 쓰기 위해 필요함.
import streamlit as st

# multipage.py 파일 안에 정의된 MultiPage 클래스를 가져온다.
# MultiPage는 "페이지 목록을 저장하고" "사이드바에서 페이지 선택"을 만들어주는
# 간단한 라우터(페이지 전환기) 역할을 한다.
from multipage import MultiPage

# page 폴더 안에 있는 intro.py 모듈을 가져온다.
# intro.py 안에는 보통 app() 함수가 있고,
# 그 app() 함수가 intro 페이지 화면을 그리는 역할을 함.
from page import intro

# page 폴더 안에 있는 project1.py 모듈을 가져온다.
# as p1 은 별명을 붙인 것.
# 즉, project1.app() 대신 p1.app()으로 편하게 부르려고 쓰는 방식.
from page import project1 as p1

# page 폴더 안에 있는 project2.py 모듈을 가져온다.
# 별명을 p2 로 붙여서 p2.app()으로 호출할 수 있게 함.
from page import project2 as p2

from page import chatbot as rag # ✅ 추가


# MultiPage 클래스의 인스턴스(객체)를 생성한다.
# app 변수는 이제 "여러 페이지를 등록(add_page)하고"
# "선택된 페이지를 실행(run)하는" 역할을 담당한다.
app = MultiPage()


# one_one_two 변수에는 LaTeX 수식 문자열이 들어있다.
# r''' ... ''' : raw string(원시 문자열)로 선언해서
# 백슬래시(\) 같은 문자를 이스케이프 처리하지 않고 그대로 쓸 수 있게 함.
# Streamlit은 $$ ... $$ 형태의 LaTeX를 화면에 수식으로 렌더링해준다.
one_one_two = r'''$${\vdash}:.(\exists x,y).\alpha=\iota`x.\beta=\iota`y.\supset:\alpha\cup\beta\in2.\equiv.\alpha\cap\beta=\Lambda$$'''


# st.write()는 Streamlit 화면에 텍스트/마크다운/수식 등을 출력한다.
# 여기서는 LaTeX 문자열(one_one_two)을 화면에 출력하여
# 수식이 렌더링되도록 한다.
st.write(one_one_two)


# 이제 멀티페이지에 "페이지 하나"를 등록한다.
# app.add_page(페이지제목, 실행함수)
#
# - '개발환경구축' : 사이드바 메뉴에 보일 이름(제목)
# - intro.app      : intro.py 안에 정의된 app() 함수를 실행하겠다는 뜻
#
# 즉, 사용자가 사이드바에서 '개발환경구축'을 선택하면 intro.app()이 실행되고,
# 그 함수 안에서 st.write(...) 등을 통해 화면을 그리게 된다.
app.add_page('개발환경구축', intro.app)


# 두 번째 페이지 등록
# - '스트림릿' 을 선택하면 p1.app() 실행
# (project1.py의 app() 함수)
app.add_page('스트림릿', p1.app)


# 세 번째 페이지 등록
# - 'Diagram' 을 선택하면 p2.app() 실행
# (project2.py의 app() 함수)
app.add_page('Diagram', p2.app)

app.add_page('RAGChatbot', rag.app)  # ✅ 추가


# 멀티페이지 실행(런칭)
# app.run()은 MultiPage 클래스의 run() 메서드를 호출하는데,
# multipage.py를 보면 다음을 한다:
# 1) st.sidebar.selectbox()로 등록된 페이지들 중 하나를 고르게 하고
# 2) 선택된 페이지 딕셔너리에서 'function'을 꺼내 실행한다.
#
# 결과적으로:
# - 사이드바에 메뉴가 뜨고
# - 유저가 고른 페이지의 app() 함수가 실행되어
# - 해당 페이지 화면이 표시된다.
app.run()

'''
이 코드가 “전체적으로” 하는 일 (요약)

MultiPage() 객체를 만든다

add_page()로 페이지 목록(제목 + 함수) 을 등록한다

run()을 호출하면:

사이드바에서 페이지를 고르는 selectbox가 나오고

고른 페이지의 app() 함수가 실행되면서 화면이 바뀐다

'''