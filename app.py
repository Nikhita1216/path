import streamlit as st
import pandas as pd
import json
import os
from graphviz import Digraph

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")

USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
AVATAR_FOLDER = "images"

# -----------------------------
# DATA LOADERS
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    else:
        cols = ['name','email','password','age','gender','location','studying','avatar','your_paths']
        return pd.DataFrame(columns=cols)

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        return pd.read_csv(COLLEGES_CSV)
    else:
        cols = ['college','location','website','courses']
        return pd.DataFrame(columns=cols)

def load_quiz():
    with open("career_questions.json", "r") as f:
        return json.load(f)

# -----------------------------
# USER MANAGEMENT
# -----------------------------
def signup(name,email,password,age,gender,location,studying):
    users_df = load_users()
    if email in users_df.email.values:
        return False, "Email already registered."
    avatar_file = "male.png" if gender.lower()=="male" else "female.png"
    users_df.loc[len(users_df)] = [name,email,password,age,gender,location,studying,avatar_file,""]
    users_df.to_csv(USERS_CSV,index=False)
    return True, "Signup successful."

def login(email,password):
    users_df = load_users()
    user = users_df[(users_df.email==email) & (users_df.password==password)]
    if not user.empty:
        return True, user.iloc[0]
    else:
        return False, None

def update_user_paths(email,your_paths):
    users_df = load_users()
    users_df.loc[users_df.email==email,'your_paths'] = your_paths
    users_df.to_csv(USERS_CSV,index=False)

# -----------------------------
# QUIZ LOGIC
# -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q, ans in zip(questions, answers):
        if ans in q["options"]:
            for stream, weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream,0)+weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    major = ranked[0][0] if len(ranked)>0 else None
    minor = ranked[1][0] if len(ranked)>1 else None
    backup = ranked[2][0] if len(ranked)>2 else None
    return major, minor, backup

# -----------------------------
# COLLEGE MAPPING
# -----------------------------
# Optional synonyms map to match streams to courses
COURSE_SYNONYMS = {
    "Software":["Computer Science","Software Engineering","CSE"],
    "AI":["Artificial Intelligence","AI & ML","Machine Learning"],
    "Mechanical":["Mechanical Engineering","ME"],
    "CivilArch":["Civil Engineering","Architecture","CE"],
    "Electronics":["Electronics","ECE","Electrical"],
    "Medical":["MBBS","BDS","Nursing","Paramedical"],
    "Science":["Physics","Chemistry","Biology","Biotechnology"]
}

def find_colleges_for_stream(stream,colleges_df):
    courses_to_search = COURSE_SYNONYMS.get(stream,[stream])
    filtered = colleges_df[colleges_df['courses'].apply(lambda x: any(c.lower() in x.lower() for c in courses_to_search))]
    return filtered

# -----------------------------
# GRAPHVIZ ROADMAP
# -----------------------------
def draw_roadmap(stream_major,stream_minor,stream_backup,sub_major,sub_minor,sub_backup,colleges_df):
    dot = Digraph(comment='Career Pathway')
    # Streams
    dot.node('Major', stream_major)
    if stream_minor: dot.node('Minor', stream_minor)
    if stream_backup: dot.node('Backup', stream_backup)
    # Specializations
    if sub_major: dot.node('SpecMajor', sub_major)
    if sub_minor: dot.node('SpecMinor', sub_minor)
    if sub_backup: dot.node('SpecBackup', sub_backup)
    # Colleges
    col_major = find_colleges_for_stream(sub_major,colleges_df) if sub_major else pd.DataFrame()
    for idx,row in col_major.iterrows():
        dot.node(f"College_{idx}", row['college'])
        dot.edge('SpecMajor', f"College_{idx}")
    # Connect streams to specializations
    dot.edge('Major','SpecMajor')
    if sub_minor: dot.edge('Minor','SpecMinor')
    if sub_backup: dot.edge('Backup','SpecBackup')
    return dot

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("Career Compass")

# Session state
if "login" not in st.session_state:
    st.session_state.login=False
if "user" not in st.session_state:
    st.session_state.user=None

