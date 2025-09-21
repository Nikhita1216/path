import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_admin
from firebase_admin import credentials, auth
from PIL import Image

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# Load dataset
df_colleges = pd.read_csv("jk_colleges.csv")

# Page configuration
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="wide")

# Sidebar navigation
st.sidebar.title("Career Compass")
menu = ["Home", "Login/Signup", "Profile", "Quiz", "Careers", "Notifications", "About Us"]
choice = st.sidebar.radio("Navigate", menu)

if choice == "Home":
    st.markdown("# Career Compass 🧭")
    st.image("images/compass.gif", width=200)
    st.markdown("> Education shapes your future. Make informed choices!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Take Quiz"):
            st.session_state.page = "quiz"
    with col2:
        if st.button("Explore Careers"):
            st.session_state.page = "careers"

elif choice == "Login/Signup":
    st.header("Login or Signup")
    auth_action = st.radio("Choose action", ["Login", "Signup"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if auth_action == "Signup":
        if st.button("Create Account"):
            try:
                user = auth.create_user(email=email, password=password)
                st.success("Account created! Verify email via Firebase Console.")
            except Exception as e:
                st.error(str(e))
    elif auth_action == "Login":
        st.info("Firebase auth verification placeholder for demo.")

    st.markdown("[Forgot Password?](#)")

elif choice == "Profile":
    st.header("Your Profile")
    name = st.text_input("Name")
    age = st.number_input("Age", 10, 100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    location = st.text_input("Location")
    studying = st.selectbox("Currently Studying", ["Schooling", "Intermediate/Diploma", "BSc/BTech/BCom"])
    avatar = st.selectbox("Choose Avatar", ["avatar1.png", "avatar2.png", "avatar3.png"])
    if st.button("Save Profile"):
        st.success("Profile saved successfully!")
    if st.button("Logout"):
        st.success("Logged out!")

elif choice == "Quiz" or ('page' in st.session_state and st.session_state.page == "quiz"):
    st.header("Career Quiz")
    interests = st.multiselect("Select your interests", ["Science", "Commerce", "Arts", "Sports", "Culinary", "Defense"])
    personality = st.radio("Personality type:", ["Analytical", "Creative", "Practical"])
    if st.button("Get Suggested Careers"):
        st.write("### Suggested Careers:")
        career_map = {
            "Science": ["Scientist", "Engineer", "Doctor"],
            "Commerce": ["Accountant", "Banker", "Entrepreneur"],
            "Arts": ["Teacher", "Historian", "Journalist"],
            "Sports": ["Athlete", "Coach"],
            "Culinary": ["Chef", "Food Blogger"],
            "Defense": ["Army", "Navy", "Air Force"]
        }
        suggested = []
        for interest in interests:
            suggested += career_map.get(interest, [])
        for c in suggested:
            st.write(f"- {c}")

        st.write("### Colleges for Your Interests:")
        for interest in interests:
            st.subheader(f"{interest} Stream Colleges")
            df_filtered = df_colleges[df_colleges["Stream"] == interest]
            st.dataframe(df_filtered)

        st.write("### Career Roadmap:")
        fig = px.timeline(df_colleges, x_start="Duration", x_end="Duration", y="Course Name", color="Stream")
        st.plotly_chart(fig)

elif choice == "Careers" or ('page' in st.session_state and st.session_state.page == "careers"):
    st.header("Explore Careers & Colleges")
    career_filter = st.multiselect("Filter careers:", ["Science", "Commerce", "Arts", "Sports", "Culinary", "Defense"])
    for career in career_filter:
        st.subheader(f"{career} Careers")
        colleges = df_colleges[df_colleges["Stream"] == career]
        st.dataframe(colleges)

elif choice == "Notifications":
    st.header("Notifications")
    st.write("No new notifications yet!")

elif choice == "About Us":
    st.header("About Career Compass")
    st.write("""
    Career Compass is a personalized guidance platform for students in Jammu & Kashmir.
    It helps students choose courses, find government colleges, explore career paths,
    and plan their academic journey effectively.
    """)

