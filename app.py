import streamlit as st
import pandas as pd
import os

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"  # Path to college CSV
AVATAR_FOLDER = "images"

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    return pd.DataFrame(columns=["email", "password", "name", "age", "gender", "city", "state", "education", "avatar"])

def save_users(df):
    df.to_csv(USERS_CSV, index=False)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    return pd.DataFrame(columns=["College", "Website", "Course"])

# -------------------------------------------------
# QUIZ DATA
# -------------------------------------------------
QUIZ_QUESTIONS = [
    {"q": "Do you enjoy solving technical problems?", "options": ["Yes", "Sometimes", "Not really"], 
     "career_map": {"Yes": "Engineer", "Sometimes": "Researcher", "Not really": "Arts"}},
    {"q": "Do you like working with people or alone?", "options": ["With people", "Alone", "Both"], 
     "career_map": {"With people": "Teacher", "Alone": "Scientist", "Both": "Manager"}},
    {"q": "What excites you most?", "options": ["Space", "Electronics", "Biology", "History"], 
     "career_map": {"Space": "Astronomer", "Electronics": "ECE Engineer", "Biology": "Doctor", "History": "Civil Services"}},
    {"q": "Do you enjoy research and experiments?", "options": ["Yes", "Sometimes", "No"], 
     "career_map": {"Yes": "Scientist", "Sometimes": "Researcher", "No": "Manager"}},
    {"q": "Do you like programming?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Engineer", "No": "Manager"}},
    {"q": "Do you enjoy teaching others?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Teacher", "No": "Scientist"}},
    {"q": "Are you interested in healthcare?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Doctor", "No": "Engineer"}},
    {"q": "Do you like organizing events or managing teams?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Manager", "No": "Scientist"}},
    {"q": "Are you interested in government services?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Civil Services", "No": "Engineer"}},
    {"q": "Do you enjoy analyzing data?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Engineer", "No": "Teacher"}},
    {"q": "Do you like working with numbers?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Engineer", "No": "Arts"}},
    {"q": "Do you like creative problem solving?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Engineer", "No": "Manager"}},
    {"q": "Are you fascinated by the universe?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Astronomer", "No": "Scientist"}},
    {"q": "Do you enjoy helping people directly?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Doctor", "No": "Engineer"}},
    {"q": "Do you enjoy reading historical events?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Civil Services", "No": "Scientist"}},
    {"q": "Do you like coding competitions?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Engineer", "No": "Manager"}},
    {"q": "Do you enjoy lab experiments?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Scientist", "No": "Teacher"}},
    {"q": "Do you like mentoring or coaching others?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Teacher", "No": "Scientist"}},
    {"q": "Are you interested in public policy?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "Civil Services", "No": "Engineer"}},
    {"q": "Do you like designing electronic devices?", "options": ["Yes", "No"], 
     "career_map": {"Yes": "ECE Engineer", "No": "Scientist"}}
   
]

CAREER_ROADMAPS = {
    "Engineer": ["Choose a branch (CSE/ECE/ME)", "Get B.Tech degree", "Projects + internships", "Appear for GATE/placements"],
    "Teacher": ["Complete UG/PG", "Clear NET/SET", "Start teaching career"],
    "Scientist": ["Strong UG base", "Masters + Research", "Apply for DRDO/ISRO/PhD"],
    "Astronomer": ["Physics/Maths UG", "Astronomy MSc", "ISRO/Research"],
    "Doctor": ["Clear NEET", "MBBS", "PG specialization"],
    "Civil Services": ["Graduate in any stream", "UPSC Prep", "Write Mains + Interview"]
}