# -----------------------------
# LOGIN / SIGNUP
# -----------------------------
if not st.session_state.login:
    tab = st.tabs(["Login","Sign Up"])
    with tab[0]:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password",type="password")
        if st.button("Login"):
            success,user = login(email,password)
            if success:
                st.session_state.login=True
                st.session_state.user=user
                st.success(f"Welcome {user['name']}!")
            else:
                st.error("Invalid credentials")
    with tab[1]:
        st.subheader("Sign Up")
        name = st.text_input("Full Name","")
        email = st.text_input("Email","")
        password = st.text_input("Password","",type="password")
        age = st.number_input("Age",min_value=10,max_value=100,value=18)
        gender = st.selectbox("Gender",["Male","Female"])
        location = st.text_input("City/State","")
        studying = st.text_input("Current Education","")
        if st.button("Sign Up"):
            success,msg = signup(name,email,password,age,gender,location,studying)
            if success:
                st.success(msg)
            else:
                st.error(msg)
else:
    # Sidebar
    st.sidebar.title(f"Hello, {st.session_state.user['name']}")
    st.sidebar.image(os.path.join(AVATAR_FOLDER,st.session_state.user['avatar']),width=80)
    menu = st.sidebar.radio("Menu",["Home","Quiz","Your Paths","Explore Colleges","Notifications","About Us","Log Out"])
    
    colleges_df = load_colleges()
    quiz_data = load_quiz()

    if menu=="Home":
        st.subheader("Welcome to Career Compass!")
        st.write("Navigate using the sidebar to explore career paths, take the quiz, and discover colleges.")
    
    elif menu=="Quiz":
        st.subheader("Career Quiz")
        # MAIN QUIZ
        main_answers = []
        for i,q in enumerate(quiz_data['main']):
            st.write(f"**Q{i+1}: {q['q']}**")
            choice = st.radio("Choose:", [f"{opt}: {q['options'][opt]['text']}" for opt in q['options']], key=f"main_{i}")
            selected = choice.split(":")[0]
            main_answers.append(selected)
        if st.button("Submit Main Quiz"):
            main_scores = calculate_scores(quiz_data['main'],main_answers)
            stream_major,stream_minor,stream_backup = recommend(main_scores)
            st.session_state.streams = (stream_major,stream_minor,stream_backup)
            st.success(f"Major Stream: {stream_major}, Minor: {stream_minor}, Backup: {stream_backup}")
            st.session_state.take_subquiz=True

        # SUB QUIZ
        if st.session_state.get("take_subquiz",False) and st.session_state.streams:
            stream_major,_ , _ = st.session_state.streams
            if stream_major in quiz_data['sub']:
                st.subheader(f"Specialization Quiz for {stream_major}")
                sub_answers=[]
                for i,q in enumerate(quiz_data['sub'][stream_major]):
                    st.write(f"**Q{i+1}: {q['q']}**")
                    choice = st.radio("Choose:", [f"{opt}: {q['options'][opt]['text']}" for opt in q['options']], key=f"sub_{i}")
                    selected = choice.split(":")[0]
                    sub_answers.append(selected)
                if st.button("Submit Sub Quiz"):
                    sub_scores = calculate_scores(quiz_data['sub'][stream_major],sub_answers)
                    sub_major,sub_minor,sub_backup = recommend(sub_scores)
                    st.session_state.specializations = (sub_major,sub_minor,sub_backup)
                    # Save paths to user
                    paths_json = json.dumps({
                        "streams": st.session_state.streams,
                        "specializations": st.session_state.specializations
                    })
                    update_user_paths(st.session_state.user['email'],paths_json)
                    st.success("Your career paths have been saved!")

    elif menu=="Your Paths":
        st.subheader("Your Career Paths")
        your_paths = st.session_state.user.get("your_paths","")
        if your_paths:
            paths = json.loads(your_paths)
            st.write("**Streams:**", paths.get("streams"))
            st.write("**Specializations:**", paths.get("specializations"))
            # Show roadmap
            dot = draw_roadmap(*paths.get("streams"),*paths.get("specializations"),colleges_df)
            st.graphviz_chart(dot)
        else:
            st.info("Take the quiz first to see your career paths.")

    elif menu=="Explore Colleges":
        st.subheader("Jammu & Kashmir Government Colleges")
        if not colleges_df.empty:
            st.dataframe(colleges_df)
        else:
            st.info("No colleges data found.")

    elif menu=="Notifications":
        st.subheader("Notifications")
        st.info("No new notifications.")

    elif menu=="About Us":
        st.subheader("About Us")
        st.write("Career Compass helps students discover their ideal streams and colleges in J&K.")

    elif menu=="Log Out":
        st.session_state.login=False
        st.session_state.user=None
        st.experimental_rerun()
