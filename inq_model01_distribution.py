import pymysql
import streamlit as st
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL = 'gpt-4.1'

# OpenAI API 설정
client = OpenAI(api_key=OPENAI_API_KEY)

# 초기 프롬프트
initial_prompt = (
    "You are a helpful, supportive chatbot named MathBuddy designed to assist college-level math students in exploring and refining their understanding of mathematical concepts. "
    "Your job is to guide students as they work through problems on their own."
    "Act as a coach, not a solver. Break the problem into manageable parts and guide the student with leading questions."
    "When a student asks a math question, **do not immediately solve it**."
    "DO NOT give full solutions or final answers."
    "Instead, first try to understand how much the student already knows."
    "Ask a few gentle, open-ended questions to assess their thinking."
    "Encourage them to explain their approach or where they got stuck. Examples:\n"
    "- What have you tried so far?\n"
    "- Where are you stuck?\n"
    "- What do you remember about similar problems?\n\n"    
    "Ask helpful questions, break the problem into steps, and suggest strategies."
    "Only offer the next helpful nudge. Let the student do the reasoning."
    "You encourage students to develop their own ideas, attempt problem solving independently, and reflect on their thinking. "
    "Your tone is friendly, clear, and educational. "
    "Use a friendly, encouraging tone. After assessing their understanding, offer a hint or suggestion—"
    "but still do not give the full solution."
    "If students are working on a project or math investigation, start by asking them to describe their math question, goal, and any process or methods they’ve already tried. "
    "Provide specific feedback on strengths and suggestions for improvement based on standard mathematical practices (e.g., clarity of reasoning, appropriate use of definitions, logical structure, completeness). "
   "Guide the student toward discovering the solution on their own. Use questions, hints, and scaffolding to support their thinking, rather than giving full solutions."
    "Work with the student to explore different strategies or perspectives, but leave the solving to them."
    "Encourage productive struggle. Help the student see mistakes as opportunities to learn, not something to avoid with full answers."
    "Always prioritize guiding students to reflect and revise."
    "Explain all mathematical expressions clearly using plain text only. Use parentheses for grouping, fractions like '3/4', powers like 'x^2', and avoid LaTeX or special symbols. Format expressions for readability."
    "Explain math in plain English. Do not use LaTeX, symbols like \(\), or math notation—use only plain text."
    "When the student has completed the necessary work and seems ready to provide an answer (indicated by a confident statement or after sufficient problem-solving effort), ask them for their final answer. Let them know that they can move on to the next phase of reflection or summary by clicking the 'Next' button."
)

# MySQL 저장 함수
def save_to_db(all_data):
    number = st.session_state.get('user_number', '').strip()
    name = st.session_state.get('user_name', '').strip()

    if not number or not name:  # 학번과 이름 확인
        st.error("Please enter your student ID and name.")
        return False  # 저장 실패

    try:
        db = pymysql.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_DATABASE"],
            charset="utf8mb4",  # UTF-8 지원
            autocommit=True  # 자동 커밋 활성화
        )
        cursor = db.cursor()
        now = datetime.now()

        sql = """
        INSERT INTO qna (number, name, chat, time)
        VALUES (%s, %s, %s, %s)
        """
        # all_data를 JSON 문자열로 변환하여 저장
        chat = json.dumps(all_data, ensure_ascii=False)  # 대화 및 피드백 내용 통합

        val = (number, name, chat, now)

        # SQL 실행
        cursor.execute(sql, val)
        cursor.close()
        db.close()
        return True  # 저장 성공
    except pymysql.MySQLError as db_err:
        st.error(f"A database error occurred: {db_err}")
        return False  # 저장 실패
    except Exception as e:
        st.error(f"An unexpected error has occurred: {e}")
        return False  # 저장 실패

# GPT 응답 생성 함수
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": initial_prompt}] + st.session_state["messages"] + [{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content

    # 사용자와 챗봇 대화만 기록
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    return answer

