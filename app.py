import streamlit as st
import pandas as pd
import json
import os

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
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
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
    if os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE,"r") as f:
            return json.load(f)
    else:
        return {"main": []}

users_df = load_users()
colleges_df = load_colleges()
quiz_data = load_quiz()

# ----------------------------- AUTH FUNCTIONS -----------------------------
def login(email,password):
    df = load_users()
    if email in df["email"].values:
        row = df[df["email"]==email].iloc[0]
        if row["password"]==password:
            return row.to_dict()
    return None

def signup(email, password, name, age, gender, city, state, education):
    df = load_users()
    if email in df["email"].values:
        return False
    # Default avatar based on gender
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

# ----------------------------- QUIZ FUNCTIONS -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q_key, ans in zip(sorted(questions.keys()), answers):
        question = questions[q_key]
        if ans in question["options"]:
            for stream, weight in question["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream, 0) + weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked) > 1 else None
    backup = ranked[2][0] if len(ranked) > 2 else None
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
                st.session_state.page="home"
                st.success(f"Welcome {user['name']}!")
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        name = st.text_input("Full Name", key="signup_name")
        age = st.number_input("Age", min_value=10, max_value=100, step=1, key="signup_age")
        gender = st.selectbox("Gender", ["Select","Male","Female","Other"], key="signup_gender")
        city = st.text_input("City", key="signup_city")
        state = st.text_input("State", key="signup_state")
        education = st.text_input("Education Qualification", key="signup_edu")

        if st.button("Sign Up"):
            if gender=="Select":
                st.error("Please select a gender first!")
            else:
                success = signup(email,password,name,age,gender,city,state,education)
                if success:
                    st.success("Signup successful! Please login.")
                else:
                    st.error("Email already exists.")

# ----------------------------- HOME PAGE -----------------------------
def home_page():
    # Ensure user exists
    if st.session_state.user is not None:
        avatar_path = st.session_state.user.get("avatar")
        if not avatar_path or not os.path.exists(avatar_path):
            avatar_path = os.path.join(AVATAR_FOLDER, "avatar3.png")
        st.sidebar.image(avatar_path, width=80)
        st.sidebar.title(f"Welcome, {st.session_state.user['name']}")
    else:
        st.sidebar.image(os.path.join(AVATAR_FOLDER, "avatar3.png"), width=80)
        st.sidebar.title("Welcome, Guest")

    menu = st.sidebar.radio(
        "📍 Menu", ["Profile","Home","Quiz","Your Paths","Explore","Notifications","About Us","Logout"]
    )
    if menu=="Home":
        st.title("🧭 Career Compass")
        st.subheader("Your personalized guide to career paths, colleges, and opportunities.")
    elif menu == "Profile":
        st.subheader("👤 Edit Profile")
        if st.session_state.user:
            user = st.session_state.user

            # Editable fields
            name = st.text_input("Full Name", user.get("name", ""))
            age = st.number_input("Age", min_value=10, max_value=100, value=int(user.get("age", 18)))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                   index=["Male","Female","Other"].index(user.get("gender","Other")))
            city = st.text_input("City", user.get("city", ""))
            state = st.text_input("State", user.get("state", ""))
            education = st.text_input("Education Qualification", user.get("education", ""))

            # Avatar update only after gender chosen
            avatar = st.file_uploader("Upload Avatar", type=["png","jpg","jpeg"])
            if avatar:
                avatar_path = os.path.join(AVATAR_FOLDER, avatar.name)
                with open(avatar_path, "wb") as f:
                    f.write(avatar.getbuffer())
                user["avatar"] = avatar_path

            if st.button("💾 Save Profile"):
                user.update({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "city": city,
                    "state": state,
                    "education": education
                })
                save_user_data(st.session_state.user["email"], user)  # <-- update CSV
                st.success("Profile updated successfully!")
    

    elif menu=="Quiz":
        quiz_page()

    elif menu=="Your Paths":
        st.title("📈 Your Career Paths")
        user_paths = st.session_state.user.get("your_paths","")
        if user_paths:
            st.write(user_paths)
        else:
            st.info("Take the quiz to generate your career paths!")

    elif menu=="Explore":
        st.title("🏫 College Recommendations")
        search = st.text_input("Search by Course or College")
        df = colleges_df
        if search:
            df = df[df.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        st.dataframe(df)

    elif menu=="Notifications":
        st.title("🔔 Notifications")
        st.info("No new notifications yet.")

    elif menu=="About Us":
        st.title("ℹ️ About Us")
        st.write("Career Compass is your personal career guidance tool built for SIH.")
        st.write("It helps students in J&K explore careers, colleges, and roadmaps.")

    elif menu=="Logout":
        st.session_state.login = False
        st.session_state.user = None
        st.session_state.quiz_answers = []
        st.success("Logged out successfully.")

# ----------------------------- QUIZ PAGE -----------------------------
def quiz_page():
    st.header("📝 Career Quiz")
    answers = []
    with st.form("quiz_form"):
        for i, q_key in enumerate(sorted(quiz_data["main"].keys())):
            q = quiz_data["main"][q_key]
            st.write(f"**Q{i+1}: {q['question']}**")
            option_texts = [opt["text"] for opt in q["options"].values()]
            ans_idx = st.radio("Choose answer", option_texts, key=f"main_{i}")
            ans_key = [k for k, v in q["options"].items() if v["text"] == ans_idx][0]
            answers.append(ans_key)

        submitted = st.form_submit_button("Submit Quiz")
        if submitted:
            main_scores = calculate_scores(quiz_data["main"], answers)
            major, minor, backup = recommend(main_scores)
            st.success(f"Major: {major}, Minor: {minor}, Backup: {backup}")

            # Save results to user
            df = load_users()
            idx = df.index[df["email"]==st.session_state.user["email"]][0]
            df.at[idx,"your_paths"] = f"Major: {major}, Minor: {minor}, Backup: {backup}"
            save_users(df)
            st.session_state.user = df.iloc[idx].to_dict()

# ----------------------------- ROUTER -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page=="login":
    login_page()
else:
    home_page()
