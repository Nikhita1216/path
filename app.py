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
    .main {background-color: #fef6f0; color: #333333;}
    .css-1d391kg {background-color: #f8eaf6;}
    div.stButton > button {
        background-color: #ffd6f0; color: #333; border-radius: 12px;
        padding: 8px 20px; font-size: 16px; font-weight: bold; transition: transform 0.2s;
    }
    div.stButton > button:hover {transform: scale(1.05); box-shadow: 0px 4px 8px rgba(0,0,0,0.2);}
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
    if os.path.exists(COLLEGES_CSV):
        df = pd.read_csv(COLLEGES_CSV)
        return df
    return pd.DataFrame(columns=["College","Location","Course","Future_Scope","Study_Materials","Exam_Info"])

# -------------------------------
# User data management
def save_user_data(data):
    if os.path.exists(USER_DATA_CSV):
        df = pd.read_csv(USER_DATA_CSV)
        df = df[df['email'] != data['email']]
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_csv(USER_DATA_CSV, index=False)

def get_user(email, password=None):
    if os.path.exists(USER_DATA_CSV):
        df = pd.read_csv(USER_DATA_CSV)
        if password:
            user = df[(df['email'] == email) & (df['password'] == password)]
        else:
            user = df[df['email'] == email]
        if not user.empty:
            return user.iloc[0].to_dict()
    return None

# -------------------------------
# Display compass
def display_compass():
    if os.path.exists(COMPASS_GIF_PATH):
        st.image(COMPASS_GIF_PATH, width=250, caption="Career Compass 🌟", use_column_width=False)

# -------------------------------
# Career roadmap
def display_roadmap(career):
    roadmap_data = {
        "Step": ["Step 1", "Step 2", "Step 3", "Step 4"],
        "Description": []
    }
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
# Initialize session state
if 'logged_in' not in st.session_state: st.session_state['logged_in']=False
if 'user_email' not in st.session_state: st.session_state['user_email']=""
if 'quiz_results' not in st.session_state: st.session_state['quiz_results']=[]

# -------------------------------
# Sidebar
if st.session_state['logged_in']:
    st.sidebar.title("Career Compass")
    menu = st.sidebar.radio("Navigate", ["Home","Profile","Your Paths","Career","Notifications","About Us"])
else:
    menu = None

# -------------------------------
# LOGIN / SIGNUP
if not st.session_state['logged_in']:
    st.title("Career Compass Login / Signup")
    choice = st.radio("Choose", ["Login","Sign Up"])
    
    if choice=="Sign Up":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if email and password:
                data = {"name":"New User","email":email,"password":password,"age":0,"gender":"Other","location":"","studying":"Schooling","avatar":AVATARS[0],"your_paths":""}
                save_user_data(data)
                st.success("Account created! You are now logged in.")
                st.session_state['logged_in']=True
                st.session_state['user_email']=email
                st.experimental_rerun()
            else:
                st.warning("Please enter email and password.")

    if choice=="Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email,password)
            if user:
                st.session_state['logged_in']=True
                st.session_state['user_email']=email
                st.success(f"Welcome {user['name']}!")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

# -------------------------------
# AFTER LOGIN
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])

    # PROFILE
    if menu=="Profile":
        st.title("Your Profile")
        st.image(user["avatar"], width=150)
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Age:** {user['age']}")
        st.write(f"**Gender:** {user['gender']}")
        st.write(f"Location: {user['location']}")
        st.write(f"Currently Studying: {user['studying']}")
        if st.button("Logout"):
            st.session_state['logged_in']=False
            st.session_state['user_email']=""
            st.experimental_rerun()

    # HOME
    elif menu=="Home":
        st.title("Welcome to Career Compass!")
        display_compass()
        st.subheader("“Education is the key to unlocking your future.”")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Take Quiz"):
                st.session_state['quiz']=True
        with col2:
            if st.button("Explore Careers"):
                st.session_state['explore']=True

    # QUIZ
    if 'quiz' in st.session_state and st.session_state['quiz']:
        st.title("Career Path Quiz")
        st.write("Answer questions to discover your optimal career paths!")
        interests = st.multiselect("Select your interests", ["Science","Commerce","Arts","Sports","Culinary","Business","Technology","Defense Services","Creative Arts"])
        personality = st.radio("Do you prefer structured or creative work?", ["Structured","Creative","Both"])
        work_style = st.radio("Teamwork or Solo work?", ["Teamwork","Solo","Both"])
        if st.button("Get Suggested Careers"):
            results=[]
            if "Science" in interests: results+=["Doctor","Engineer","Scientist"]
            if "Commerce" in interests: results+=["Accountant","Business Analyst","Economist"]
            if "Arts" in interests: results+=["Writer","Designer","Teacher"]
            if "Sports" in interests: results+=["Athlete","Coach","Physiotherapist"]
            if "Culinary" in interests: results+=["Chef","Food Entrepreneur"]
            if "Defense Services" in interests: results+=["Army Officer","Navy Officer","Airforce Officer"]
            if "Creative Arts" in interests: results+=["Actor","Musician","Graphic Designer"]
            st.session_state['quiz_results']=list(set(results))
            paths=user.get('your_paths',"")
            for c in st.session_state['quiz_results']:
                if paths: paths+=f";{c}"
                else: paths=c
            user['your_paths']=paths
            save_user_data(user)
            st.success("Suggested careers saved to 'Your Paths'")
            st.session_state['quiz']=False
            st.experimental_rerun()

    # YOUR PATHS
    elif menu=="Your Paths":
        st.title("Your Saved Career Paths")
        paths=user.get('your_paths',"")
        if paths:
            paths_list=paths.split(";")
            df=load_colleges()
            for career in paths_list:
                st.markdown(f'<div class="card"><h4>{career}</h4></div>', unsafe_allow_html=True)
                display_roadmap(career)
                filtered=df[df['Course'].str.contains(career.split()[0],case=False,na=False)]
                for idx,row in filtered.iterrows():
                    st.markdown(f"""
                        <div class="card">
                            <h5>{row['College']} ({row['Location']})</h5>
                            <p><b>Future Scope:</b> {row['Future_Scope']}</p>
                            <p><b>Study Material:</b> <a href="{row['Study_Materials']}" target="_blank">Link</a></p>
                            <p><b>Exam Info:</b> {row['Exam_Info']}</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No career paths saved yet. Take the quiz!")

    # CAREER EXPLORER
    elif menu=="Career":
        st.title("Explore Careers & Colleges")
        df=load_colleges()
        course_filter = st.selectbox("Select Course/Career", df['Course'].unique())
        filtered=df[df['Course'].str.contains(course_filter,case=False,na=False)]
        for idx,row in filtered.iterrows():
            st.markdown(f"""
                <div class="card">
                    <h5>{row['College']} ({row['Location']})</h5>
                    <p><b>Future Scope:</b> {row['Future_Scope']}</p>
                    <p><b>Study Material:</b> <a href="{row['Study_Materials']}" target="_blank">Link</a></p>
                    <p><b>Exam Info:</b> {row['Exam_Info']}</p>
                </div>
            """, unsafe_allow_html=True)

    # NOTIFICATIONS
    elif menu=="Notifications":
        st.title("Notifications")
        st.info("No new notifications. All your career paths and updates appear here.")

    # ABOUT US
    elif menu=="About Us":
        st.title("About Career Compass")
        st.write("Career Compass is your ultimate tool to discover and plan your future career paths!")
        st.subheader("Contact Info")
        st.write("Email: info@careercompass.com")
        st.write("Phone: +91-9876543210")
        st.write("Website: www.careercompass.com")
        st.write("Address: Jammu & Kashmir, India")
