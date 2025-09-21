import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Paths and Data
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
st.markdown("""
<style>
body {
    background-color: #fef6f0;
    color: #333333;
}
.css-1d391kg { background-color: #f8eaf6; }
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
""", unsafe_allow_html=True)

# -------------------------------
# Load colleges
@st.cache_data
def load_colleges():
    return pd.read_csv(COLLEGES_CSV)

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
            user = df[df['email'] == email]
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            return None
    except FileNotFoundError:
        return None

# -------------------------------
# Display compass animation
def display_compass():
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
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'quiz_results' not in st.session_state:
    st.session_state['quiz_results'] = []
if 'quiz_active' not in st.session_state:
    st.session_state['quiz_active'] = False

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
            # Check if user already exists
            if get_user(email):
                st.error("User already exists. Please login.")
            else:
                data = {
                    "name": "",
                    "email": email,
                    "password": password,
                    "age": "",
                    "gender": "",
                    "location": "",
                    "studying": "",
                    "avatar": AVATARS[0],
                    "your_paths": ""
                }
                save_user_data(data)
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.success("Account created! Complete your profile below.")

    elif choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = get_user(email,password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.success(f"Welcome {user.get('name','')}!")
            else:
                st.error("Invalid email or password.")

# -------------------------------
# AFTER LOGIN
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])

    # Sidebar
    st.sidebar.title("Career Compass")
    menu = st.sidebar.radio("Navigate", ["Home","Profile","Your Paths","Career","Notifications","About Us"])

    # -------------------------------
    # PROFILE
    if menu=="Profile":
        st.title("Your Profile")
        avatar = user.get("avatar", AVATARS[0])
        st.markdown(f'<img src="{avatar}" width="150" style="border-radius:50%;">', unsafe_allow_html=True)
        user["name"] = st.text_input("Full Name", value=user.get("name",""))
        user["age"] = st.text_input("Age", value=user.get("age",""))
        user["gender"] = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(user.get("gender","Male")) if user.get("gender") else 0)
        user["location"] = st.text_input("Location", value=user.get("location",""))
        user["studying"] = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"], index=["Schooling","Intermediate/Diploma","BTech/BSc","Other"].index(user.get("studying","Schooling")))
        user["avatar"] = st.selectbox("Choose your avatar", AVATARS, index=AVATARS.index(user.get("avatar", AVATARS[0])))

        if st.button("Save Profile"):
            save_user_data(user)
            st.success("Profile updated!")

        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = ""
            st.experimental_rerun()

    # -------------------------------
    # HOME
    elif menu=="Home":
        st.title("Welcome to Career Compass 🌟")
        display_compass()
        st.info("Use the sidebar to navigate to your profile, career paths, quizzes, and colleges in J&K.")

    # -------------------------------
    # YOUR PATHS
    elif menu=="Your Paths":
        st.title("Your Career Paths")
        paths = user.get("your_paths","")
        st.write("Saved paths:", paths)

    # -------------------------------
    # CAREER
    elif menu=="Career":
        st.title("Career Guidance")
        career_choice = st.selectbox("Select a career", ["Doctor","Engineer","Scientist","Teacher","Writer","Designer","Accountant","Business Analyst","Chef","Athlete","Army Officer","Other"])
        if st.button("Show Roadmap"):
            display_roadmap(career_choice)

        st.subheader("J&K Government Colleges")
        df_colleges = load_colleges()
        st.dataframe(df_colleges[["College","Location","Course","Future_Scope"]].head(50))

    # -------------------------------
    # NOTIFICATIONS
    elif menu=="Notifications":
        st.title("Notifications")
        st.info("No new notifications yet.")

    # -------------------------------
    # ABOUT US
    elif menu=="About Us":
        st.title("About Career Compass")
        st.markdown("""
        Career Compass is your personal guide for choosing career paths, exploring government colleges in J&K, quizzes, and roadmap visualizations.
        """)
        st.subheader("Contact")
        st.write("Email: support@careercompass.com")
        st.write("Phone: +91 98765 43210")
