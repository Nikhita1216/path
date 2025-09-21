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
COLLEGES_CSV = "jk_colleges_final.csv"  # CSV with College, Location, Course, Future_Scope, Study_Materials, Exam_Info
USER_DATA_CSV = "users.csv"

# -------------------------------
# Streamlit CSS for better UI
st.markdown("""
<style>
body {
    background-color: #fef6f0;
    color: #333333;
    font-family: 'Arial', sans-serif;
}
.stButton>button {
    background-color: #ffd6f0;
    color: #333;
    border-radius: 12px;
    padding: 8px 20px;
    font-size: 16px;
    font-weight: bold;
    transition: transform 0.2s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
}
.card {
    background-color: #fff1f3;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load colleges
@st.cache_data
def load_colleges():
    df = pd.read_csv(COLLEGES_CSV)
    return df

# -------------------------------
# Save/get user data
def save_user_data(data):
    try:
        df = pd.read_csv(USER_DATA_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=data.keys())
    df = df[df['email'] != data['email']]  # remove old record if exists
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(USER_DATA_CSV, index=False)

def get_user(email, password=None):
    try:
        df = pd.read_csv(USER_DATA_CSV)
        if password:
            user = df[(df['email'] == email) & (df['password'] == password)]
        else:
            user = df[(df['email'] == email)]
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            return None
    except FileNotFoundError:
        return None

# -------------------------------
# Display compass animation
def display_compass():
    st.image(COMPASS_GIF_PATH, width=100, caption="Career Compass 🌟")

# -------------------------------
# Career roadmap
def display_roadmap(career):
    roadmap_data = {
        "Step": ["Step 1", "Step 2", "Step 3", "Step 4"],
        "Description": []
    }
    if career in ["Doctor","Engineer","Scientist"]:
        roadmap_data["Description"] = ["12th Science", "BSc/BTech/MBBS", "Internship/Research", "Specialization/Jobs"]
    elif career in ["Accountant","Business Analyst","Economist"]:
        roadmap_data["Description"] = ["12th Commerce", "BCom/BBA/Economics", "Internship/Entry Job", "Certifications/Higher Studies"]
    elif career in ["Writer","Designer","Teacher"]:
        roadmap_data["Description"] = ["12th Arts/Science", "BA/BEd/Design", "Portfolio/Practice", "Jobs/Freelance/Masters"]
    elif career in ["Chef","Food Entrepreneur"]:
        roadmap_data["Description"] = ["12th", "Culinary Diploma/BSc Food Tech", "Apprenticeship", "Own Business/Chef Jobs"]
    elif career in ["Athlete","Coach","Physiotherapist"]:
        roadmap_data["Description"] = ["School Training", "Graduation/Diploma", "Competitions/Training", "Professional Career"]
    elif career in ["Army Officer","Navy Officer","Airforce Officer"]:
        roadmap_data["Description"] = ["12th/Graduation", "Defence Academy", "Field Experience", "Promotion/Specialization"]
    else:
        roadmap_data["Description"] = ["Step 1", "Step 2", "Step 3", "Step 4"]

    df = pd.DataFrame(roadmap_data)
    fig = px.timeline(df, x_start=[0,1,2,3], x_end=[1,2,3,4], y=[""]*4, text="Description")
    fig.update_yaxes(visible=False)
    fig.update_layout(title=f"{career} Roadmap", showlegend=False, paper_bgcolor='rgba(255,255,255,0.8)', plot_bgcolor='rgba(255,255,255,0.8)')
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Initialize session state
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = ""
if 'quiz_results' not in st.session_state: st.session_state['quiz_results'] = []
if 'quiz_index' not in st.session_state: st.session_state['quiz_index'] = 0
if 'show_quiz' not in st.session_state: st.session_state['show_quiz'] = False

# -------------------------------
# Login / Signup
if not st.session_state['logged_in']:
    st.title("Career Compass")
    choice = st.radio("Choose", ["Login","Sign Up"])
    if choice=="Sign Up":
        st.subheader("Create New Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if email and password:
                user_data = {
                    "email": email,
                    "password": password,
                    "name": "",
                    "age": 0,
                    "gender": "",
                    "location": "",
                    "studying": "",
                    "avatar": "",
                    "your_paths": ""
                }
                save_user_data(user_data)
                st.success("Account created! Please login.")
    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email,password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
            else:
                st.error("Invalid email/password")

# -------------------------------
# Main App after login
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])
    st.sidebar.title("Career Compass")
    menu = st.sidebar.radio("career compass", ["Profile","Home","Your Paths","Explore","Notifications","About Us"])

    # -------------------------------
    # Profile
    if menu=="Profile":
        st.title("Your Profile")
        if not user['name']:
            st.subheader("Complete Your Profile")
            user['name'] = st.text_input("Full Name")
            user['age'] = st.number_input("Age",10,100)
            user['gender'] = st.selectbox("Gender",["Male","Female","Other"])
            user['location'] = st.text_input("Location")
            user['studying'] = st.selectbox("Currently Studying", ["Schooling","Intermediate","BTech/BSc","Other"])
            st.subheader("Choose your avatar")
            avatar_choice = st.radio("Avatar", AVATARS, format_func=lambda x: f"![avatar]({x})")
            user['avatar'] = avatar_choice
            if st.button("Save Profile"):
                save_user_data(user)
                st.success("Profile saved!")
        else:
            st.image(user['avatar'], width=150)
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Age:** {user['age']}")
            st.write(f"**Gender:** {user['gender']}")
            st.write(f"Location: {user['location']}")
            st.write(f"Currently Studying: {user['studying']}")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.session_state['user_email'] = ""

    # -------------------------------
    # Home
    if menu=="Home":
        st.title("Welcome to Career Compass!")
        display_compass()
        col1,col2 = st.columns(2)
        with col1:
            if st.button("Take Quiz"):
                st.session_state['show_quiz'] = True
                st.session_state['quiz_index'] = 0
                st.session_state['quiz_results'] = []
        with col2:
            st.write("Explore careers, colleges, and more!")

    # -------------------------------
    # Quiz
    if st.session_state['show_quiz']:
        quiz_questions = [
            {"q":"Which field interests you most?","options":["Science","Commerce","Arts","Sports","Culinary","Business","Technology","Defense","Creative Arts"],"type":"multiselect"},
            {"q":"Structured or creative work?","options":["Structured","Creative","Both"],"type":"radio"},
            {"q":"Teamwork or Solo?","options":["Teamwork","Solo","Both"],"type":"radio"}
        ]
        idx = st.session_state['quiz_index']
        question = quiz_questions[idx]
        st.title("Career Quiz")
        st.write(question["q"])
        answer = st.multiselect("Choose:", question["options"]) if question["type"]=="multiselect" else st.radio("Choose:", question["options"])
        if st.button("Next"):
            st.session_state['quiz_results'] += answer if isinstance(answer,list) else [answer]
            if idx+1 < len(quiz_questions):
                st.session_state['quiz_index'] +=1
            else:
                st.success(f"Quiz completed! Your selections: {st.session_state['quiz_results']}")
                st.session_state['show_quiz'] = False
                    # -------------------------------
    # Career / Roadmaps
    if menu=="Explore":
        st.title("Explore careers")
        careers = ["Doctor","Engineer","Scientist","Accountant","Business Analyst","Economist",
                   "Writer","Designer","Teacher","Chef","Food Entrepreneur",
                   "Athlete","Coach","Physiotherapist","Army Officer","Navy Officer","Airforce Officer"]
        career_choice = st.selectbox("Select a career to view roadmap", careers)
        if career_choice:
            display_roadmap(career_choice)

    # -------------------------------
    # Your Paths / Colleges
    if menu=="Your Paths":
        st.title("J&K Government Colleges")
        colleges_df = load_colleges()
        filter_course = st.selectbox("Filter by course", ["All"] + sorted(colleges_df['Course'].unique()))
        if filter_course != "All":
            colleges_df = colleges_df[colleges_df['Course'] == filter_course]

        for _, row in colleges_df.iterrows():
            st.markdown(f"""
            <div class="card">
            **College:** {row['College']}  \n
            **Location:** {row['Location']}  \n
            **Course:** {row['Course']}  \n
            **Future Scope:** {row['Future_Scope']}  \n
            **Study Materials:** {row['Study_Materials']}  \n
            **Exam Info:** {row['Exam_Info']}
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------
    # Notifications
    if menu=="Notifications":
        st.title("Notifications")
        notifications = [
            "New careers added in roadmap section!",
            "Colleges data refreshed with latest courses."
        ]
        for note in notifications:
            st.info(note)

    # -------------------------------
    # About Us
    if menu=="About Us":
        st.title("About Career Compass 🌟")
        st.markdown("""
        Career Compass is your personal guide to discovering career paths, exploring colleges,
        and planning your roadmap to success. 🎯  

        Features:
        - Personalized Career Quiz
        - J&K Government Colleges info
        - Career Roadmaps for multiple fields
        - Notifications & updates
        - Profile customization with avatars
        - Fun pastel UI
        """)
        st.image(COMPASS_GIF_PATH, width=200)

