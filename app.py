import streamlit as st
import pandas as pd
import os
import json
import graphviz

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Career Compass", layout="wide")
USERS_CSV = "users.csv"
COLLEGES_CSV = "jk_colleges.csv"
QUIZ_JSON = "career_questions.json"

# -----------------------------
# LOAD DATA
# -----------------------------
def load_users():
    if os.path.exists(USERS_CSV):
        return pd.read_csv(USERS_CSV)
    else:
        return pd.DataFrame(columns=["Name", "Avatar","Stream", "Specialization", "Skills"])

def load_colleges():
    if os.path.exists(COLLEGES_CSV):
        df = pd.read_csv(COLLEGES_CSV)
        df.fillna("", inplace=True)
        return df
    else:
        return pd.DataFrame(columns=["College","Location","Website","Courses","Skills"])

def load_quiz():
    with open(QUIZ_JSON, "r") as f:
        return json.load(f)

# -----------------------------
# CANONICAL COURSE MAPPING
# -----------------------------
course_synonyms = {
    "Computer Science": ["CS", "CSE", "Software", "Software Engineering", "Comp Sci"],
    "Electronics": ["ECE", "Electronics and Communication", "Electronics Engineering"],
    "Mechanical": ["Mech", "Mechanical Engineering"],
    "Civil": ["Civil Engineering", "Construction"],
    "Electrical": ["Electrical Engineering", "EEE"],
    "IT": ["Information Technology", "IT Engineering"],
    "Biology": ["Bio", "Life Sciences"],
    "Medicine": ["Medical", "MBBS", "Doctor"],
    "Arts": ["Fine Arts", "Design", "Painting", "Performing Arts"],
    "Commerce": ["Business", "Economics", "Finance", "Accounting"],
}

synonym_to_canonical = {}
for canonical, synonyms in course_synonyms.items():
    for syn in synonyms:
        synonym_to_canonical[syn.lower()] = canonical

# -----------------------------
# QUIZ LOGIC
# -----------------------------
def calculate_scores(questions, answers):
    scores = {}
    for q, ans in zip(questions, answers):
        if ans in q["options"]:
            for stream, weight in q["options"][ans]["weights"].items():
                scores[stream] = scores.get(stream, 0) + weight
    return scores

def recommend(scores):
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    major = ranked[0][0] if ranked else None
    minor = ranked[1][0] if len(ranked) > 1 else None
    backup = ranked[2][0] if len(ranked) > 2 else None
    return major, minor, backup

# -----------------------------
# COLLEGE MATCHING
# -----------------------------
def match_colleges(colleges_df, stream, skills):
    stream_key = synonym_to_canonical.get(stream.lower(), stream)

    def score_college(row):
        college_courses = [c.strip() for c in row["Courses"].split(",")]
        college_courses_canonical = [synonym_to_canonical.get(c.lower(), c) for c in college_courses]
        course_score = 2 if stream_key in college_courses_canonical else 0
        college_skills = [s.strip().lower() for s in str(row.get("Skills","")).split(",")]
        skill_overlap = len(set(skills) & set(college_skills))
        return course_score + skill_overlap

    colleges_df["MatchScore"] = colleges_df.apply(score_college, axis=1)
    return colleges_df[colleges_df["MatchScore"] > 0].sort_values(by="MatchScore", ascending=False)

# -----------------------------
# APP UI
# -----------------------------
users_df = load_users()
colleges_df = load_colleges()
quiz_data = load_quiz()

# -----------------------------
# SIDEBAR LOGIN & PROFILE
# -----------------------------
st.sidebar.title("👤 User Profile")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.session_state.user_name = st.sidebar.text_input("Enter your name")
    st.session_state.avatar = st.sidebar.selectbox("Choose Avatar", ["😀","🧑‍🎓","👩‍💻","🎨","💼"])
    if st.sidebar.button("Login"):
        if st.session_state.user_name:
            st.session_state.logged_in = True
