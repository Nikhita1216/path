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
# Streamlit CSS for pastel UI
st.markdown(
    """
    <style>
    /* Main background & font */
    .main {background-color: #fef6f0; color: #333333;}
    /* Sidebar */
    .css-1d391kg {background-color: #f8eaf6;}
    /* Buttons */
    div.stButton > button {
        background-color: #ffd6f0; color: #333;
        border-radius: 12px; padding: 8px 20px;
        font-size: 16px; font-weight: bold; transition: transform 0.2s;
    }
    div.stButton > button:hover {transform: scale(1.05); box-shadow: 0px 4px 8px rgba(0,0,0,0.2);}
    /* Cards */
    .card {
        background-color: #fff1f3; border-radius: 12px; padding: 15px; margin: 10px 0;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1); transition: transform 0.2s;
    }
    .card:hover {transform: scale(1.02); box-shadow: 0px 4px 10px rgba(0,0,0,0.15);}
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
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USER_DATA_CSV, index=False)

def get_user(email, password=None):
    try:
        df = pd.read_csv(USER_DATA_CSV)
        if password:
            user = df[(df['email'] == email) & (df['password'] == password)]
        else:
            user = df[(df['email'] == email)]
        if not user.empty:
            return user.iloc[0]
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
    roadmap_data = {"Step": ["Step 1", "Step 2", "Step 3", "Step 4"], "Description": []}
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
# Session state
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_email' not in st.session_state: st.session_state['user_email'] = ""
if 'quiz_results' not in st.session_state: st.session_state['quiz_results'] = []

# -------------------------------
# SIGNUP / LOGIN FLOW
st.title("Career Compass")
if not st.session_state['logged_in']:
    choice = st.radio("Choose action", ["Login", "Sign Up"])

    if choice=="Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email, password)
            if user is not None:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.success(f"Welcome {user['name']}!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

    if choice=="Sign Up":
        st.subheader("Sign Up")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Proceed to Profile"):
            if email and password:
                # Save minimal info
                data = {"email": email, "password": password}
                save_user_data(data)
                st.session_state['user_email'] = email
                st.session_state['logged_in'] = True
                st.experimental_rerun()
            else:
                st.error("Enter email and password")

# -------------------------------
# AFTER LOGIN
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])

    # Sidebar menu
    menu = st.sidebar.radio("Navigate", ["Home","Profile","Your Paths","Career","Notifications","About Us"])

    # PROFILE
    if menu=="Profile":
        st.title("Your Profile")
        # If profile details missing, ask for them
        if pd.isna(user.get('name')) or 'avatar' not in user:
            st.info("Complete your profile")
            name = st.text_input("Full Name", user.get('name',""))
            age = st.number_input("Age", 10, 100, value=int(user.get('age',18)))
            gender = st.selectbox("Gender", ["Male","Female","Other"])
            location = st.text_input("Location", user.get('location',""))
            studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"])
            avatar = st.selectbox("Choose your avatar", AVATARS)
            if st.button("Save Profile"):
                user_data = {
                    "name": name, "age": age, "gender": gender, "location": location,
                    "studying": studying, "avatar": avatar, "email": user['email'], "password": user['password'],
                    "your_paths": user.get('your_paths',"")
                }
                save_user_data(user_data)
                st.success("Profile updated!")
                st.experimental_rerun()
        else:
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
        st.title("Welcome to Career Compass!")
        display_compass()
        st.subheader("“Education is the key to unlocking your future.”")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Take Quiz"):
                st.session_state['quiz'] = True
                st.experimental_rerun()
        with col2:
            if st.button("Explore Careers"):
                st.session_state['explore'] = True
                st.experimental_rerun()

    # YOUR PATHS
    elif menu=="Your Paths":
        st.title("Your Career Paths")
        if pd.isna(user.get('your_paths')) or user.get('your_paths')=="":
            st.info("You haven't added any paths yet!")
        else:
            st.write(user.get('your_paths'))

    # CAREER
    elif menu=="Career":
        st.title("Explore Careers & Colleges")
        career = st.selectbox("Choose career", ["Doctor","Engineer","Scientist","Accountant","Business Analyst","Writer","Chef","Athlete","Army Officer"])
        display_roadmap(career)
        st.subheader("Recommended Colleges in J&K")
        df_colleges = load_colleges()
        st.dataframe(df_colleges)

   # NOTIFICATIONS / Colleges
    elif menu=="Notifications":
        st.title("Government Colleges in J&K")
        df = load_colleges()
        st.dataframe(df)

    # ABOUT US
    elif menu=="About Us":
        st.title("About Career Compass")
        st.write("""
        Career Compass is your AI-powered assistant to help explore career paths, education options, and colleges in Jammu & Kashmir.
        """)
        st.subheader("Contact us:")
        st.write("Email: support@careercompass.com")
        st.write("Phone: +91-9876543210")
