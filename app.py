import streamlit as st
import pandas as pd
import json
import os
import graphviz
from io import BytesIO

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUIZ_JSON = "career_questions.json"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        df = pd.read_csv(USERS_CSV)
        df['your_paths'] = df['your_paths'].apply(lambda x: json.loads(x) if pd.notnull(x) else {})
        return df
    else:
        cols = ['name','email','password','age','gender','location','studying','avatar','your_paths']
        return pd.DataFrame(columns=cols)

def save_users(df):
    df_copy = df.copy()
    df_copy['your_paths'] = df_copy['your_paths'].apply(lambda x: json.dumps(x))
    df_copy.to_csv(USERS_CSV,index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    else:
        return pd.DataFrame(columns=['College','Location','Website','Courses'])

def load_quiz():
    with open(QUIZ_JSON,'r') as f:
        return json.load(f)

# -----------------------------
# USER FUNCTIONS
# -----------------------------
def signup(email,password,name,age,gender,location,studying,avatar_file):
    users_df = load_users()
    if email in users_df.email.values:
        return False, "Email already exists"
    users_df.loc[len(users_df)] = [name,email,password,age,gender,location,studying,avatar_file,{}]
    save_users(users_df)
    return True, "Signup successful"

def login(email,password):
    users_df = load_users()
    user = users_df[(users_df.email==email)&(users_df.password==password)]
    if not user.empty:
        return user.iloc[0]
    return None

# -----------------------------
# QUIZ LOGIC
# -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q, ans in zip(questions, answers):
        if ans in q["options"]:
            for stream, weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream,0)+weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked)>1 else None
    backup = ranked[2][0] if len(ranked)>2 else None
    return major, minor, backup

# -----------------------------
# MAIN UI
# -----------------------------
st.title("🎯 Career Compass")

# Sidebar
menu = ["Home","Quiz","Your Paths","Explore Colleges","Notifications","About Us","Log Out"]
choice = st.sidebar.selectbox("Menu", menu)

# Dummy session_state for login
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# HOME
# -----------------------------
if choice=="Home":
    st.header("Welcome to Career Compass!")
    if st.session_state.user:
        st.success(f"Hello {st.session_state.user['name']}!")
    else:
        st.info("Please log in from the sidebar.")

# -----------------------------
# SIGNUP / LOGIN
# -----------------------------
if st.session_state.user is None:
    st.sidebar.subheader("Login / Signup")
    login_option = st.sidebar.radio("Option",["Login","Sign Up"])

    if login_option=="Login":
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password",type="password")
        if st.sidebar.button("Login"):
            user = login(email,password)
            if user is not None:
                st.session_state.user = user
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")

    else: # Sign Up
        st.sidebar.subheader("Sign Up")
        name = st.sidebar.text_input("Full Name")
        age = st.sidebar.number_input("Age",min_value=10,max_value=100)
        gender = st.sidebar.selectbox("Gender",["Male","Female","Other"])
        location = st.sidebar.text_input("City")
        studying = st.sidebar.text_input("Education / Currently Studying")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password",type="password")
        if st.sidebar.button("Sign Up"):
            # Avatar logic
            if gender=="Male":
                avatar_file = "images/male.png"
            elif gender=="Female":
                avatar_file = "images/female.png"
            else:
                avatar_file = "images/other.png"
            success,msg = signup(email,password,name,age,gender,location,studying,avatar_file)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# -----------------------------
# QUIZ
# -----------------------------
if choice=="Quiz" and st.session_state.user:
    st.header("Career Quiz")
    quiz_data = load_quiz()
    main_questions = quiz_data["main"]
    answers = []

    for i,q in enumerate(main_questions):
        st.subheader(f"Q{i+1}: {q['q']}")
        opt = {k:v['text'] for k,v in q['options'].items()}
        ans = st.radio("",list(opt.values()),key=f"q{i}")
        # Convert selected text back to key
        selected_key = [k for k,v in opt.items() if v==ans][0]
        answers.append(selected_key)

    if st.button("Submit Quiz"):
        main_scores = calculate_scores(main_questions,answers)
        major, minor, backup = recommend(main_scores)
        st.session_state.user['your_paths']["major_stream"] = major
        st.session_state.user['your_paths']["minor_stream"] = minor
        st.session_state.user['your_paths']["backup_stream"] = backup

        # Sub quiz
        if major in quiz_data["sub"]:
            st.info(f"Proceed to {major} specialization")
            sub_questions = quiz_data["sub"][major]
            sub_answers = []
            for i,q in enumerate(sub_questions):
                st.subheader(f"SubQ{i+1}: {q['q']}")
                opt = {k:v['text'] for k,v in q['options'].items()}
                ans = st.radio("",list(opt.values()),key=f"subq{i}")
                selected_key = [k for k,v in opt.items() if v==ans][0]
                sub_answers.append(selected_key)
            if st.button("Submit Sub-Quiz"):
                sub_scores = calculate_scores(sub_questions,sub_answers)
                s_major,s_minor,s_backup = recommend(sub_scores)
                st.session_state.user['your_paths']["major_spec"] = s_major
                st.session_state.user['your_paths']["minor_spec"] = s_minor
                st.session_state.user['your_paths']["backup_spec"] = s_backup
                st.success("Specialization recommendations saved!")
        st.success("Main stream recommendations saved!")

# -----------------------------
# YOUR PATHS
# -----------------------------
if choice=="Your Paths" and st.session_state.user:
    st.header("Your Recommended Career Paths")
    paths = st.session_state.user.get("your_paths",{})
    st.json(paths)

# -----------------------------
# EXPLORE COLLEGES
# -----------------------------
if choice=="Explore Colleges" and st.session_state.user:
    st.header("Explore Colleges in J&K")
    colleges_df = load_colleges()
    if not colleges_df.empty:
        st.dataframe(colleges_df)
    else:
        st.info("College data not available")

# -----------------------------
# NOTIFICATIONS
# -----------------------------
if choice=="Notifications" and st.session_state.user:
    st.header("Notifications")
    st.info("No new notifications")

# -----------------------------
# ABOUT US
# -----------------------------
if choice=="About Us":
    st.header("About Career Compass")
    st.write("This platform helps students find career streams and specializations based on their interests.")

# -----------------------------
# LOG OUT
# -----------------------------
if choice=="Log Out":
    st.session_state.user = None
    st.success("Logged out successfully!")
