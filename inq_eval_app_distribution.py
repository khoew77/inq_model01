import streamlit as st
import pymysql
import json

# OpenAI API 키 설정
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# MySQL 연결 함수
def connect_to_db():
    return pymysql.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_DATABASE"],
        charset='utf8mb4'
    )

# 모든 레코드 가져오기 함수
def fetch_records():
    try:
        db = connect_to_db()
        cursor = db.cursor()
        query = """
        SELECT id, number, name, time 
        FROM qna
        ORDER BY time
        """
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        db.close()
        return records
    except pymysql.MySQLError as e:
        st.error(f"Error: A database error has occurred.: {e}")
        return []

# 특정 ID의 레코드 가져오기 함수
def fetch_record_by_id(record_id):
    try:
        db = connect_to_db()
        cursor = db.cursor()
        cursor.execute("SELECT chat FROM qna WHERE id = %s", (record_id,))
        record = cursor.fetchone()
        cursor.close()
        db.close()
        return record
    except pymysql.MySQLError as e:
        st.error(f"Error: A database error has occurred.: {e}")
        return None

# Streamlit 애플리케이션
st.title("Student AI Usage History (For Teachers)")

# 비밀번호 입력
password = st.text_input("Please enter your password", type="password")

if password == st.secrets["PASSWORD"]:  # 환경 변수에 저장된 비밀번호와 비교
    # 저장된 레코드 불러오기
    records = fetch_records()

    if records:
        # 레코드 선택
        record_options = [f"{record[1]} ({record[2]}) - {record[3]}" for record in records]
        selected_record = st.selectbox("Please select a record.:", record_options)

        # 선택된 레코드 ID 추출
        selected_record_id = records[record_options.index(selected_record)][0]

        # 선택된 학생의 대화 기록 불러오기
        record = fetch_record_by_id(selected_record_id)
        if record and record[0]:  # 대화 기록이 있는지 확인
            try:
                chat = json.loads(record[0])  # JSON 디코딩
                st.write("### Student Chat History")
                for message in chat:
                    if message["role"] == "user":
                        st.write(f"**You:** {message['content']}")
                    elif message["role"] == "assistant":
                        st.write(f"**MathMentor:** {message['content']}")
            except json.JSONDecodeError:
                st.error("Failed to load chat history. The JSON format is invalid.")
        else:
            st.warning("No chat history found for the selected record.")
    else:
        st.warning("No records stored in the database.")
else:
    st.error("The password is incorrect.")
