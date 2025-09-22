import streamlit as st
import pandas as pd
import json
import os
from graphviz import Digraph

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUESTIONS_JSON = "career_questions.json"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    else:
        df = pd.DataFrame(columns=["username","password","fullname","gender","avatar"])
        df.to_csv(USERS_CSV, index=False)
        return df

def load_colleges():
    return pd.read_csv(COLLEGES_CSV)

def load_questions():
    with open(QUESTIONS_JSON,"r") as f:
        return json.load(f)

users_df = load_users()
colleges_df = load_colleges()
questions_data = load_questions()

# -----------------------------
# AUTHENTICATION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def login(username, password):
    user = users_df[(users_df.username==username) & (users_df.password==password)]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

def signup(username, password, fullname, gender):
    global users_df
    # Ensure required columns exist
    required_cols = ["username","password","fullname","gender","avatar"]
    for col in required_cols:
        if col not in users_df.columns:
            users_df[col] = ""

    # Check if username exists
    if username in users_df["username"].values:
        return False

    # Assign avatar based on gender
    if gender=="Male":
        avatar_file="male.png"
    elif gender=="Female":
        avatar_file="female.png"
    else:
        avatar_file="other.png"

    # Append new user as a dictionary
    new_row = {
        "username": username,
        "password": password,
        "fullname": fullname,
        "gender": gender,
        "avatar": avatar_file
    }

    users_df = pd.concat([users_df, pd.DataFrame([new_row])], ignore_index=True)
    users_df.to_csv(USERS_CSV,index=False)
    return True


# -----------------------------
# SIDEBAR
# -----------------------------
def sidebar():
    if st.session_state.logged_in:
        st.sidebar.image(os.path.join(AVATAR_FOLDER, st.session_state.user["avatar"]), width=100)
        st.sidebar.write(f"Hello, {st.session_state.user['fullname']}")
        menu = st.sidebar.radio("Navigation", ["Home","Quiz","Your Paths","Explore","Notifications","About Us","Logout"])
        return menu
    return None

menu = sidebar()

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q, ans in zip(questions, answers):
        if ans in q["options"]:
            for stream, weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream,0) + weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked)>1 else None
    backup = ranked[2][0] if len(ranked)>2 else None
    return major, minor, backup

# Canonical course mapping
COURSE_SYNONYMS = {
    "Software": ["Computer Science","Software Engineering","CSE"],
    "AI": ["Artificial Intelligence","Machine Learning","AI & ML"],
    "Mechanical": ["Mechanical Engineering"],
    "CivilArch": ["Civil Engineering","Architecture"],
    "Electrical": ["Electrical Engineering","EEE"],
    "Biology": ["Biotechnology","Biology"],
    "Physics": ["Physics"],
    "Chemistry": ["Chemistry"],
    "Medical": ["MBBS","Nursing","Paramedical","Nutrition"],
    "Arts": ["Design","Fine Arts","Performing Arts"],
    "Commerce": ["BBA","BCom","Economics"]
}

def map_course_to_colleges(course):
    synonyms = COURSE_SYNONYMS.get(course,[course])
    matched = colleges_df[colleges_df['Courses'].apply(lambda x: any(s.lower() in x.lower() for s in synonyms))]
    return matched

def show_roadmap(major, sub_major):
    dot = Digraph(comment='Career Roadmap', format='png')
    dot.node('Start', 'You')
    dot.node('Stream', major)
    dot.node('Specialization', sub_major)
    
    # Courses offered
    colleges = map_course_to_colleges(sub_major)
    for idx,row in colleges.iterrows():
        dot.node(f"{row['College']}", f"{row['College']}\n({row['Location']})")
        dot.edge('Specialization', f"{row['College']}")
    
    dot.edge('Start','Stream')
    dot.edge('Stream','Specialization')
    st.graphviz_chart(dot)

# -----------------------------
# MAIN PAGES
# -----------------------------
if not st.session_state.logged_in:
    st.title("🎯 Career Compass")
    tab1, tab2 = st.tabs(["Login","Signup"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login(username,password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Welcome, {user['fullname']}!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials!")
    with tab2:
        new_username = st.text_input("New Username", key="new_user")
        new_password = st.text_input("Password", type="password", key="new_pass")
        fullname = st.text_input("Full Name")
        gender = st.radio("Gender", ["Male","Female","Other"])
        if st.button("Signup"):
            success = signup(new_username,new_password,fullname,gender)
            if success:
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists!")
else:
    if menu=="Home":
        st.title("🏠 Home")
        st.write("Welcome to Career Compass!")
    elif menu=="Quiz":
        st.title("📝 Career Quiz")
        answers=[]
        for i,q in enumerate(questions_data["main"]):
            st.write(f"**Q{i+1}: {q['q']}**")
            opt = {k:v["text"] for k,v in q["options"].items()}
            choice = st.radio("Choose one:", list(opt.values()), key=f"main_{i}")
            # map back to option letter
            for k,v in opt.items():
                if v==choice:
                    answers.append(k)
        if st.button("Submit Quiz"):
            main_scores = calculate_scores(questions_data["main"],answers)
            major, minor, backup = recommend(main_scores)
            st.session_state.quiz_result = {"major":major,"minor":minor,"backup":backup}
            st.success(f"Your major: {major}, minor: {minor}, backup: {backup}")
    elif menu=="Your Paths":
        st.title("📊 Your Career Roadmap")
        if "quiz_result" in st.session_state:
            major = st.session_state.quiz_result["major"]
            # Run sub-quiz if exists
            if major in questions_data["sub"]:
                sub_answers=[]
                for i,q in enumerate(questions_data["sub"][major]):
                    st.write(f"**Q{i+1}: {q['q']}**")
                    opt = {k:v["text"] for k,v in q["options"].items()}
                    choice = st.radio("Choose one:", list(opt.values()), key=f"sub_{i}")
                    for k,v in opt.items():
                        if v==choice:
                            sub_answers.append(k)
                if st.button("Submit Sub-Quiz"):
                    sub_scores = calculate_scores(questions_data["sub"][major],sub_answers)
                    sub_major, sub_minor, sub_backup = recommend(sub_scores)
                    st.session_state.sub_result = {"major":sub_major,"minor":sub_minor,"backup":sub_backup}
                    st.success(f"Specialization: {sub_major}")
                    show_roadmap(major, sub_major)
            else:
                st.warning("No specialization available for your stream.")
        else:
            st.info("Please complete the main quiz first.")
    elif menu=="Explore":
        st.title("🏫 College Recommendations")
        if "quiz_result" in st.session_state:
            major = st.session_state.quiz_result["major"]
            sub_major = st.session_state.sub_result["major"] if "sub_result" in st.session_state else major
            st.write(f"**Based on your career path: {sub_major}**")
            matched_colleges = map_course_to_colleges(sub_major)
            if not matched_colleges.empty:
                st.dataframe(matched_colleges[["College","Location","Website","Courses"]])
            else:
                st.info("No colleges found for this course.")
        else:
            st.info("Complete quiz first.")
    elif menu=="Notifications":
        st.title("🔔 Notifications")
        st.info("No new notifications.")
    elif menu=="About Us":
        st.title("ℹ️ About Us")
        st.write("Career Compass helps you discover your ideal career path and colleges!")
    elif menu=="Logout":
        st.session_state.logged_in=False
        st.session_state.user=None
        st.experimental_rerun()
