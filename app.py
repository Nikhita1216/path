import streamlit as st
import modules.auth as auth
import modules.quiz as quiz
import modules.recommender as recommender
import modules.roadmap as roadmap
import modules.forum as forum
import json
import os
from datetime import date

# Load data
DATA_PATH = os.path.join("data","career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

st.set_page_config(page_title="Career Advisor", layout="wide")

# ---------- Helper UI ----------
def daily_affirmation():
    affirmations = [
        "You are capable of amazing things.",
        "Small steps every day lead to big changes.",
        "Believe in yourself and your potential.",
        "Curiosity is your superpower — explore.",
        "Every attempt is progress."
    ]
    # rotate by day
    idx = date.today().toordinal() % len(affirmations)
    return affirmations[idx]

# ---------- Authentication ----------
if "user" not in st.session_state:
    st.session_state.user = None

st.title("One-Stop Personalized Career & Education Advisor (Prototype)")

if not st.session_state.user:
    st.sidebar.header("Account")
    choice = st.sidebar.selectbox("Choose", ["Login","Register","About"])
    if choice=="Register":
        st.header("Create Account")
        name = st.text_input("Name")
        gender = st.selectbox("Gender", ["Prefer not to say","Male","Female","Other"])
        level = st.selectbox("Current study level", ["10th","12th","Diploma","ITI","Other"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        region = st.text_input("Region")
        city = st.text_input("City")
        state = st.text_input("State")
        age = st.number_input("Age", min_value=10, max_value=80, value=16)
        if st.button("Register"):
            ok, msg = auth.register({
                "name":name,"gender":gender,"email":email,"password":password,
                "age":age,"region":region,"city":city,"state":state,"level":level
            })
            if ok:
                st.success("Registered. Please login from sidebar.")
            else:
                st.error(msg)
    elif choice=="Login":
        st.header("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            user = auth.login(email, password)
            if user:
                st.success("Logged in.")
                st.session_state.user = {"id":user[0], "name":user[1], "email":user[3], "chosen_career":user[9]}
            else:
                st.error("Invalid credentials.")
    else:
        st.header("About")
        st.write("Prototype for SIH — Career advisor focused on J&K govt colleges.")

else:
    # ---------- Logged in Dashboard ----------
    user = st.session_state.user
    # Sidebar menu
    with st.sidebar:
        st.write(f"**Hello, {user['name']}**")
        menu = st.radio("Menu", ["Home","Profile","Discussion Forum","About"])
        if st.button("Logout"):
            st.session_state.user = None
            st.experimental_rerun()

    # Top affirmation
    st.markdown(f"### ✨ Daily Affirmation: {daily_affirmation()}")

    if menu=="Profile":
        st.header("Your Profile")
        db_user = auth.get_user_by_email(user["email"])
        if db_user:
            st.write(f"Name: {db_user[1]}")
            st.write(f"Email: {db_user[3]}")
            st.write(f"Region: {db_user[6]}, {db_user[8]}")
            st.write(f"Current Level: {db_user[9]}")
            st.write(f"Chosen Career: {db_user[10] or 'NO CHOSEN PATH YET'}")

    elif menu=="Home":
        st.header("Home")
        left, right = st.columns([2,1])

        # Left column: Search bars & results
        with left:
            st.subheader("Search")
            search_text = st.text_input("Search (free text)")
            filter_type = st.selectbox("Search by", ["Select","College","Course","Career"])
            # Process search
            if filter_type=="College":
                # show list of college names
                all_colleges = [c["name"] for c in DATA.get("colleges",[])]
                sel = st.selectbox("Select College", ["--select--"] + all_colleges)
                if sel and sel!="--select--":
                    # show courses for that college
                    cinfo = next((c for c in DATA.get("colleges",[]) if c["name"]==sel), None)
                    if cinfo:
                        st.subheader("Courses offered")
                        for cr in cinfo.get("courses",[]):
                            st.write("- " + cr)
            elif filter_type=="Course":
                # show courses from careers + college courses
                courses = set()
                for c in DATA.get("colleges",[]):
                    courses.update(c.get("courses",[]))
                for career, info in DATA.get("careers", {}).items():
                    for d in info.get("degrees", []):
                        courses.add(d)
                courses = sorted(list(courses))
                sel = st.selectbox("Select Course", ["--select--"] + courses)
                if sel and sel!="--select--":
                    st.subheader("Colleges offering this course")
                    # find colleges with this course name substring
                    found = []
                    for c in DATA.get("colleges",[]):
                        for s in c.get("courses",[]):
                            if sel.lower() in s.lower():
                                found.append(c["name"])
                    if found:
                        for f in found:
                            st.write("- " + f)
                    else:
                        st.write("No matching colleges in demo dataset.")
                    # career options for this course - search in careers for degree name match
                    st.subheader("Career outcomes from this course")
                    outcomes = []
                    for career, info in DATA.get("careers",{}).items():
                        if any(sel.lower() in d.lower() for d in info.get("degrees",[])):
                            outcomes.append(career)
                    if outcomes:
                        for o in outcomes:
                            st.write("- " + o)
                    else:
                        st.write("No direct mapping in demo dataset.")
            elif filter_type=="Career":
                careers = list(DATA.get("careers", {}).keys())
                sel = st.selectbox("Select Career", ["--select--"] + careers)
                if sel and sel!="--select--":
                    roadmap.show_roadmap(sel)

            # Free text search (simple)
            if search_text and st.button("Search"):
                st.write(f"Search results for: {search_text}")
                # naive matching: search in college names and career names
                matches = [c["name"] for c in DATA.get("colleges",[]) if search_text.lower() in c["name"].lower()]
                careers = [k for k in DATA.get("careers",{}) if search_text.lower() in k.lower()]
                if matches:
                    st.subheader("Colleges")
                    for m in matches:
                        st.write("- " + m)
                if careers:
                    st.subheader("Careers")
                    for c in careers:
                        st.write("- " + c)
                if not matches and not careers:
                    st.write("No direct results in demo data.")

            # Empty chosen path widget and Find your path CTA
            st.write("---")
            db_user = auth.get_user_by_email(user["email"])
            chosen = db_user[10] if db_user else None
            st.subheader("Your Chosen Path")
            if not chosen:
                st.info("NO CHOSEN PATH YET")
            else:
                st.success(f"Chosen: {chosen}")
                if st.button("View Roadmap"):
                    roadmap.show_roadmap(chosen)

            if st.button("Find your path (Take Quiz)"):
                st.session_state.show_quiz = True

            # Show notifications relevant to chosen career or general
            st.write("---")
            st.subheader("Notifications")
            if chosen:
                # career notifications from dataset
                for n in DATA.get("notifications", []):
                    if n.get("career")==chosen:
                        st.info(n.get("msg"))
            else:
                # general notifications
                for n in DATA.get("notifications", []):
                    st.write("- " + n.get("msg"))

        # Right column: fun / daily / quick links
        with right:
            st.subheader("Quick Tips")
            st.write("- Explore careers using the quiz")
            st.write("- Check Government college listings")
            st.write("- Join Discussions")
            st.write("---")
            st.subheader("Fun")
            st.write("🎯 Tip: Build a portfolio for creative careers (e.g., photography).")
            st.write("💡 Tip: Short diplomas can be direct to jobs.")

        # If user started quiz show quiz area & recommendation
        if st.session_state.get("show_quiz"):
            path = quiz.quiz_ui()
            if path:
                tags = recommender.tags_from_path(path)
                best, scores = recommender.score_and_recommend(tags)
                if best:
                    st.markdown("### ✅ Recommended Career (Optimal):")
                    st.markdown(f"**{best}**")
                    st.write(recommender.explain_recommendation(best, tags))
                    # Save chosen career in user db
                    auth.update_chosen_career(user["email"], best)
                    st.button("View Roadmap", on_click=roadmap.show_roadmap, args=(best,))
    elif menu=="Discussion Forum":
        forum.forum_ui()
    else:
        st.header("About")
        st.write("This is a prototype for SIH. Focus: Personalized career guidance for J&K govt college ecosystem.")
