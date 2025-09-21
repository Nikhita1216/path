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
st.markdown("""
<style>
/* General background */
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
# Session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""
if 'quiz_index' not in st.session_state:
    st.session_state['quiz_index'] = 0
if 'quiz_results' not in st.session_state:
    st.session_state['quiz_results'] = []
if 'quiz_answers' not in st.session_state:
    st.session_state['quiz_answers'] = []

# -------------------------------
# Login / Signup
if not st.session_state['logged_in']:
    st.title("Career Compass ")
    choice = st.radio("Choose", ["Login", "Sign Up"])
    
    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = get_user(email,password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")
    
    elif choice == "Sign Up":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if email and password and st.button("Sign Up"):
            data = {
                "email": email,
                "password": password,
                "name": "",
                "age": 0,
                "gender": "",
                "location": "",
                "studying": "",
                "avatar": AVATARS[0],
                "your_paths": ""
            }
            save_user_data(data)
            st.success("Account created! Please login.")
            st.experimental_rerun()

# -------------------------------
# Main app after login
if st.session_state['logged_in']:
    user = get_user(st.session_state['user_email'])
    
    # Sidebar
    st.sidebar.title("Career Compass")
    menu = st.sidebar.radio("Navigate", ["Home","Profile","Quiz","Your Paths","Career","Notifications","About Us"])
    
    # ----------- HOME -----------
    if menu=="Home":
        st.title(f"Welcome, {user['name'] if user['name'] else user['email']}!")
        display_compass()
        st.subheader("“Education is the key to unlocking your future.”")
        col1,col2 = st.columns(2)
        with col1:
            if st.button("Take Quiz"):
                st.session_state['quiz_index'] = 0
                st.session_state['quiz_answers'] = []
                st.session_state['quiz_results'] = []
                st.experimental_rerun()
        with col2:
            if st.button("Explore Careers"):
                st.session_state['explore'] = True
                st.experimental_rerun()
    
    # ----------- PROFILE -----------
    elif menu=="Profile":
        st.title("Your Profile")
        st.image(user['avatar'], width=150)
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Age:** {user['age']}")
        st.write(f"**Gender:** {user['gender']}")
        st.write(f"**Location:** {user['location']}")
        st.write(f"Currently Studying: {user['studying']}")
        if st.button("Logout"):
            st.session_state['logged_in']=False
            st.session_state['user_email']=""
            st.experimental_rerun()
    
    # ----------- QUIZ -----------
    elif menu=="Quiz" or ('quiz_index' in st.session_state and st.session_state['quiz_index']<3):
        questions = [
            {"q":"What subjects interest you the most?", "options":["Science","Commerce","Arts","Sports","Culinary","Business","Technology","Defense Services","Creative Arts"]},
            {"q":"Do you prefer structured or creative work?", "options":["Structured","Creative","Both"]},
            {"q":"Do you prefer working in a team or alone?", "options":["Teamwork","Solo","Both"]}
        ]
        idx = st.session_state['quiz_index']
        st.title("Career Path Quiz")
        st.write(questions[idx]['q'])
        answer = st.radio("Select one:", questions[idx]['options'])
        if st.button("Next"):
            st.session_state['quiz_answers'].append(answer)
            st.session_state['quiz_index'] += 1
            st.experimental_rerun()
        if st.session_state['quiz_index']>=len(questions):
            # Generate career suggestions
            results=[]
            interests = st.session_state['quiz_answers'][0] if len(st.session_state['quiz_answers'])>0 else ""
            if "Science" in interests: results+=["Doctor","Engineer","Scientist"]
            if "Commerce" in interests: results+=["Accountant","Business Analyst","Economist"]
            if "Arts" in interests: results+=["Writer","Designer","Teacher"]
            if "Sports" in interests: results+=["Athlete","Coach","Physiotherapist"]
            if "Culinary" in interests: results+=["Chef","Food Entrepreneur"]
            if "Defense Services" in interests: results+=["Army Officer","Navy Officer","Airforce Officer"]
            if "Creative Arts" in interests: results+=["Actor","Musician","Graphic Designer"]
            st.session_state['quiz_results']=list(set(results))
            # Save to user
            paths=user.get('your_paths',"")
            for c in st.session_state['quiz_results']:
                if paths: paths+=f";{c}"
                else: paths=c
            user['your_paths']=paths
            save_user_data(user)
            st.success("Suggested careers saved to 'Your Paths'")
            st.session_state['quiz_index']=0
            st.session_state['quiz_answers']=[]
    
    # ----------- YOUR PATHS -----------
    elif menu=="Your Paths":
        st.title("Your Suggested Careers")
        paths = user.get('your_paths',"").split(";")
        if paths==[""] or not paths:
            st.info("No paths suggested yet. Take the quiz first!")
        else:
            for c in paths:
                st.subheader(c)
                display_roadmap(c)
    
    # ----------- CAREER -----------
    elif menu=="Career":
        st.title("Career Exploration")
        careers = ["Doctor","Engineer","Scientist","Accountant","Business Analyst","Economist","Writer","Designer","Teacher","Chef","Athlete","Defense Services"]
        selected = st.selectbox("Choose a career to explore", careers)
        st.write(f"**Career:** {selected}")
        display_roadmap(selected)
    
    # ----------- NOTIFICATIONS -----------
    elif menu=="Notifications":
        st.title("Notifications")
        if st.session_state['quiz_results']:
            st.success(f"New careers suggested: {', '.join(st.session_state['quiz_results'])}")
        else:
            st.info("No new notifications yet.")
    
    # ----------- ABOUT US -----------
    elif menu=="About Us":
        st.title("About Career Compass")
        st.write("Interactive app to guide students in choosing career paths, explore colleges, and plan roadmaps.")
        st.image(COMPASS_GIF_PATH, width=300)