CAREER_DESCRIPTIONS = {
    "Engineer": "Design and build solutions using technology.",
    "Teacher": "Educate and guide students in schools or colleges.",
    "Scientist": "Conduct research and experiments in scientific domains.",
    "Astronomer": "Study celestial bodies and the universe.",
    "Doctor": "Provide medical care to patients.",
    "Civil Services": "Work in government services and administration."
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
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

# -------------------------------------------------
# LOGIN / SIGNUP
# -------------------------------------------------
def login_page():
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

# -------------------------------------------------
# PROFILE SETUP
# -------------------------------------------------
def profile_setup_page():
    st.title("👤 Set up your profile")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    city = st.text_input("City")
    state = st.text_input("State")
    education = st.text_input("Education Qualification")

   

    if st.button("Finish Setup"):
         # Avatar selection based on gender
    # In profile setup
        if gender == "Female":
           chosen_avatar = "images/avatar1.png"
        elif gender == "Male":
           chosen_avatar = "images/avatar3.png"
        else:
           chosen_avatar = "images/avatar2.png"

    avatar_path = st.session_state.user.get("avatar")
    if avatar_path and os.path.exists(avatar_path):
       st.sidebar.image(avatar_path, width=80)
    else:
       st.sidebar.image("images/avatar2.png", width=80)  # default fallback

        user_df = load_users()
        new_user = {"email": st.session_state.temp_signup["email"], "password": st.session_state.temp_signup["password"],
                    "name": name, "age": age, "gender": gender, "city": city, "state": state,
                    "education": education, "avatar": os.path.join(AVATAR_FOLDER, chosen_avatar)}
        user_df = pd.concat([user_df, pd.DataFrame([new_user])], ignore_index=True)
        save_users(user_df)
        st.session_state.user = new_user
        st.session_state.page = "home"
        st.success("Profile created ✅")

# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
def home_page():
    sidebar()
    st.title("🧭 Career Compass")
    st.subheader("Your personalized guide to careers, colleges, and opportunities.")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
def sidebar():
    st.sidebar.image(st.session_state.user["avatar"], width=80)
    st.sidebar.title(f"{st.session_state.user['name']}")
    choice = st.sidebar.radio("📍 Navigate", ["Home", "Quiz", "Explore", "Careers", "Colleges", "Profile", "About Us", "Logout"])
    if choice == "Home":
        st.session_state.page = "home"
    elif choice == "Quiz":
        st.session_state.page = "quiz"
    elif choice == "Explore":
        st.session_state.page = "explore"
    elif choice == "Careers":
        st.session_state.page = "career"
    elif choice == "Colleges":
        st.session_state.page = "colleges"
    elif choice == "Profile":
        st.session_state.page = "profile"
    elif choice == "About Us":
        st.session_state.page = "about"
    elif choice == "Logout":
        st.session_state.page = "login"
        st.session_state.user = None

# -------------------------------------------------
# QUIZ PAGE
# -------------------------------------------------
def quiz_page():
    st.header("🎯 Career Quiz")
    if st.button("Retake Quiz"):
        st.session_state.quiz_answers = []
        st.session_state.quiz_index = 0

    if st.session_state.quiz_index < len(QUIZ_QUESTIONS):
        q = QUIZ_QUESTIONS[st.session_state.quiz_index]
        st.write(q["q"])
        choice = st.radio("Select:", q["options"], key=f"q{st.session_state.quiz_index}")
        if st.button("Next Question"):
            if choice:
                st.session_state.quiz_answers.append(choice)
                st.session_state.quiz_index += 1
                st.experimental_rerun = lambda : None  # prevent rerun
    else:
        st.success("✅ Quiz Completed!")
        suggested = []
        for i, ans in enumerate(st.session_state.quiz_answers):
            role = QUIZ_QUESTIONS[i]["career_map"].get(ans)
            if role:
                suggested.append(role)
        suggested = list(set(suggested))
        st.subheader("Your suggested careers:")
        for role in suggested:
            st.write(f"- {role}")
            if role in CAREER_ROADMAPS:
                st.subheader(f"📌 {role} Roadmap:")
                for step in CAREER_ROADMAPS[role]:
                    st.write(f"- {step}")

# -------------------------------------------------
# EXPLORE PAGE
# -------------------------------------------------
def explore_page():
    st.header("🔎 Explore Careers")
    career = st.selectbox("Select Career", list(CAREER_ROADMAPS.keys()))
    if career:
        st.subheader("Description:")
        st.write(CAREER_DESCRIPTIONS.get(career, "No description available"))
        st.subheader("Roadmap:")
        for step in CAREER_ROADMAPS.get(career, []):
            st.write(f"- {step}")
        st.subheader("Courses & Colleges:")
        df = load_colleges()
        df_courses = df[df["Course"].str.contains(career, case=False, na=False)]
        st.dataframe(df_courses[["College", "Course", "Website"]])

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
# COLLEGES PAGE
# -------------------------------------------------
def college_page():
    st.header("🎓 Government Colleges in J&K")
    df = load_colleges()
    if df.empty:
        st.error("No college data found. Please upload dataset.")
        return
    search_type = st.radio("Search by:", ["Course", "College"])
    search = st.text_input("Search")
    if search_type == "Course" and search:
        filtered = df[df["Course"].str.contains(search, case=False, na=False)]
        st.dataframe(filtered[["College", "Course", "Website"]])
    elif search_type == "College" and search:
        filtered = df[df["College"].str.contains(search, case=False, na=False)]
        col_selected = st.selectbox("Select College", filtered["College"])
        if col_selected:
            selected = filtered[filtered["College"] == col_selected].iloc[0]
            st.write(f"**Website:** {selected['Website']}")
            st.write(f"**Courses Offered:** {selected['Course']}")

# -------------------------------------------------
# PROFILE PAGE
# -------------------------------------------------
def profile_page():
    st.header("👤 Profile")
    user = st.session_state.user
    st.image(user["avatar"], width=120)
    name = st.text_input("Full Name", user["name"])
    age = st.number_input("Age", value=int(user["age"]))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(user["gender"]))
    city = st.text_input("City", user["city"])
    state = st.text_input("State", user["state"])
    education = st.text_input("Education", user["education"])
    if st.button("Save Profile"):
        df = load_users()
        df.loc[df["email"] == user["email"], ["name","age","gender","city","state","education"]] = [name, age, gender, city, state, education]
        save_users(df)
        st.success("Profile updated ✅")
        st.session_state.user.update({"name":name,"age":age,"gender":gender,"city":city,"state":state,"education":education})

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
elif st.session_state.page == "quiz":
    quiz_page()
elif st.session_state.page == "career":
    career_page()
elif st.session_state.page == "colleges":
    college_page()
elif st.session_state.page == "profile":
    profile_page()
elif st.session_state.page == "explore":
    explore_page()
elif st.session_state.page == "about":
    about_page()
