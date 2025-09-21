import streamlit as st
import pandas as pd
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "/mnt/data/jk_colleges.csv"
AVATAR_FOLDER = "images"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["email","password","name","age","gender","city","state","education","avatar"])

def save_users(df):
    df.to_csv(USERS_CSV,index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    return pd.DataFrame(columns=["College","Website","Courses"])

# -----------------------------
# QUIZ DATA
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
    "Engineer":["Choose branch","B.Tech","Projects+Internships","Placements/GATE"],
    "Teacher":["UG/PG","Clear NET/SET","Start teaching"],
    "Scientist":["UG base","Masters+Research","Apply DRDO/ISRO/PhD"],
    "Astronomer":["Physics/Math UG","MSc Astronomy","ISRO/Research"],
    "Doctor":["Clear NEET","MBBS","PG Specialization"],
    "Civil Services":["Graduate","UPSC Prep","Mains+Interview"]
}

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page="login"
if "user" not in st.session_state:
    st.session_state.user=None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers=[]
if "sidebar_choice" not in st.session_state:
    st.session_state.sidebar_choice="Home"

# -----------------------------
# SIDEBAR
# -----------------------------
def sidebar():
    if st.session_state.user:
        st.sidebar.title(f"Welcome, {st.session_state.user['name']}")
        avatar_path = st.session_state.user.get("avatar")
        if avatar_path and os.path.exists(avatar_path):
            st.sidebar.image(avatar_path,width=80)
        else:
            st.sidebar.image(os.path.join(AVATAR_FOLDER,"avatar2.png"),width=80)

        st.session_state.sidebar_choice = st.sidebar.radio(
            "📍 Navigate",
            ["Home","Quiz","Careers","Colleges","Explore","Profile","About Us","Logout"],
            index=["Home","Quiz","Careers","Colleges","Explore","Profile","About Us","Logout"].index(st.session_state.sidebar_choice)
        )

        choice = st.session_state.sidebar_choice
        if choice=="Logout":
            st.session_state.page="login"
            st.session_state.user=None
            st.session_state.quiz_answers=[]
        else:
            st.session_state.page = choice.lower().replace(" ","_")

# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
def login_page():
    st.title("🔐 Login / Sign Up")
    tab1, tab2 = st.tabs(["Login","Sign Up"])

    with tab1:
        email = st.text_input("Email",key="login_email")
        password = st.text_input("Password",type="password",key="login_pwd")
        if st.button("Login"):
            users = load_users()
            if not users.empty and ((users["email"]==email) & (users["password"]==password)).any():
                st.session_state.user = users[users["email"]==email].iloc[0].to_dict()
                st.session_state.page="home"
                st.success("Login successful ✅")
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("Email",key="signup_email")
        password = st.text_input("Password",type="password",key="signup_pwd")
        if st.button("Next ➡️"):
            st.session_state.temp_signup = {"email":email,"password":password}
            st.session_state.page="profile_setup"

# -----------------------------
# PROFILE SETUP
# -----------------------------
def profile_setup_page():
    st.title("👤 Profile Setup")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender",["Male","Female","Other"])
    city = st.text_input("City")
    state = st.text_input("State")
    education = st.text_input("Education Qualification")

    avatar_map = {"Male":"avatar3.png","Female":"avatar1.png","Other":"avatar2.png"}

    if st.button("Finish Setup"):
        avatar_file = os.path.join(AVATAR_FOLDER, avatar_map[gender])
        user_df = load_users()
        new_user = {"email":st.session_state.temp_signup["email"],
                    "password":st.session_state.temp_signup["password"],
                    "name":name,"age":age,"gender":gender,"city":city,
                    "state":state,"education":education,"avatar":avatar_file}
        user_df = pd.concat([user_df,pd.DataFrame([new_user])],ignore_index=True)
        save_users(user_df)
        st.session_state.user=new_user
        st.session_state.page="home"
        st.success("Profile created ✅")

# -----------------------------
# PROFILE EDIT
# -----------------------------
def profile_page():
    st.header("👤 Edit Profile")
    user = st.session_state.user

    name = st.text_input("Full Name", user.get("name", ""))

    # safe conversion for age
    try:
        default_age = int(user.get("age", 18))
    except:
        default_age = 18
    age = st.number_input("Age", value=default_age, min_value=10, max_value=100)

    gender = st.selectbox(
        "Gender", 
        ["Male", "Female", "Other"], 
        index=["Male","Female","Other"].index(user.get("gender","Other"))
    )
    city = st.text_input("City", user.get("city",""))
    state = st.text_input("State", user.get("state",""))
    education = st.text_input("Education", user.get("education",""))

    if st.button("Save"):
        avatar_map = {"Male":"avatar3.png","Female":"avatar1.png","Other":"avatar2.png"}
        avatar_file = os.path.join(AVATAR_FOLDER, avatar_map[gender])
        users = load_users()
        users.loc[users["email"]==user["email"], ["name","age","gender","city","state","education","avatar"]] = [
            name, age, gender, city, state, education, avatar_file
        ]
        save_users(users)
        st.session_state.user.update({
            "name": name, "age": age, "gender": gender, "city": city, "state": state,
            "education": education, "avatar": avatar_file
        })
        st.success("Profile updated ✅")

