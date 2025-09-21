import streamlit as st
import pandas as pd
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"

# Custom CSS for nice UI
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .stButton > button { border-radius: 10px; background-color: #4CAF50; color: white; font-weight: bold; }
    .stRadio > div > label { font-size: 16px; font-weight: bold; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .hero { text-align: center; margin: 20px 0; }
    .metric { background-color: #f0f2f6; padding: 10px; border-radius: 8px; text-align: center; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# Hide menu
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# -----------------------------
# LOAD DATA (with caching for performance)
# -----------------------------
@st.cache_data
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["email","password","name","age","gender","city","state","education","avatar"])

def save_users(df):
    df.to_csv(USERS_CSV, index=False)

@st.cache_data
def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    return pd.DataFrame(columns=["College","Website","Courses"])

# -----------------------------
# QUIZ DATA (unchanged from previous)
# -----------------------------
QUIZ_QUESTIONS = [
    {"q":"Do you enjoy solving technical problems?",
     "options":["Yes, love it","Sometimes","Not really"],
     "career_map":{"Yes, love it":"Engineer","Sometimes":"Researcher","Not really":"Arts"}},
    {"q":"Do you like working with people or alone?",
     "options":["With people","Alone","Both"],
     "career_map":{"With people":"Teacher","Alone":"Scientist","Both":"Manager"}},
    {"q":"What excites you most?",
     "options":["Space","Electronics","Biology","History"],
     "career_map":{"Space":"Astronomer","Electronics":"ECE Engineer","Biology":"Doctor","History":"Civil Services"}}
]

CAREER_ROADMAPS = {
    "Engineer":["Choose branch (e.g., CSE, Mech)","B.Tech/B.E.","Projects + Internships","Placements/GATE for PSUs"],
    "Teacher":["Complete UG/PG in relevant subject","Clear NET/SET/CTET","Start teaching in schools/colleges"],
    "Scientist":["UG in Science base (B.Sc)","Masters + Research projects","Apply to DRDO/ISRO/PhD programs"],
    "Astronomer":["B.Sc Physics/Math","M.Sc Astronomy/Astrophysics","ISRO/Research institutes"],
    "Doctor":["Clear NEET exam","MBBS (5.5 years)","PG Specialization (MD/MS)"],
    "Civil Services":["Any Graduate degree","UPSC Prep (1-2 years)","Mains + Interview"],
    "ECE Engineer":["B.Tech ECE","Internships in Electronics","Jobs in Telecom/IT"],
    "Researcher":["B.Sc/M.Sc in field","Research publications","PhD/Grants"],
    "Manager":["BBA/B.Com","MBA (optional)","Entry-level management roles"],
    "Arts":["B.A in subject","Freelance/Skill courses","Media/Government jobs"]
}

CAREER_DESCRIPTIONS = {
    "Engineer": "Engineers design and build solutions to real-world problems, from software to infrastructure. High demand in tech and manufacturing.",
    "Teacher": "Teachers educate and inspire the next generation. Opportunities in schools, coaching centers, and online platforms.",
    "Scientist": "Scientists conduct experiments and research to advance knowledge. Roles in labs, universities, and R&D firms.",
    "Astronomer": "Astronomers study celestial bodies and space phenomena. Involves telescopes, data analysis, and space agencies like ISRO.",
    "Doctor": "Doctors diagnose and treat illnesses, saving lives. Path starts with NEET and leads to specialization.",
    "Civil Services": "Civil servants manage public administration. Prestigious roles via UPSC, impacting policy and governance.",
    "ECE Engineer": "ECE Engineers work on electronics, communications, and embedded systems. Key in telecom, robotics, and IoT.",
    "Researcher": "Researchers investigate topics in science/humanities. Focus on innovation, publications, and funding.",
    "Manager": "Managers lead teams and operations in business. Skills in leadership, strategy, and problem-solving.",
    "Arts": "Arts professionals create and analyze culture/history. Careers in writing, museums, or civil services."
}

CAREER_COURSES = {
    "Engineer": "B.Tech Computer Science, B.Tech Mechanical, B.E. Civil",
    "Teacher": "B.A Education, B.Ed, M.A Subject",
    "Scientist": "B.Sc Physics, B.Sc Chemistry, M.Sc Research",
    "Astronomer": "B.Sc Physics, B.Sc Mathematics, M.Sc Astronomy",
    "Doctor": "MBBS, B.Sc Nursing",
    "Civil Services": "B.A Political Science, B.Com, Any UG",
    "ECE Engineer": "B.Tech ECE, B.Sc Electronics",
    "Researcher": "B.Sc Biology, M.Sc Environmental Science",
    "Manager": "BBA, B.Com Accounting, MBA",
    "Arts": "B.A English, B.A History, B.A Fine Arts"
}

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "sidebar_choice" not in st.session_state:
    st.session_state.sidebar_choice = "Home"
if "temp_signup" not in st.session_state:
    st.session_state.temp_signup = None

# -----------------------------
# SIDEBAR (Enhanced with icons and divider)
# -----------------------------
def sidebar():
    if st.session_state.user:
        st.sidebar.title(f"👋 Welcome, {st.session_state.user['name']}")
        avatar_path = st.session_state.user.get("avatar")
        if avatar_path and os.path.exists(avatar_path):
            st.sidebar.image(avatar_path, width=80)
        else:
            default_avatar = os.path.join(AVATAR_FOLDER, "avatar2.png")
            if os.path.exists(default_avatar):
                st.sidebar.image(default_avatar, width=80)

        st.sidebar.markdown("---")  # Divider

        options = ["🏠 Home", "🎯 Quiz", "🎓 Colleges", "🔎 Explore", "👤 Profile", "ℹ️ About Us", "🚪 Logout"]
        display_options = [opt.split(" ", 1)[1] for opt in options]  # For internal use
        selected_idx = display_options.index(st.session_state.sidebar_choice) if st.session_state.sidebar_choice in display_options else 0
        st.session_state.sidebar_choice = st.sidebar.radio(
            "📍 Navigate",
            display_options,
            index=selected_idx,
            key="sidebar_radio"
        )

        choice = st.session_state.sidebar_choice
        if choice == "Logout":
            if st.sidebar.button("Confirm Logout?"):
                st.session_state = {"page": "login", "user": None, "quiz_answers": [], "sidebar_choice": "Home", "temp_signup": None}
                st.rerun()
        else:
            st.session_state.page = choice.lower().replace(" ", "_")

# -----------------------------
# LOGIN / SIGNUP (Enhanced layout)
# -----------------------------
def login_page():
    st.title("🔐 Login / Sign Up")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Login")
        email = st.text_input("📧 Email", key="login_email", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", key="login_pwd", placeholder="Enter password")
        if st.button("Login 🚀", use_container_width=True):
            with st.spinner("Checking credentials..."):
                users = load_users()
                if not users.empty and ((users["email"] == email) & (users["password"] == password)).any():
                    st.session_state.user = users[users["email"] == email].iloc[0].to_dict()
                    st.session_state.page = "home"
                    st.success("Login successful! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try again.")

    with col2:
        st.markdown("### Sign Up")
        email = st.text_input("📧 Email", key="signup_email", placeholder="New email")
        password = st.text_input("🔒 Password", type="password", key="signup_pwd", placeholder="New password")
        if st.button("Next ➡️", use_container_width=True):
            if email and password:
                st.session_state.temp_signup = {"email": email, "password": password}
                st.session_state.page = "profile_setup"
                st.rerun()
            else:
                st.error("❌ Please enter email and password")

# -----------------------------
# PROFILE SETUP (Enhanced with columns)
# -----------------------------
def profile_setup_page():
    st.title("👤 Complete Your Profile")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Enter your full name")
        age = st.number_input("Age", min_value=10, max_value=100, placeholder="Your age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        city = st.text_input("City", placeholder="e.g., Jammu")
        state = st.text_input("State", value="Jammu & Kashmir", disabled=True)
        education = st.text_input("Education (e.g., Class 12th)", placeholder="Your qualification")

    avatar_map = {"Male": "avatar3.png", "Female": "avatar1.png", "Other": "avatar2.png"}

    if st.button("Finish Setup 🎓", use_container_width=True):
        if st.session_state.temp_signup:
            with st.spinner("Saving profile..."):
                avatar_file = os.path.join(AVATAR_FOLDER, avatar_map[gender])
                user_df = load_users()
                new_user = {
                    "email": st.session_state.temp_signup["email"],
                    "password": st.session_state.temp_signup["password"],
                    "name": name, "age": age, "gender": gender, "city": city,
                    "state": state, "education": education, "avatar": avatar_file
                }
                user_df = pd.concat([user_df, pd.DataFrame([new_user])], ignore_index=True)
                save_users(user_df)
                st.session_state.user = new_user
                st.session_state.temp_signup = None
                st.session_state.page = "home"
                st.success("Profile created! Welcome aboard! 🚀")
                st.rerun()

# -----------------------------
# PROFILE EDIT (Enhanced)
# -----------------------------
def profile_page():
    st.header("👤 Edit Profile")
    user = st.session_state.user

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=user.get("name", ""), key="edit_name")
        try:
            default_age = int(user.get("age", 18))
        except:
            default_age = 18
        age = st.number_input("Age", value=default_age, min_value=10, max_value=100)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(user.get("gender","Other")))
    with col2:
        city = st.text_input("City", value=user.get("city",""))
        state = st.text_input("State", value=user.get("state","Jammu & Kashmir"))
        education = st.text_input("Education", value=user.get("education",""))

    if st.button("Save Changes 💾", use_container_width=True):
        avatar_map = {"Male":"avatar3.png","Female":"avatar1.png","Other":"avatar2.png"}
        avatar_file = os.path.join(AVATAR_FOLDER, avatar
