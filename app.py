import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Paths
COMPASS_GIF_PATH = "compass.gif"
AVATARS = [
    "images/avatar1.png",
    "images/avatar2.png",
    "images/avatar3.png"
]
COLLEGES_CSV = "jk_colleges.csv"
USER_DATA_CSV = "users.csv"

# -------------------------------
# CSS for pastel UI
st.markdown("""
<style>
.main {background-color: #fef6f0; color: #333333;}
.css-1d391kg {background-color: #f8eaf6;}
div.stButton > button {background-color: #ffd6f0; color: #333; border-radius: 12px; padding: 8px 20px; font-size:16px; font-weight:bold; transition: transform 0.2s;}
div.stButton > button:hover {transform: scale(1.05); box-shadow: 0px 4px 8px rgba(0,0,0,0.2);}
.card {background-color:#fff1f3; border-radius:12px; padding:15px; margin:10px 0; box-shadow:0px 2px 6px rgba(0,0,0,0.1); transition: transform 0.2s;}
.card:hover {transform: scale(1.02); box-shadow:0px 4px 10px rgba(0,0,0,0.15);}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load colleges
@st.cache_data
def load_colleges():
    df = pd.read_csv(COLLEGES_CSV)
    # Ensure required columns exist for app
    if not {"College","Location","Course","Future_Scope","Study_Materials","Exam_Info"}.issubset(df.columns):
        # Create dummy columns if missing
        for col in ["College","Location","Course","Future_Scope","Study_Materials","Exam_Info"]:
            if col not in df.columns:
                df[col] = ""
    return df

# -------------------------------
# User data functions
def save_user_data(data):
    try:
        df = pd.read_csv(USER_DATA_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=data.keys())
    # Remove old entry with same email
    df = df[df['email'] != data['email']]
    # Use pd.concat instead of deprecated append
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(USER_DATA_CSV, index=False)

def get_user(email, password=None):
    try:
        df = pd.read_csv(USER_DATA_CSV)
        if password:
            user = df[(df['email'] == email) & (df['password'] == password)]
        else:
            user = df[df['email'] == email]
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            return None
    except FileNotFoundError:
        return None

# -------------------------------
# Compass animation
def display_compass():
    st.image(COMPASS_GIF_PATH, width=250, caption="Career Compass 🌟", use_column_width=False)

# -------------------------------
# Career roadmap
def display_roadmap(career):
    roadmap_data = {"Step":["Step 1","Step 2","Step 3","Step 4"], "Description":[]}
    if career in ["Doctor","Engineer","Scientist"]:
        roadmap_data["Description"] = ["12th Science","BSc/BTech/MBBS","Internship/Research","Specialization/Jobs"]
    elif career in ["Accountant","Business Analyst","Economist"]:
        roadmap_data["Description"] = ["12th Commerce","BCom/BBA/Economics","Internship/Entry Job","Certifications/Higher Studies"]
    elif career in ["Writer","Designer","Teacher"]:
        roadmap_data["Description"] = ["12th Arts/Science","BA/BEd/Design","Portfolio/Practice","Jobs/Freelance/Masters"]
    elif career in ["Chef","Food Entrepreneur"]:
        roadmap_data["Description"] = ["12th","Culinary Diploma/BSc Food Tech","Apprenticeship","Own Business/Chef Jobs"]
    elif career in ["Athlete","Coach","Physiotherapist"]:
        roadmap_data["Description"] = ["School Training","Graduation/Diploma","Competitions/Training","Professional Career"]
    elif career in ["Army Officer","Navy Officer","Airforce Officer"]:
        roadmap_data["Description"] = ["12th/Graduation","Defence Academy","Field Experience","Promotion/Specialization"]
    else:
        roadmap_data["Description"] = ["Step 1","Step 2","Step 3","Step 4"]

    df = pd.DataFrame(roadmap_data)
    fig = px.timeline(df, x_start=[0,1,2,3], x_end=[1,2,3,4], y=[""]*4, text="Description")
    fig.update_yaxes(visible=False)
    fig.update_layout(title=f"{career} Roadmap", showlegend=False, paper_bgcolor='rgba(255,255,255,0.8)', plot_bgcolor='rgba(255,255,255,0.8)')
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'quiz_results' not in st.session_state:
    st.session_state.quiz_results = []
if 'show_quiz' not in st.session_state:
    st.session_state.show_quiz = False

# -------------------------------
# MAIN APP
if not st.session_state.logged_in:
    st.title("Career Compass Login / Signup")
    choice = st.radio("Choose", ["Login","Sign Up"], horizontal=True)

    if choice=="Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success(f"Welcome {user['name']}!")
            else:
                st.error("Invalid email or password")

    elif choice=="Sign Up":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Next"):
            st.session_state.temp_signup = {"email":email,"password":password}
            st.session_state.signup_step = 1

        if st.session_state.get("signup_step",0)==1:
            name = st.text_input("Full Name")
            age = st.number_input("Age", 10, 100)
            gender = st.selectbox("Gender", ["Male","Female","Other"])
            location = st.text_input("Location")
            studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"])
            avatar = st.selectbox("Choose your avatar", AVATARS)
            if st.button("Create Account"):
                data = {"email":st.session_state.temp_signup["email"],
                        "password":st.session_state.temp_signup["password"],
                        "name":name, "age":age, "gender":gender,
                        "location":location, "studying":studying,
                        "avatar":avatar, "your_paths":""}
                save_user_data(data)
                st.session_state.logged_in = True
                st.session_state.user_email = data["email"]
                st.success("Account created! Welcome!")

# -------------------------------
# AFTER LOGIN
if st.session_state.logged_in:
    user = get_user(st.session_state.user_email)
    menu = st.sidebar.radio("Navigate", ["Home","Profile","Your Paths","Career","Notifications","About Us"])

    # PROFILE
    if menu=="Profile":
        st.title("Your Profile")
        st.image(user["avatar"], width=150)
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Age:** {user['age']}")
        st.write(f"**Gender:** {user['gender']}")
        st.write(f"**Location:** {user['location']}")
        st.write(f"Currently Studying: {user['studying']}")
        if st.button("Logout"):
            st.session_state.logged_in=False
            st.session_state.user_email=""
            st.session_state.show_quiz=False
            st.success("Logged out!")

    # HOME
    elif menu=="Home":
        st.title("Welcome to Career Compass!")
        display_compass()
        st.subheader("“Education is the key to unlocking your future.”")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Take Quiz"):
                st.session_state.show_quiz=True
        with col2:
            st.info("Explore Careers in the 'Career' tab.")

    # QUIZ
    if st.session_state.show_quiz:
        st.title("Career Path Quiz")
        st.write("Answer questions to discover your optimal career paths.")
        q1 = st.selectbox("Do you enjoy Science?", ["Yes","No"])
        q2 = st.selectbox("Do you enjoy Math?", ["Yes","No"])
        q3 = st.selectbox("Do you enjoy Arts?", ["Yes","No"])
        q4 = st.selectbox("Do you enjoy helping people?", ["Yes","No"])
        if st.button("Submit Quiz"):
            score = 0
            if q1=="Yes" and q2=="Yes":
                score += 2
            if q3=="Yes":
                score += 1
            if q4=="Yes":
                score += 2
            if score>=4:
                st.success("Suggested Career: Engineer / Scientist / Doctor")
                display_roadmap("Engineer")
            elif score==3:
                st.success("Suggested Career: Teacher / Designer / Writer")
                display_roadmap("Teacher")
            else:
                st.success("Suggested Career: Business / Entrepreneurship")
                display_roadmap("Business")
            st.session_state.show_quiz=False

    # CAREER PATHS
    elif menu=="Career":
        st.title("Career Paths Explorer")
        careers = ["Doctor","Engineer","Scientist","Accountant","Business Analyst",
                   "Writer","Designer","Teacher","Chef","Food Entrepreneur",
                   "Athlete","Coach","Physiotherapist","Army Officer","Navy Officer","Airforce Officer"]
        selected = st.selectbox("Select Career", careers)
        display_roadmap(selected)

    # YOUR PATHS (saved J&K colleges)
    elif menu=="Your Paths":
        st.title("Explore Government Colleges in J&K")
        df = load_colleges()
        search = st.text_input("Search by college or course")
        if search:
            df = df[df.apply(lambda x: search.lower() in x["College"].lower() or search.lower() in x["Course"].lower(), axis=1)]
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
            <b>{row['College']}</b> - {row['Location']}<br>
            <b>Course:</b> {row['Course']}<br>
            <b>Future Scope:</b> {row['Future_Scope']}<br>
            <b>Study Materials:</b> {row['Study_Materials']}<br>
            <b>Exam Info:</b> {row['Exam_Info']}
            </div>
            """, unsafe_allow_html=True)

    # ABOUT / CONTACT
    elif menu=="About Us":
        st.title("About Career Compass")
        st.write("This platform helps students explore careers, government colleges in J&K, and chart their personal learning paths.")
        st.write("Contact: careercompass@example.com")