# 페이지 1: 학번 및 이름 입력
def page_1():
    
    # Set page title
    st.set_page_config(page_title="MathBuddy", page_icon="🧮", layout="centered")
    st.title("📚 Welcome to MathBuddy")
    # Display the image
    st.image("20250426_1112_MathMentor App Design_simple_compose_01jssmpambehdrzr9d7ej2h9bf.png",
         caption="Your Study Companion for Math Success 📱",
         width=200)
    st.write("Please enter your student ID and name, then click the 'Next' button.")

    if "user_number" not in st.session_state:
        st.session_state["user_number"] = ""
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    st.session_state["user_number"] = st.text_input("Student ID", value=st.session_state["user_number"])
    st.session_state["user_name"] = st.text_input("Name", value=st.session_state["user_name"])

    st.write(" ")  # Add space to position the button at the bottom properly
    if st.button("Next", key="page1_next_button"):
        if st.session_state["user_number"].strip() == "" or st.session_state["user_name"].strip() == "":
            st.error("Oops! Please make sure to enter both your student ID and name.")
        else:
            st.session_state["step"] = 2
            st.rerun()

# 페이지 2: 사용법 안내
def page_2():
    st.title("MathBuddy: Your Personal AI Calculus Tutor")

    # Step-by-step guide
    st.subheader("How to Use MathBuddy")

    st.write(
       """  
       Welcome to **MathBuddy!** 

        🧠 Here's how to interact with the chatbot:
        1. Start by explaining your math question, problem, or exploration goal.
        2. MathBuddy will give you constructive feedback, suggest improvements, and ask guiding questions.
        3. Ask as many questions as you like to understand the feedback better.
        4. When you feel ready, you can say "I'm ready to move on" and MathBuddy will continue the guidance.

        ✍️ Examples:
        - "Solve and explain this equation step by step: (2x + 3)(x - 1) = 0"
        - “What transformations are applied to f(x) = x² to get f(x) = -2(x - 1)² + 5?”
        - “Factor this expression: x² + 5x + 6”
        - “What’s the domain and range of f(x) = 1 / (x + 2)?”
        - “How do I find the derivative of sin(x²)?”
        - “What is the chain rule and when do I use it?”
        - “Can you explain the concept of a critical point?”

        Please make sure you're ready before moving on. When you're ready, click **Next**.
        
        """)
    
    # 버튼
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Previous"):
            st.session_state["step"] = 1
            st.rerun()

    with col2:
        if st.button("Next", key="page2_next_button"):
            st.session_state["step"] = 3
            st.rerun()

# 페이지 3: GPT와 대화
def page_3():
    st.title("Start Chatting with MathBuddy")
    st.write("""
        ✍️ Describe your math question or idea. Let's work through it together!\n
        🧠 Done with this part? Just scroll down and click **Next** to move on to the reflection.
        """
    )
    # 학번과 이름 확인
    if not st.session_state.get("user_number") or not st.session_state.get("user_name"):
        st.error("Missing Student ID or Name.")
        st.session_state["step"] = 1
        st.rerun()

    # 대화 기록 초기화
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "user_input_temp" not in st.session_state:
        st.session_state["user_input_temp"] = ""

    if "recent_message" not in st.session_state:
        st.session_state["recent_message"] = {"user": "", "assistant": ""}

    # 대화 UI
    user_input = st.text_area(
        "You: ",
        value=st.session_state["user_input_temp"],
        key="user_input",
        on_change=lambda: st.session_state.update({"user_input_temp": st.session_state["user_input"]}),
    )

    if st.button("Send") and user_input.strip():
        # GPT 응답 가져오기
        assistant_response = get_chatgpt_response(user_input)

        # 최근 대화 저장
        st.session_state["recent_message"] = {"user": user_input, "assistant": assistant_response}

        # 사용자 입력을 초기화하고 페이지를 새로고침
        st.session_state["user_input_temp"] = ""
        st.rerun()
    
    # 최근 대화 출력
    st.subheader("📌 Most Recent Exchange")
    if st.session_state["recent_message"]["user"] or st.session_state["recent_message"]["assistant"]:
        st.write(f"**You:** {st.session_state['recent_message']['user']}")
        st.write(f"**MathBuddy:** {st.session_state['recent_message']['assistant']}")
    else:
        st.write("No recent messages yet.")

    # 누적 대화 출력
    st.subheader("📜 Full Chat History")
    if st.session_state["messages"]:
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            elif message["role"] == "assistant":
                st.write(f"**MathBuddy:** {message['content']}")
    else:
        st.write("Start your first message above!")

    col1, col2 = st.columns([1, 1])

    # 이전 버튼
    with col1:
        if st.button("Previous"):
            st.session_state["step"] = 2
            st.rerun()

    # 다음 버튼
    with col2:
        if st.button("Next", key="page3_next_button"):
            st.session_state["step"] = 4
            st.session_state["feedback_saved"] = False  # 피드백 재생성 플래그 초기화
            st.rerun()

