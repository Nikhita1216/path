import streamlit as st
import pandas as pd
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "/mnt/data/jk_colleges.csv"  # Your dataset path
AVATAR_FOLDER = "images"
COMPASS_GIF = "compass.gif"

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["email", "password", "name", "avatar"])

def save_users(df):
    df.to_csv(USERS_CSV, index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    return pd.DataFrame(columns=["College", "Location", "Course", "Future_Scope", "Study_Materials", "Exam_Info"])

# -------------------------------------------------
# QUIZ DATA
# -------------------------------------------------
QUIZ_QUESTIONS = [
    {
        "q": "Do you enjoy solving technical problems?",
        "options": ["Yes, love it", "Sometimes", "Not really"],
        "career_map": {"Yes, love it": "Engineer", "Sometimes": "Researcher", "Not really": "Arts"}
    },
    {
        "q": "Do you like working with people or alone?",
        "options": ["With people", "Alone", "Both"],
        "career_map": {"With people": "Teacher", "Alone": "Scientist", "Both": "Manager"}
    },
    {
        "q": "What excites you most?",
        "options": ["Space", "Electronics", "Biology", "History"],
        "career_map": {"Space": "Astronomer", "Electronics": "ECE Engineer", "Biology": "Doctor", "History": "Civil Services"}
    }
]

CAREER_ROADMAPS = {
    "Engineer": ["Step 1: Choose a branch (CSE/ECE/ME)", "Step 2: Get B.Tech degree", "Step 3: Do projects + internships", "Step 4: Appear for GATE/placements"],
    "Teacher": ["Step 1: Complete UG/PG", "Step 2: Clear NET/SET", "Step 3: Start teaching career"],
    "Scientist": ["Step 1: Strong UG base", "Step 2: Masters + Research", "Step 3: Apply for DRDO/ISRO/PhD"],
    "Astronomer": ["Step 1: Physics/Maths UG", "Step 2: Astronomy MSc", "Step 3: ISRO/Research"],
    "Doctor": ["Step 1: Clear NEET", "Step 2: MBBS", "Step 3: PG specialization"],
    "Civil Services": ["Step 1: Graduate in any stream", "Step 2: UPSC Prep", "Step 3: Write Mains + Interview"]
}

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []

# -------------------------------------------------
# LOGIN / SIGNUP
# -------------------------------------------------
def login_page():
    st.image(COMPASS_GIF, width=120)
    st.title("🔐 Login to Career Compass")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            users = load_users()
            if not users.empty and ((users["email"] == email) & (users["password"] == password)).any():
                st.session_state.user = users[users["email"] == email].iloc[0].to_dict()
                st.session_state.page = "home"
                st.success("Login successful ✅")
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pwd")
        if st.button("Next ➡️"):
            st.session_state.temp_signup = {"email": email, "password": password}
            st.session_state.page = "profile_setup"

def profile_setup_page():
    st.title("👤 Set up your profile")
    name = st.text_input("Full Name")
    avatars = [os.path.join(AVATAR_FOLDER, f) for f in os.listdir(AVATAR_FOLDER) if f.endswith(".png")]
    chosen = st.radio("Choose an avatar", avatars, format_func=lambda x: os.path.basename(x))
    if st.button("Finish Setup"):
        user_df = load_users()
        new_user = {"email": st.session_state.temp_signup["email"],
                    "password": st.session_state.temp_signup["password"],
                    "name": name, "avatar": chosen}
        user_df = pd.concat([user_df, pd.DataFrame([new_user])], ignore_index=True)
        save_users(user_df)
        st.session_state.user = new_user
        st.session_state.page = "home"
        st.success("Profile created ✅")

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def home_page():
    st.sidebar.image(st.session_state.user["avatar"], width=80)
    st.sidebar.title(f"Welcome, {st.session_state.user['name']}")
    choice = st.sidebar.radio("📍 Navigate", ["Home", "Quiz", "Careers", "Colleges", "About Us", "Logout"])

    if choice == "Home":
        st.title("🧭 Career Compass")
        st.image(COMPASS_GIF, width=200)
        st.subheader("Your personalized guide to career paths, colleges, and opportunities.")
    elif choice == "Quiz":
        quiz_page()
    elif choice == "Careers":
        career_page()
    elif choice == "Colleges":
        college_page()
    elif choice == "About Us":
        about_page()
    elif choice == "Logout":
        st.session_state.page = "login"
        st.session_state.user = None

# -------------------------------------------------
# QUIZ PAGE
# -------------------------------------------------
def quiz_page():
    st.header("🎯 Career Quiz")
    q_num = len(st.session_state.quiz_answers)
    if q_num < len(QUIZ_QUESTIONS):
        q = QUIZ_QUESTIONS[q_num]
        st.write(q["q"])
        choice = st.radio("Select:", q["options"], key=f"q{q_num}")
        if st.button("Next"):
            st.session_state.quiz_answers.append(choice)
            st.rerun()
    else:
        st.success("✅ Quiz Completed!")
        suggested = []
        for i, ans in enumerate(st.session_state.quiz_answers):
            role = QUIZ_QUESTIONS[i]["career_map"].get(ans)
            if role:
                suggested.append(role)
        st.subheader("Your suggested careers:")
        for role in set(suggested):
            st.write(f"- {role}")
        st.info("👉 Go to Careers tab for detailed roadmaps.")

# -------------------------------------------------
# CAREERS PAGE
# -------------------------------------------------
def career_page():
    st.header("🚀 Career Roadmaps")
    if not st.session_state.quiz_answers:
        st.warning("Take the quiz first!")
        return
    roles = []
    for i, ans in enumerate(st.session_state.quiz_answers):
        r = QUIZ_QUESTIONS[i]["career_map"].get(ans)
        if r:
            roles.append(r)
    roles = list(set(roles))
    for r in roles:
        with st.expander(f"📌 {r}"):
            if r in CAREER_ROADMAPS:
                for step in CAREER_ROADMAPS[r]:
                    st.write(f"- {step}")

# -------------------------------------------------
# COLLEGE PAGE
# -------------------------------------------------
def college_page():
    st.header("🎓 Government Colleges in J&K")
    df = load_colleges()
    if df.empty:
        st.error("No college data found. Please upload dataset.")
        return
    search = st.text_input("Search by Course")
    if search:
        df = df[df["Course"].str.contains(search, case=False, na=False)]
    st.dataframe(df, use_container_width=True)

# -------------------------------------------------
# ABOUT US
# -------------------------------------------------
def about_page():
    st.header("ℹ️ About Us")
    st.write("Career Compass is your personal career guidance tool built for SIH.")
    st.write("We help students in Jammu & Kashmir explore careers, colleges, and roadmaps.")
    st.subheader("📞 Contact Info")
    st.write("Email: support@careercompass.in")
    st.write("Phone: +91-9876543210")

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "profile_setup":
    profile_setup_page()
elif st.session_state.page == "home":
    home_page()