# -----------------------------
# HOME
# -----------------------------
def home_page_content():
    st.header("🧭 Career Compass")
    st.subheader("Your personalized guide to careers, colleges, and opportunities.")

# -----------------------------
# QUIZ
# -----------------------------
def quiz_page():
    st.header("🎯 Career Quiz")
    if st.button("Retake Quiz"):
        st.session_state.quiz_answers=[]
    q_num = len(st.session_state.quiz_answers)
    if q_num < len(QUIZ_QUESTIONS):
        q = QUIZ_QUESTIONS[q_num]
        st.write(q["q"])
        choice = st.radio("Select:",q["options"],key=f"q{q_num}")
        if st.button("Next"):
            st.session_state.quiz_answers.append(choice)
    else:
        st.success("✅ Quiz Completed!")
        suggested=[]
        for i,ans in enumerate(st.session_state.quiz_answers):
            role = QUIZ_QUESTIONS[i]["career_map"].get(ans)
            if role:
                suggested.append(role)
        st.subheader("Your suggested careers:")
        for role in set(suggested):
            st.write(f"- {role}")
            if role in CAREER_ROADMAPS:
                st.write("Roadmap:")
                for step in CAREER_ROADMAPS[role]:
                    st.write(f"• {step}")

# -----------------------------
# CAREERS PAGE
# -----------------------------
def career_page():
    st.header("🚀 Career Roadmaps")
    if not st.session_state.quiz_answers:
        st.warning("Take the quiz first!")
        return
    roles=[]
    for i,ans in enumerate(st.session_state.quiz_answers):
        r = QUIZ_QUESTIONS[i]["career_map"].get(ans)
        if r:
            roles.append(r)
    roles = list(set(roles))
    for r in roles:
        st.subheader(r)
        if r in CAREER_ROADMAPS:
            for step in CAREER_ROADMAPS[r]:
                st.write(f"- {step}")

# -----------------------------
# EXPLORE PAGE
# -----------------------------
def explore_page():
    st.header("🔎 Explore Careers")
    career = st.text_input("Enter career to explore")
    if career:
        st.subheader(career)
        if career in CAREER_ROADMAPS:
            st.write("Roadmap:")
            for step in CAREER_ROADMAPS[career]:
                st.write(f"- {step}")
        df = load_colleges()
        if not df.empty:
            df_filtered = df[df["Courses"].str.contains(career,case=False,na=False)]
            if not df_filtered.empty:
                st.write("Colleges offering this career/course:")
                for idx,row in df_filtered.iterrows():
                    st.write(f"- {row['College']} ({row['Website']})")

# -----------------------------
# COLLEGES PAGE
# -----------------------------
def college_page():
    st.header("🎓 Colleges in J&K")
    df = load_colleges()
    if df.empty:
        st.error("No college data found!")
        return
    search_by = st.radio("Search by:",["Course","College"])
    if search_by=="Course":
        course = st.text_input("Enter course")
        if course:
            filtered = df[df["Courses"].str.contains(course,case=False,na=False)]
            st.dataframe(filtered)
    else:
        college = st.text_input("Enter college")
        if college:
            filtered = df[df["College"].str.contains(college,case=False,na=False)]
            if not filtered.empty:
                st.write(f"College: {filtered.iloc[0]['College']}")
                st.write(f"Website: {filtered.iloc[0]['Website']}")
                st.write(f"Courses: {filtered.iloc[0]['Courses']}")

# -----------------------------
# ABOUT
# -----------------------------
def about_page():
    st.header("ℹ️ About Us")
    st.write("Career Compass is your personal career guidance tool built for SIH.")
    st.write("We help students in Jammu & Kashmir explore careers, colleges, and roadmaps.")
    st.subheader("📞 Contact Info")
    st.write("Email: support@careercompass.in")
    st.write("Phone: +91-9876543210")

# -----------------------------
# MAIN ROUTER
# -----------------------------
if st.session_state.page=="login":
    login_page()
elif st.session_state.page=="profile_setup":
    profile_setup_page()
else:
    sidebar()  # persistent
    if st.session_state.page=="home":
        home_page_content()
    elif st.session_state.page=="quiz":
        quiz_page()
    elif st.session_state.page=="career":
        career_page()
    elif st.session_state.page=="colleges":
        college_page()
    elif st.session_state.page=="explore":
        explore_page()
    elif st.session_state.page=="profile":
        profile_page()
    elif st.session_state.page=="about":
        about_page()

