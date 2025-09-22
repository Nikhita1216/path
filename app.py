import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import graphviz

# ----------------------------- CONFIG -----------------------------
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUIZ_FILE = "career_questions.json"

# ----------------------------- SESSION STATE -----------------------------
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None
if "temp_signup" not in st.session_state:
    st.session_state.temp_signup = {}

# ----------------------------- LOAD DATA -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        df = pd.read_csv(USERS_CSV)
        required_cols = ["email","password","name","age","gender","city","state","education","avatar","your_paths"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        df = pd.DataFrame(columns=["email","password","name","age","gender","city","state","education","avatar","your_paths"])
        df.to_csv(USERS_CSV,index=False)
        return df

def save_users(df):
    df.to_csv(USERS_CSV,index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    else:
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

# ----------------------------- AUTH -----------------------------
def login(email,password):
    df = load_users()
    if email in df["email"].values:
        row = df[df["email"]==email].iloc[0]
        if row["password"]==password:
            return row.to_dict()
    return None

def signup(email, password, name, age, gender, city, state, education, avatar_file=None):
    df = load_users()
    if email in df["email"].values:
        return False
    if avatar_file is None:
        # assign avatar based on gender
        if gender=="Male":
            avatar_file = os.path.join(AVATAR_FOLDER,"avatar2.png")
        elif gender=="Female":
            avatar_file = os.path.join(AVATAR_FOLDER,"avatar1.png")
        else:
            avatar_file = os.path.join(AVATAR_FOLDER,"avatar3.png")
    new_row = {
        "email": email,
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
    save_users(df)
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

# ----------------------------- LOGIN / SIGNUP PAGE -----------------------------
def login_page():
    st.title("🔐 Login to Career Compass")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            user = login(email,password)
            if user:
                st.session_state.login=True
                st.session_state.user=user
                st.success(f"Welcome {user['name']}!")
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        name = st.text_input("Full Name", key="signup_name")
        age = st.number_input("Age", min_value=10, max_value=100, step=1, key="signup_age")
        gender = st.selectbox("Gender", ["Select","Male","Female","Other"], key="signup_gender")
        
        # Show avatar selection only after gender is chosen
        chosen_avatar = None
        if gender != "Select":
            avatars = [os.path.join(AVATAR_FOLDER, f) for f in os.listdir(AVATAR_FOLDER) if f.endswith(".png")]
            chosen_avatar = st.radio("Choose an avatar", avatars, format_func=lambda x: os.path.basename(x))
        
        city = st.text_input("City", key="signup_city")
        state = st.text_input("State", key="signup_state")
        education = st.text_input("Education Qualification", key="signup_edu")
        
        if st.button("Sign Up"):
            if gender=="Select":
                st.error("Please select a gender first!")
            else:
                success = signup(email,password,name,age,gender,city,state,education,chosen_avatar)
                if success:
                    st.success("Signup successful! Please login.")
                else:
                    st.error("Email already exists.")

# ----------------------------- MAIN -----------------------------
if not st.session_state.login:
    login_page()
else:
    menu = st.sidebar.selectbox("Menu", ["Home","Quiz","Your Paths","Explore","Notifications","About Us","Logout"])

    if menu=="Home":
        st.title("🎯 Career Compass")
        st.success(f"Logged in as {st.session_state.user['name']} ({st.session_state.user['education']})")
        st.image(st.session_state.user['avatar'], width=120)

    elif menu=="Quiz":
        st.title("📝 Career Quiz")
        answers = []
        with st.form("quiz_form"):
            for i,q in enumerate(quiz_data["main"]):
                st.write(f"**Q{i+1}: {q['q']}**")
                ans = st.radio("Choose answer", [opt["text"] for opt in q["options"].values()], key=f"main_{i}")
                answers.append(ans)
            submitted = st.form_submit_button("Submit Quiz")
            if submitted:
                main_scores = calculate_scores(quiz_data["main"],answers)
                major, minor, backup = recommend(main_scores)
                st.success(f"Major: {major}, Minor: {minor}, Backup: {backup}")

    elif menu=="Your Paths":
        st.title("📈 Your Career Paths")
        st.write(st.session_state.user.get("your_paths","No paths saved yet."))

    elif menu=="Explore":
        st.title("🏫 College Recommendations")
        st.dataframe(colleges_df)

    elif menu=="Notifications":
        st.title("🔔 Notifications")
        st.info("No new notifications.")

    elif menu=="About Us":
        st.title("ℹ️ About Us")
        st.write("This app helps students discover their career paths and recommended colleges in J&K.")

    elif menu=="Logout":
        st.session_state.login=False
        st.session_state.user=None
        st.success("Logged out successfully.")
