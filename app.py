import streamlit as st
import pandas as pd
import os
import json
from graphviz import Digraph

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"
QUIZ_JSON = "career_questions.json"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        df = pd.read_csv(USERS_CSV)
    else:
        df = pd.DataFrame(columns=["username","password","name","age","gender","city","state","education","avatar","your_paths"])
        df.to_csv(USERS_CSV,index=False)
    return df

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        df = pd.read_csv(COLLEGES_CSV)
    else:
        df = pd.DataFrame(columns=["College","Location","Website","Courses"])
    return df

def load_quiz():
    with open(QUIZ_JSON,"r") as f:
        return json.load(f)

users_df = load_users()
colleges_df = load_colleges()
quiz_data = load_quiz()

# -----------------------------
# AVATAR LOGIC
# -----------------------------
def get_avatar_file(gender):
    if gender.lower()=="male":
        return os.path.join(AVATAR_FOLDER,"male.png")
    elif gender.lower()=="female":
        return os.path.join(AVATAR_FOLDER,"female.png")
    else:
        return os.path.join(AVATAR_FOLDER,"other.png")

# -----------------------------
# LOGIN & SIGNUP
# -----------------------------
def signup(username,password,name,age,gender,city,state,education):
    global users_df
    if username in users_df.username.values:
        return False
    avatar_file = get_avatar_file(gender)
    users_df.loc[len(users_df)] = [username,password,name,age,gender,city,state,education,avatar_file,""]
    users_df.to_csv(USERS_CSV,index=False)
    return True

def login(username,password):
    global users_df
    user_row = users_df[(users_df.username==username)&(users_df.password==password)]
    if not user_row.empty:
        return user_row.iloc[0]
    return None

# -----------------------------
# QUIZ SCORING
# -----------------------------
def calculate_scores(questions,answers):
    scores={}
    for q,ans in zip(questions,answers):
        if ans in q["options"]:
            for stream,weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream,0)+weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked)>1 else None
    backup = ranked[2][0] if len(ranked)>2 else None
    return major, minor, backup

# -----------------------------
# COLLEGE MATCHING
# -----------------------------
# Example synonym map to map your quiz streams to course names
course_synonyms = {
    "Software":["Computer Science","Software Engineering","CSE"],
    "AI":["Artificial Intelligence","AI & ML"],
    "Mechanical":["Mechanical Engineering"],
    "CivilArch":["Civil Engineering","Architecture"],
    "Physics":["Physics"],
    "Chemistry":["Chemistry"],
    "Biology":["Biology","Life Sciences"],
    "Medical":["MBBS","BDS","Nursing","Pharmacy"],
    "Commerce":["BBA","BCom","Economics"],
    "Arts":["Fine Arts","Design","Performing Arts"]
}

def get_colleges_for_course(course_name):
    mapped_names = course_synonyms.get(course_name,[course_name])
    matching_colleges=[]
    for cname in mapped_names:
        for _, row in colleges_df.iterrows():
            if cname.lower() in row.Courses.lower():
                matching_colleges.append(f"{row.College} ({row.Location})")
    return matching_colleges

# -----------------------------
# GRAPHVIZ ROADMAP
# -----------------------------
def generate_roadmap(major,minor,backup,sub_major,sub_minor,sub_backup):
    dot = Digraph(comment="Career Path")
    dot.attr(rankdir="LR", size='10')
    
    dot.node("Start","Start")
    
    # Main stream nodes
    dot.node(major,f"Major Stream:\n{major}")
    dot.node(minor,f"Minor Stream:\n{minor}")
    dot.node(backup,f"Backup Stream:\n{backup}")
    
    dot.edge("Start",major)
    dot.edge("Start",minor)
    dot.edge("Start",backup)
    
    # Specialization nodes
    dot.node(sub_major,f"Specialization:\n{sub_major}\nColleges:\n" + "\n".join(get_colleges_for_course(sub_major)))
    dot.node(sub_minor,f"Specialization:\n{sub_minor}\nColleges:\n" + "\n".join(get_colleges_for_course(sub_minor)))
    dot.node(sub_backup,f"Specialization:\n{sub_backup}\nColleges:\n" + "\n".join(get_colleges_for_course(sub_backup)))
    
    dot.edge(major,sub_major)
    dot.edge(minor,sub_minor)
    dot.edge(backup,sub_backup)
    
    return dot

# -----------------------------
# APP MAIN
# -----------------------------
st.sidebar.title("Career Compass")
menu = st.sidebar.radio("Menu",["Home","Quiz","Your Paths","Explore","Notifications","About Us","Log Out"],key="sidebar_menu")

# Session state for login
if "login" not in st.session_state:
    st.session_state.login=False
if "user" not in st.session_state:
    st.session_state.user=None

