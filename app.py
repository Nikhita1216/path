import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
# Streamlit CSS for pastel UI, cards, buttons
st.markdown(
    """
    <style>
    /* Background & font */
    .main {
        background-color: #fef6f0;
        color: #333333;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8eaf6;
    }
    /* Buttons */
    div.stButton > button {
        background-color: #ffd6f0;
        color: #333;
        border-radius: 12px;
        padding: 8px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }
    /* Cards */
    .card {
        background-color: #fff1f3;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: scale(1.02);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    df = df[df['email'] != data['email']]
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
    if os.path.exists(COMPASS_GIF_PATH):
        st.image(COMPASS_GIF_PATH, width=250, caption="Career Compass 🌟", use_column_width=False)

# -------------------------------
# Career roadmap (Plotly)
def display_roadmap(career):
    roadmap_data = {
        "Step": ["Step 1", "Step 2", "Step 3", "Step 4"],
        "Description": []
    }
    if career in ["Doctor", "Engineer", "Scientist"]:
        roadmap_data["Description"] = ["12th Science", "BSc/BTech/MBBS", "Internship/Research", "Specialization/Jobs"]
    elif career in ["Accountant", "Business Analyst", "Economist"]:
        roadmap_data["Description"] = ["12th Commerce", "BCom/BBA/Economics", "Internship/Entry Job", "Certifications/Higher Studies"]
    elif career in ["Writer", "Designer", "Teacher"]:
        roadmap_data["Description"] = ["12th Arts/Science", "BA/BEd/Design", "Portfolio/Practice", "Jobs/Freelance/Masters"]
    elif career in ["Chef", "Food Entrepreneur"]:
        roadmap_data["Description"] = ["12th", "Culinary Diploma/BSc Food Tech", "Apprenticeship", "Own Business/Chef Jobs"]
    elif career in ["Athlete", "Coach", "Physiotherapist"]:
        roadmap_data["Description"] = ["School Training", "Graduation/Diploma", "Competitions/Training", "Professional Career"]
    elif career in ["Army Officer", "Navy Officer", "Airforce Officer"]:
        roadmap_data["Description"] = ["12th/Graduation", "Defence Academy", "Field Experience", "Promotion/Specialization"]
    else:
        roadmap_data["Description"] = ["Step 1", "Step 2", "Step 3", "Step 4"]

    df = pd.DataFrame(roadmap_data)
    fig = px.timeline(df, x_start=[0,1,2,3], x_end=[1,2,3,4], y=[""]*4, text="Description")
    fig.update_yaxes(visible=False)
    fig.update_layout(title=f"{career} Roadmap", showlegend=False, paper_bgcolor='rgba(255,255,255,0.8)', plot_bgcolor='rgba(255,255,255,0.8)')
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Session state initialization
for key in ['logged_in','user_email','quiz_results','quiz','explore']:
    if key not in st.session_state:
        st.session_state[key] = False
if 'user_profile_setup' not in st.session_state:
    st.session_state['user_profile_setup'] = False

# -------------------------------
# LOGIN / SIGNUP
if not st.session_state['logged_in']:
    st.title("Career Compass Login / Signup")
    choice = st.radio("Choose", ["Login", "Sign Up"])

    if choice == "Sign Up":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if email and password:
                if get_user(email):
                    st.error("Email already exists")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_profile_setup'] = False
                    save_user_data({"email": email, "password": password, "your_paths": "", "avatar": AVATARS[0]})
                    st.experimental_rerun()
            else:
                st.warning("Please enter email and password")

    if choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email,password)
            if user is not None:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.success(f"Welcome {user.get('name','User')}!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

# -------------------------------
# AFTER LOGIN
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])

    # PROFILE SETUP (after signup)
    if not st.session_state['user_profile_setup']:
        st.title("Complete Your Profile")
        name = st.text_input("Full Name", value=user.get('name',''))
        age = st.number_input("Age", 10, 100, value=int(user.get('age',18)) if user.get('age') else 18)
        gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(user.get('gender','Male')))
        location = st.text_input("Location", value=user.get('location',''))
        studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"], index=0)
        avatar = st.selectbox("Choose your avatar", AVATARS)

        if st.button("Save Profile"):
            user.update({"name": name, "age": age, "gender": gender, "location": location, "studying": studying, "avatar": avatar})
            save_user_data(user)
            st.session_state['user_profile_setup'] = True
            st.experimental_rerun()

    else:
        # Sidebar Menu
        st.sidebar.title("Career Compass")
        menu = st.sidebar.radio("Navigate", ["Home","Profile","Your Paths","Career","Notifications","About Us"])

        # PROFILE
        if menu=="Profile":
            st.title("Your Profile")
            st.markdown(f'<img src="{user["avatar"]}" width="150" style="border-radius:50%;">', unsafe_allow_html=True)
            st.write(f"**Name:** {user['name']}")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Age:** {user['age']}")
            st.write(f"**Gender:** {user['gender']}")
            st.write(f"Location: {user['location']}")
            st.write(f"Currently Studying: {user['studying']}")
            if st.button("Logout"):
                st.session_state['logged_in'] = False
                st.session_state['user_email'] = ""
                st.experimental_rerun()

        # HOME
        elif menu=="Home":
            st.title("Welcome to Career Compass 🌟")
            display_compass()
            st.write("Explore careers, quizzes, colleges, and build your roadmap!")

        # CAREER
        elif menu=="Career":
            st.title("Career Roadmap & Quiz")
            st.subheader("Take a quiz to discover your path")
            if "quiz_index" not in st.session_state:
                st.session_state['quiz_index'] = 0
                st.session_state['quiz_score'] = 0
                st.session_state['quiz'] = [
                    {"q":"Do you enjoy problem solving?","a":["Yes","No"]},
                    {"q":"Do you like working in teams?","a":["Yes","No"]},
                    {"q":"Are you good at science?","a":["Yes","No"]},
                    {"q":"Do you enjoy creative work?","a":["Yes","No"]},
                ]
            if st.session_state['quiz_index'] < len(st.session_state['quiz']):
                q = st.session_state['quiz'][st.session_state['quiz_index']]
                ans = st.radio(q['q'], q['a'], key=st.session_state['quiz_index'])
                if st.button("Next"):
                    if ans=="Yes":
                        st.session_state['quiz_score'] += 1
                    st.session_state['quiz_index'] += 1
                    st.session_state['rerun_quiz'] = True
            else:
                st.success(f"Quiz Completed! Score: {st.session_state['quiz_score']}")
                if st.session_state['quiz_score']>=3:
                    career = "Engineer/Scientist"
                else:
                    career = "Creative/Arts"
                display_roadmap(career)

            if st.session_state.get('rerun_quiz'):
                st.session_state['rerun_quiz'] = False
                st.experimental_rerun()

        # YOUR PATHS
        elif menu=="Your Paths":
            st.title("Your Saved Career Paths")
            paths = user.get("your_paths","")
            st.write(paths if paths else "No paths saved yet.")

        # NOTIFICATIONS
        elif menu=="Notifications":
            st.title("Notifications")
            st.info("No new notifications.")

        # ABOUT US
        elif menu=="About Us":
            st.title("About Career Compass")
            st.markdown("""
            **Career Compass** helps students explore careers, colleges, and build roadmaps.
            Contact: careercompass@example.com
            """)

        # COLLEGES (optional section)
        st.sidebar.subheader("Explore J&K Colleges")
        explore_colleges = st.sidebar.checkbox("Show Colleges")
        if explore_colleges:
            colleges_df = load_colleges()
            st.title("Government Colleges in J&K")
            st.dataframe(colleges_df)