else:
    st.sidebar.success(f"Hello {st.session_state.user_name} {st.session_state.avatar}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    st.sidebar.info("Use tabs to navigate: Quiz → Colleges → Roadmap")

# -----------------------------
# MAIN TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📝 Career Quiz", "🏫 College Recommendations", "🛤️ Visual Roadmap"])

# -----------------------------
# Step 1: Career Quiz
# -----------------------------
with tab1:
    if not st.session_state.logged_in:
        st.warning("Please login from sidebar to continue.")
    else:
        st.header("Step 1: Take the Career Quiz")
        answers_main = []
        total_questions = len(quiz_data["main"])
        for i, q in enumerate(quiz_data["main"]):
            ans = st.radio(f"{i+1}. {q['q']}", list(q["options"].keys()), key=f"main_{i}")
            answers_main.append(ans)
            st.progress((i+1)/total_questions)

        if st.button("Get Stream Recommendation", key="quiz_next"):
            main_scores = calculate_scores(quiz_data["main"], answers_main)
            major_stream, minor_stream, backup_stream = recommend(main_scores)
            st.success(f"✅ Your Recommended Streams:\n- Major: {major_stream}\n- Minor: {minor_stream}\n- Backup: {backup_stream}")

            if major_stream in quiz_data["sub"]:
                st.header(f"Step 2: {major_stream} Specialization")
                answers_sub = []
                total_sub_questions = len(quiz_data["sub"][major_stream])
                for i, q in enumerate(quiz_data["sub"][major_stream]):
                    ans = st.radio(f"{i+1}. {q['q']}", list(q["options"].keys()), key=f"sub_{i}")
                    answers_sub.append(ans)
                    st.progress((i+1)/total_sub_questions)

                if st.button("Get Specialization Recommendation", key="sub_next"):
                    sub_scores = calculate_scores(quiz_data["sub"][major_stream], answers_sub)
                    sub_major, sub_minor, sub_backup = recommend(sub_scores)
                    st.success(f"Specialization in {major_stream}:\n- Major: {sub_major}\n- Minor: {sub_minor}\n- Backup: {sub_backup}")

                    users_df = pd.concat([users_df, pd.DataFrame([{
                        "Name": st.session_state.user_name,
                        "Avatar": st.session_state.avatar,
                        "Stream": major_stream,
                        "Specialization": sub_major,
                        "Skills": ""
                    }])], ignore_index=True)
                    users_df.to_csv(USERS_CSV, index=False)

# -----------------------------
# Step 2: College Recommendations
# -----------------------------
with tab2:
    if not st.session_state.logged_in:
        st.warning("Please login from sidebar to continue.")
    else:
        st.header("Step 3: Find Colleges for Your Stream")
        user_stream = st.text_input("Enter your chosen stream:", key="college_stream_input")
        skills_input = st.text_input("Enter your skills (comma separated):", key="college_skills_input")
        if st.button("Find Colleges", key="find_colleges"):
            if not user_stream:
                st.warning("Enter a stream to find colleges.")
            else:
                skills = [s.strip().lower() for s in skills_input.split(",")]
                matched_colleges = match_colleges(colleges_df, user_stream, skills)
                st.subheader(f"Colleges matching '{user_stream}':")
                if matched_colleges.empty:
                    st.info("No colleges found matching your criteria.")
                else:
                    for idx, row in matched_colleges.iterrows():
                        st.markdown(f"**{row['College']}** {st.session_state.avatar}")
                        st.markdown(f"- Location: {row['Location']}")
                        st.markdown(f"- Website: [{row['Website']}]({row['Website']})")
                        st.markdown(f"- Courses Offered: {row['Courses']}")
                        st.markdown(f"- Relevant Skills: {row.get('Skills','N/A')}")
                        st.markdown(f"- Match Score: {row['MatchScore']}")
                        st.markdown("---")

# -----------------------------
# Step 3: Visual Roadmap
# -----------------------------
with tab3:
    if not st.session_state.logged_in:
        st.warning("Please login from sidebar to continue.")
    else:
        st.header("Visual Career Roadmap")
        user_stream_viz = st.text_input("Enter your major stream for roadmap:", key="roadmap_stream_input")
        if user_stream_viz:
            dot = graphviz.Digraph(comment='Career Roadmap', format='png')
            dot.node("Start", "Your Career Path")
            dot.node(user_stream_viz, f"Stream: {user_stream_viz}")
            dot.edge("Start", user_stream_viz)

            if user_stream_viz in quiz_data["sub"]:
                specializations = list(quiz_data["sub"][user_stream_viz][0]["options"].keys())
            else:
                specializations = []

            for sub_spec in specializations:
                dot.node(sub_spec, f"Specialization: {sub_spec}")
                dot.edge(user_stream_viz, sub_spec)

                matched = match_colleges(colleges_df, sub_spec, [])
                for idx, row in matched.iterrows():
                    college_node = f"{sub_spec}_{row['College']}"
                    dot.node(college_node, f"<{row['College']}>\n<a href='{row['Website']}'>{row['Website']}</a>", shape="box", href=row['Website'])
                    dot.edge(sub_spec, college_node)

            st.graphviz_chart(dot)