# -----------------------------
# HOME
# -----------------------------
if menu=="Home":
    st.title("Welcome to Career Compass")
    if not st.session_state.login:
        st.subheader("Login")
        username = st.text_input("Username",key="login_user")
        password = st.text_input("Password",type="password",key="login_pass")
        if st.button("Login",key="login_btn"):
            user = login(username,password)
            if user is not None:
                st.session_state.login=True
                st.session_state.user=user
                st.success(f"Welcome {user['name']}")
            else:
                st.error("Invalid credentials")
        
        st.subheader("Sign Up")
        new_username = st.text_input("Username",key="signup_user")
        new_password = st.text_input("Password",type="password",key="signup_pass")
        name = st.text_input("Full Name",key="signup_name")
        age = st.number_input("Age",min_value=10,max_value=100,step=1,key="signup_age")
        gender = st.selectbox("Gender",["Male","Female","Other"],key="signup_gender")
        city = st.text_input("City",key="signup_city")
        state = st.text_input("State",key="signup_state")
        education = st.text_input("Education Qualification",key="signup_edu")
        if st.button("Sign Up",key="signup_btn"):
            success = signup(new_username,new_password,name,age,gender,city,state,education)
            if success:
                st.success("Sign up successful! Please login.")
            else:
                st.error("Username already exists.")
    else:
        st.image(st.session_state.user['avatar'],width=120)
        st.write(f"Logged in as: {st.session_state.user['name']}")
        st.write(f"Location: {st.session_state.user['city']}, {st.session_state.user['state']}")
        st.write(f"Education: {st.session_state.user['education']}")

# -----------------------------
# QUIZ
# -----------------------------
elif menu=="Quiz":
    if not st.session_state.login:
        st.warning("Login to take the quiz")
    else:
        st.title("Career Quiz")
        main_answers=[]
        for i,q in enumerate(quiz_data["main"]):
            st.subheader(f"Q{i+1}: {q['q']}")
            opts=[f"{k}: {v['text']}" for k,v in q["options"].items()]
            ans = st.radio("Select option",opts,key=f"main_q{i}")
            selected_letter = ans.split(":")[0]
            main_answers.append(selected_letter)
        if st.button("Submit Quiz",key="submit_quiz"):
            main_scores = calculate_scores(quiz_data["main"],main_answers)
            major_stream, minor_stream, backup_stream = recommend(main_scores)
            st.session_state.user['your_paths'] = f"{major_stream},{minor_stream},{backup_stream}"
            st.success(f"Recommended Streams: {major_stream} (Major), {minor_stream} (Minor), {backup_stream} (Backup)")
            
            # Sub quiz
            if major_stream in quiz_data["sub"]:
                st.subheader(f"Specialization Quiz for {major_stream}")
                sub_answers=[]
                for i,q in enumerate(quiz_data["sub"][major_stream]):
                    st.write(f"Q{i+1}: {q['q']}")
                    opts=[f"{k}: {v['text']}" for k,v in q["options"].items()]
                    ans = st.radio("Select option",opts,key=f"sub_q{i}")
                    selected_letter = ans.split(":")[0]
                    sub_answers.append(selected_letter)
                if st.button("Submit Sub Quiz",key="submit_sub_quiz"):
                    sub_scores = calculate_scores(quiz_data["sub"][major_stream],sub_answers)
                    sub_major,sub_minor,sub_backup = recommend(sub_scores)
                    st.session_state.user['sub_paths'] = f"{sub_major},{sub_minor},{sub_backup}"
                    st.success(f"Specializations: {sub_major} (Major), {sub_minor} (Minor), {sub_backup} (Backup)")
                    # Roadmap
                    dot = generate_roadmap(major_stream,minor_stream,backup_stream,sub_major,sub_minor,sub_backup)
                    st.graphviz_chart(dot)

# -----------------------------
# YOUR PATHS
# -----------------------------
elif menu=="Your Paths":
    if not st.session_state.login:
        st.warning("Login to see your paths")
    else:
        st.title("Your Career Paths")
        if 'your_paths' in st.session_state.user:
            st.write(f"Streams: {st.session_state.user['your_paths']}")
        if 'sub_paths' in st.session_state.user:
            st.write(f"Specializations: {st.session_state.user['sub_paths']}")

# -----------------------------
# EXPLORE COLLEGES
# -----------------------------
elif menu=="Explore":
    st.title("Explore Colleges")
    stream_choice = st.selectbox("Select Stream",list(course_synonyms.keys()))
    st.write("Colleges offering courses related to",stream_choice)
    colleges = get_colleges_for_course(stream_choice)
    for c in colleges:
        st.write("-",c)

# -----------------------------
# NOTIFICATIONS
# -----------------------------
elif menu=="Notifications":
    st.title("Notifications")
    st.info("No new notifications")

# -----------------------------
# ABOUT US
# -----------------------------
elif menu=="About Us":
    st.title("About Us")
    st.write("Career Compass is a Streamlit app to guide students in choosing career paths based on their interests.")

# -----------------------------
# LOG OUT
# -----------------------------
elif menu=="Log Out":
    st.session_state.login=False
    st.session_state.user=None
    st.success("Logged out successfully")
