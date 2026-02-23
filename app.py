import streamlit as st
from page import project1 as p1
from page import project2 as p2
from page import intro
from page import chatbot as rag   # ✅ 추가

st.title('Project')

item_list = ['item0','item1', 'item2', 'item3']  # ✅ item3 추가

item_labels = {
    'item0':'개발환경구축',
    'item1':'스트림릿',
    'item2':'Diagram',
    'item3':'RAGChatbot'   # ✅ 추가
}

FIL = lambda x : item_labels[x]
item = st.sidebar.selectbox('항목을 골라요.',  item_list, format_func = FIL )

if item == 'item1': # project1.py 파일 불러오기 (Streamlit 매뉴얼)
	p1.app()
elif item == 'item2': # project2.py 파일 불러오기 (수행한 프로젝트의 Data Flow Diagram을 작성)
	p2.app()
elif item == 'item0': # intro.py 파일 불러오기 (개발 환경을 구축한 차례에 따라 매뉴얼을 작성)
	intro.app()
elif item == 'item3':          # ✅ 추가
    rag.app()