import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import graphviz

# ----------------------------- CONFIG -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide", page_icon="🎯")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUIZ_FILE = "career_questions.json"

# Ensure session_state variables
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None

# ----------------------------- LOAD DATA -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        df = pd.read_csv(USERS_CSV)
        # Ensure all required columns exist
        required_cols = ["username","password","name","age","gender","city","state","education","avatar","your_paths"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        df = pd.DataFrame(columns=["username","password","name","age","gender","city","state","education","avatar","your_paths"])
        df.to_csv(USERS_CSV,index=False)
        return df


def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    else:
        # Sample placeholder
        df = pd.DataFrame({
            "College":["SKUAST-Kashmir","GCET Jammu"],
            "Location":["Srinagar","Jammu"],
            "Website":["https://www.skuastkashmir.ac.in","https://gcetjammu.ac.in"],
            "Courses":["Engineering,Science","Commerce,Arts,Engineering"]
        })
        df.to_csv(COLLEGES_CSV,index=False)
        return df

def load_quiz():
    with open(QUIZ_FILE,"r") as f:
        return json.load(f)

users_df = load_users()
colleges_df = load_colleges()
quiz_data = load_quiz()

# ----------------------------- AUTH LOGIC -----------------------------
def login(username,password):
    df = load_users()
    if username in df.username.values:
        row = df[df.username==username].iloc[0]
        if row.password==password:
            return row.to_dict()
    return None

def signup(username, password, name, age, gender, city, state, education):
    df = load_users()
    # Use df["username"] to avoid AttributeError
    if "username" in df.columns and username in df["username"].values:
        return False
    # assign avatar based on gender
    if gender=="Male":
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar2.png")
    elif gender=="Female":
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar1.png")
    else:
        avatar_file = os.path.join(AVATAR_FOLDER,"avatar3.png")
    
    new_row = {
        "username": username,
        "password": password,
        "name": name,
        "age": age,
        "gender": gender,
        "city": city,
        "state": state,
        "education": education,
        "avatar": avatar_file,
        "your_paths": ""
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    return True


# ----------------------------- QUIZ LOGIC -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q, ans in zip(questions, answers):
        if ans in q["options"]:
            for stream, weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream,0)+weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked)>1 else None
    backup = ranked[2][0] if len(ranked)>2 else None
    return major, minor, backup

# ----------------------------- SIDEBAR -----------------------------
menu = st.sidebar.selectbox("Menu", ["Home","Quiz","Your Paths","Explore","Notifications","About Us","Logout"])

# ----------------------------- HOME -----------------------------
if menu=="Home":
    st.title("🎯 Career Compass")
    if not st.session_state.login:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted:
                user = login(username,password)
                if user:
                    st.session_state.login=True
                    st.session_state.user=user
                    st.success(f"Welcome {user['name']}!")
                else:
                    st.error("Invalid credentials")
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_user")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            name = st.text_input("Full Name", key="signup_name")
            age = st.number_input("Age", min_value=10, max_value=100, step=1, key="signup_age")
            gender = st.selectbox("Gender", ["Male","Female","Other"], key="signup_gender")
            city = st.text_input("City", key="signup_city")
            state = st.text_input("State", key="signup_state")
            education = st.text_input("Education Qualification", key="signup_edu")
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                success = signup(new_username,new_password,name,age,gender,city,state,education)
                if success:
                    st.success("Signup successful! Please login.")
                else:
                    st.error("Username already exists.")
    else:
        st.success(f"Logged in as {st.session_state.user['name']} ({st.session_state.user['education']})")
        st.image(st.session_state.user['avatar'], width=120)

# ----------------------------- QUIZ -----------------------------
elif menu=="Quiz" and st.session_state.login:
    st.title("📝 Career Quiz")
    answers = []
    with st.form("quiz_form"):
        for i,q in enumerate(quiz_data["main"]):
            st.write(f"**Q{i+1}: {q['q']}**")
            for key,opt in q["options"].items():
                st.radio(opt["text"], ["Select"], key=f"main_{i}_{key}")  # ensure unique keys
            ans = st.selectbox("Choose answer", options=list(q["options"].keys()), key=f"main_select_{i}")
            answers.append(ans)
        submitted = st.form_submit_button("Submit Quiz")
        if submitted:
            main_scores = calculate_scores(quiz_data["main"],answers)
            major, minor, backup = recommend(main_scores)
            st.success(f"Major: {major}, Minor: {minor}, Backup: {backup}")

            # Sub quiz
            if major in quiz_data["sub"]:
                st.subheader(f"{major} Specialization")
                sub_answers=[]
                for i,q in enumerate(quiz_data["sub"][major]):
                    st.write(f"**Q{i+1}: {q['q']}**")
                    for key,opt in q["options"].items():
                        st.radio(opt["text"], ["Select"], key=f"sub_{i}_{key}")
                    ans = st.selectbox("Choose answer", options=list(q["options"].keys()), key=f"sub_select_{i}")
                    sub_answers.append(ans)
                sub_submitted = st.form_submit_button("Submit Specialization")
                if sub_submitted:
                    sub_scores = calculate_scores(quiz_data["sub"][major],sub_answers)
                    sub_major, sub_minor, sub_backup = recommend(sub_scores)
                    st.success(f"Specialization Major: {sub_major}, Minor: {sub_minor}, Backup: {sub_backup}")

# ----------------------------- YOUR PATHS -----------------------------
elif menu=="Your Paths" and st.session_state.login:
    st.title("📈 Your Career Paths")
    user_paths = st.session_state.user.get("your_paths","None")
    st.write(user_paths if user_paths else "No paths saved yet.")

# ----------------------------- EXPLORE -----------------------------
elif menu=="Explore" and st.session_state.login:
    st.title("🏫 College Recommendations")
    st.dataframe(colleges_df)

# ----------------------------- NOTIFICATIONS -----------------------------
elif menu=="Notifications":
    st.title("🔔 Notifications")
    st.info("No new notifications.")

# ----------------------------- ABOUT US -----------------------------
elif menu=="About Us":
    st.title("ℹ️ About Us")
    st.write("This app helps students discover their career paths and recommended colleges in J&K.")

# ----------------------------- LOGOUT -----------------------------
elif menu=="Logout":
    st.session_state.login=False
    st.session_state.user=None
    st.success("Logged out successfully.")