# 피드백 저장 함수
def save_feedback_to_db(feedback):
    number = st.session_state.get('user_number', '').strip()
    name = st.session_state.get('user_name', '').strip()

    if not number or not name:  # 학번과 이름 확인
        st.error("Enter your student ID and name.")
        return False  # 저장 실패

    try:
        db = pymysql.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_DATABASE"],
            charset="utf8mb4",  # UTF-8 지원
            autocommit=True  # 자동 커밋 활성화
        )
        cursor = db.cursor()
        now = datetime.now()

        sql = """
        INSERT INTO feedback (number, name, feedback, time)
        VALUES (%s, %s, %s, %s)
        """
        val = (number, name, feedback, now)

        # SQL 실행
        cursor.execute(sql, val)
        cursor.close()
        db.close()
        st.success("Feedback saved.")
        return True  # 저장 성공
    except pymysql.MySQLError as db_err:
        st.error(f"DB 처리 중 오류가 발생했습니다: {db_err}")
        return False  # 저장 실패
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False  # 저장 실패

# 페이지 4: 실험 과정 출력
def page_4():
    st.title("Wrap-Up: Final Reflection")
    
    # 페이지 4로 돌아올 때마다 새로운 피드백 생성
    if not st.session_state.get("feedback_saved", False):
        # 대화 기록을 기반으로 탐구 계획 작성
        chat_history = "\n".join(f"{msg['role']}: {msg['content']}" for msg in st.session_state["messages"])
        prompt = f"This is a conversation between a student and MathBuddy :\n{chat_history}\n\n"
        prompt += "Please summarize the key concepts discussed, note areas of strength, and suggest improvements or study tips."
        # OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        st.session_state["experiment_plan"] = response.choices[0].message.content

    # 피드백 출력
    st.subheader("📋 Feedback Summary")
    st.write(st.session_state["experiment_plan"])

    # 새로운 변수에 대화 내용과 피드백을 통합
    if "all_data" not in st.session_state:
        st.session_state["all_data"] = []

    all_data_to_store = st.session_state["messages"] + [{"role": "assistant", "content": st.session_state["experiment_plan"]}]

    # 중복 저장 방지: 피드백 저장 여부 확인
    if "feedback_saved" not in st.session_state:
        st.session_state["feedback_saved"] = False  # 초기화

    if not st.session_state["feedback_saved"]:
        # 새로운 데이터(all_data_to_store)를 MySQL에 저장
        if save_to_db(all_data_to_store):  # 기존 save_to_db 함수에 통합된 데이터 전달
            st.session_state["feedback_saved"] = True  # 저장 성공 시 플래그 설정
        else:
            st.error("Failed to save conversation. Try again!")

    # 이전 버튼 (페이지 3으로 이동 시 피드백 삭제)
    if st.button("Previous", key="page4_back_button"):
        st.session_state["step"] = 3
        if "experiment_plan" in st.session_state:
            del st.session_state["experiment_plan"]  # 피드백 삭제
        st.session_state["feedback_saved"] = False  # 피드백 재생성 플래그 초기화
        st.rerun()

# 메인 로직
if "step" not in st.session_state:
    st.session_state["step"] = 1

if st.session_state["step"] == 1:
    page_1()
elif st.session_state["step"] == 2:
    page_2()
elif st.session_state["step"] == 3:
    page_3()
elif st.session_state["step"] == 4:
    page_4()
