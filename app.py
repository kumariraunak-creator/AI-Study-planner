import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------- DARK MODE ----------------
st.markdown("""
<style>
body {background-color: #0E1117; color: white;}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS study(username TEXT, subject TEXT, hours INTEGER)")

# ---------------- HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- AUTH ----------------
def add_user(username, password):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        return False
    c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
    conn.commit()
    return True

def login_user(username, password):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone()
    if data:
        return data[0] == hash_password(password)
    return False

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- MENU ----------------
menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

# ---------------- SIGNUP ----------------
if menu == "Signup":
    st.title("📝 Signup")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        if add_user(user, password):
            st.success("Account created ✅")
        else:
            st.error("User already exists ❌")

# ---------------- LOGIN ----------------
elif menu == "Login":
    st.title("🔐 Login")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(user, password):
            st.session_state.logged_in = True
            st.session_state.username = user
            st.success("Login successful ✅")
        else:
            st.error("Invalid credentials ❌")

# ---------------- STOP ----------------
if not st.session_state.logged_in:
    st.stop()

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# ---------------- MAIN APP ----------------
st.title("📚 AI Study Planner")
st.subheader(f"Welcome {st.session_state.username} 👋")

subjects = st.text_input("Subjects (comma separated)")
hours = st.slider("Study hours per day", 1, 10, 3)

if st.button("Generate Plan"):
    if subjects:
        subject_list = [s.strip() for s in subjects.split(",")]
        data = []

        st.write("### 📅 Study Plan")
        for sub in subject_list:
            h = hours // len(subject_list)
            st.write(f"{sub} → {h} hrs")
            data.append((st.session_state.username, sub, h))

        c.executemany("INSERT INTO study VALUES (?, ?, ?)", data)
        conn.commit()

# ---------------- DASHBOARD ----------------
st.subheader("📊 Dashboard")

c.execute("SELECT subject, hours FROM study WHERE username=?", (st.session_state.username,))
rows = c.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["Subject", "Hours"])
    st.dataframe(df)

    fig, ax = plt.subplots()
    df.groupby("Subject").sum().plot(kind="bar", ax=ax)
    st.pyplot(fig)
else:
    st.info("No data yet")

# ---------------- ML PREDICTION ----------------
st.subheader("🧠 Smart Prediction")

def predict(days):
    X = np.array([[5],[10],[15],[20]])
    y = np.array([6,4,3,2])
    model = LinearRegression()
    model.fit(X,y)
    return model.predict([[days]])[0]

days = st.slider("Days left", 1, 30)

if st.button("Predict Study Hours"):
    st.success(f"{round(predict(days),2)} hrs/day")

# ---------------- CHATBOT ----------------
st.subheader("🤖 Chatbot")

msg = st.text_input("Ask something")

def chatbot(text):
    if "study" in text:
        return "Focus on important subjects 📚"
    elif "time" in text:
        return "Make a proper timetable ⏰"
    else:
        return "Keep learning 🚀"

if st.button("Ask"):
    st.write(chatbot(msg))