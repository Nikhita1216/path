import streamlit as st
import pandas as pd
import json
import os

# -----------------------------
# Load J&K Govt Colleges Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("jk_govt_colleges.csv")
    return df

df_colleges = load_data()

# -----------------------------
# User Authentication
# -----------------------------
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(email, password, name, age, gender, location, study, avatar):
    users = load_users()
    if email in users:
        return False, "User already exists!"
    users[email] = {
        "password": password,
        "name": name,
        "age": age,
        "gender": gender,
        "location": location,
        "study": study,
        "avatar": avatar,
        "paths": [],
        "notifications": []
    }
    save_users(users)
    return True, "Signup successful!"

def login(email, password):
    users = load_users()
    if email in users and users[email]["password"] == password:
        return True, users[email]
    return False, None

# -----------------------------
# Quiz Engine (simplified AI-like rules)
# -----------------------------
def run_quiz(study, interests, personality):
    careers = []
    if "science" in interests.lower():
        careers.append("Engineering")
    if "math" in interests.lower():
        careers.append("Data Science")
    if "art" in interests.lower() or "creative" in personality.lower():
        careers.append("Design / Creative Arts")
    if "social" in personality.lower():
        careers.append("Teaching / UPSC / Civil Services")
    if "sports" in interests.lower():
        careers.append("Sports / Fitness Training")
    if "food" in interests.lower():
        careers.append("Culinary / Hospitality")
    if not careers:
        careers = ["General Bachelors Path (BA/BSc/BCom)", "Entrepreneurship", "Defence Services"]
    return careers

# -----------------------------
# Roadmaps (simplified)
# -----------------------------
ROADMAPS = {
    "Engineering": ["10+2 with PCM → JEE / CET → BTech → MTech/Jobs → PSU/Research"],
    "Data Science": ["10+2 with PCM → BSc CS/Maths or BTech → Certifications (Python, ML) → Jobs in IT/Analytics"],
    "Design / Creative Arts": ["10+2 → BDes / Fine Arts → Internships → Freelance/Industry Jobs"],
    "Teaching / UPSC / Civil Services": ["10+2 → Graduation (any stream) → UPSC/J&K Civil Exams → Govt Jobs"],
    "Sports / Fitness Training": ["10+2 → BPEd / Sports Academy → Coaching / Professional Sports"],
    "Culinary / Hospitality": ["10+2 → BHM (Hotel Management) → Culinary School → Chef / Hotel Industry"]
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

# Pastel theme background
st.markdown("""
    <style>
    body {
        background-color: #fdf6f0;
    }
    .stButton>button {
        background-color: #a3d2ca;
        color: black;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# Login / Signup Page
# -----------------------------
if not st.session_state.logged_in:
    st.title("🌍 Career Compass")
    st.write("“Education is the most powerful weapon which you can use to change the world.” – Nelson Mandela")

    choice = st.radio("Login or Sign Up?", ["Login", "Sign Up"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, user = login(email, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")

    else:
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        age = st.number_input("Age", 10, 60)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        location = st.text_input("Location")
        study = st.selectbox("Currently Studying", ["Schooling", "Intermediate/Diploma", "BTech/BSc/etc"])
        avatar = st.selectbox("Choose Profile Avatar", ["🎓", "👩‍💻", "👨‍🔬", "👩‍🎨", "⚽", "🍳"])
        if st.button("Sign Up"):
            success, msg = signup(email, password, name, age, gender, location, study, avatar)
            if success:
                st.success(msg + " Please login now.")
            else:
                st.error(msg)

else:
    # -----------------------------
    # Main App (after login)
    # -----------------------------
    st.sidebar.title(f"{st.session_state.user['avatar']} {st.session_state.user['name']}")
    page = st.sidebar.radio("Navigate", ["Home", "Profile", "Your Paths", "Quiz", "Career Explorer", "Notifications", "About Us", "Logout"])

    # Home
    if page == "Home":
        st.header("📌 Welcome to Career Compass")
        st.info("“Education is the key to unlocking the golden door of freedom.” – George Washington Carver")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Take Career Quiz"):
                st.session_state.page = "Quiz"
        with col2:
            if st.button("Explore Careers"):
                st.session_state.page = "Career Explorer"

    # Profile
    elif page == "Profile":
        st.subheader("👤 Profile")
        st.json(st.session_state.user)

    # Quiz
    elif page == "Quiz":
        st.subheader("🧑‍💻 Career Quiz")
        study = st.selectbox("What are you currently studying?", ["Schooling", "Intermediate", "BTech/BSc", "Other"])
        interests = st.text_area("What are your main interests?")
        personality = st.text_area("Describe your personality in a few words")
        if st.button("Get Career Suggestions"):
            careers = run_quiz(study, interests, personality)
            st.success("Based on your answers, here are some suggested careers:")
            for c in careers:
                st.write(f"👉 {c}")
                if st.button(f"View Roadmap for {c}"):
                    st.write("Roadmap:")
                    for step in ROADMAPS.get(c, ["Explore further study options..."]):
                        st.write(f"- {step}")
                    # Colleges
                    st.write("Government Colleges in J&K offering this stream:")
                    if "Engineering" in c:
                        st.dataframe(df_colleges[df_colleges["Courses_Offered"].str.contains("BTech|Engineering", case=False, na=False)])
                    elif "Data Science" in c or "Science" in c:
                        st.dataframe(df_colleges[df_colleges["Courses_Offered"].str.contains("BSc", case=False, na=False)])
                    elif "Arts" in c or "Design" in c:
                        st.dataframe(df_colleges[df_colleges["Courses_Offered"].str.contains("BA", case=False, na=False)])
                    elif "Culinary" in c:
                        st.write("Few specialized institutions (not many Govt colleges offer Culinary in J&K). Consider Hotel Management courses.")
                    else:
                        st.dataframe(df_colleges)

    # Career Explorer
    elif page == "Career Explorer":
        st.subheader("🎓 Career Explorer")
        course_filter = st.text_input("Search by course (e.g. BSc, BCom, BCA)")
        if course_filter:
            filtered = df_colleges[df_colleges["Courses_Offered"].str.contains(course_filter, case=False, na=False)]
            st.dataframe(filtered)
        else:
            st.dataframe(df_colleges)

    # Your Paths
    elif page == "Your Paths":
        st.subheader("🛤 Your Saved Career Paths")
        st.info("This will display careers saved from quiz results.")
        # Can expand to allow saving from quiz results

    # Notifications
    elif page == "Notifications":
        st.subheader("🔔 Notifications")
        st.write("You will get updates here when new study material or career paths are added.")

    # About Us
    elif page == "About Us":
        st.subheader("ℹ️ About Career Compass")
        st.write("""
        Career Compass is built to help students of Jammu & Kashmir discover their best career paths.  
        By combining quizzes, government college data, study resources, and future scope, we aim to guide the youth toward sustainable development and better opportunities.
        """)

    # Logout
    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("You have logged out successfully!")
