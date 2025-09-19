import streamlit as st
import json
import os
from datetime import date
import modules.auth as auth
import modules.roadmap as roadmap

# 🔹 Tailwind injection
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Load career DB
DATA_PATH = os.path.join("data","career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

# Daily affirmation
def daily_affirmation():
    affirmations = [
        "🌟 You are capable of amazing things.",
        "🚀 Small steps every day lead to big changes.",
        "💡 Believe in yourself and your potential.",
        "🌱 Curiosity is your superpower — explore.",
        "🔥 Every attempt is progress."
    ]
    idx = date.today().toordinal() % len(affirmations)
    return affirmations[idx]

# ---------------- Authentication ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("""
    <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-2xl shadow-lg text-center">
      <h1 class="text-4xl font-bold mb-4">Career Compass</h1>
      <p class="text-lg">Your personalized career & education advisor 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("✨ Login / Sign Up")

    # 🔹 Anime-style Visme form
    st.markdown("""
    <div class="visme_d"
         data-title="Webinar Registration Form"
         data-url="g7ddqxx0-untitled-project?fullPage=true"
         data-domain="forms"
         data-full-page="true"
         data-min-height="70vh"
         data-form-id="133190">
    </div>
    <script src="https://static-b-assets.visme.co/forms/vismeforms-embed.js"></script>
    """, unsafe_allow_html=True)

    st.info("➡️ For hackathon demo, skip Visme login & press 'Demo Login' below.")
    if st.button("Demo Login"):
        st.session_state.user = {"name":"HackathonUser","email":"demo@sih.com"}
        st.success("Logged in as Demo User ✅")
        st.experimental_rerun()

else:
    # ---------------- Dashboard ----------------
    user = st.session_state.user

    st.markdown(f"""
    <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
      <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
      <p>{daily_affirmation()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Menu
    menu = st.sidebar.radio("📍 Navigate", ["Home","Quiz","Roadmap","About","Logout"])

    if menu=="Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu=="Home":
        st.header("🏠 Home")

        # Search Section
        st.markdown("""
        <div class="bg-white p-4 rounded-xl shadow-md mb-4">
          <h3 class="text-xl font-bold">🔎 Search</h3>
        </div>
        """, unsafe_allow_html=True)

        search_text = st.text_input("Free Search (College / Course / Career)")
        filter_type = st.selectbox("Filter by", ["Select","College","Course","Career"])

        if st.button("Search"):
            if filter_type=="College":
                names = [c["name"] for c in DATA["colleges"]]
                st.write("Colleges:", names)
            elif filter_type=="Course":
                st.write("Courses across colleges:")
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            st.write(f"- {cr} ({c['name']})")
            elif filter_type=="Career":
                if search_text in DATA["careers"]:
                    roadmap.show_roadmap(search_text)
                else:
                    st.error("Career not found in demo dataset")

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu=="Quiz":
        st.header("🎯 Career Quiz")

        quiz_tree = {
            "Q1": {"q":"What are your main interests?",
                   "options":["Photography","Culinary","Engineering","Medicine"]},
            "Q2-Photography": {"q":"Do you prefer studio editing or outdoor shooting?",
                               "options":["Editing","Outdoor"]},
            "Q2-Culinary": {"q":"Do you enjoy baking, cooking, or management?",
                            "options":["Baking","Cooking","Management"]}
        }

        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = "Q1"
            st.session_state.answers = []
            st.session_state.quiz_result = None

        node = quiz_tree[st.session_state.quiz_step]
        choice = st.radio(node["q"], node["options"], key=st.session_state.quiz_step)

        if st.button("Next Question"):
            st.session_state.answers.append(choice)
            next_key = f"Q2-{choice}"
            if next_key in quiz_tree:
                st.session_state.quiz_step = next_key
            else:
                st.session_state.quiz_result = choice
                st.success(f"✅ Based on your answers, we suggest: **{choice}**")

        if st.session_state.quiz_result:
            if st.button("View Roadmap"):
                roadmap.show_roadmap(st.session_state.quiz_result)

    # ---------------- Roadmap ----------------
    if menu=="Roadmap":
        st.header("🛤 Career Roadmap")
        career = st.text_input("Enter a career to view roadmap", "Culinary")
        if st.button("Show Roadmap"):
            roadmap.show_roadmap(career)

    # ---------------- About ----------------
    if menu=="About":
        st.header("ℹ️ About")
        st.write("Prototype for SIH Hackathon — Personalized Career & Education Advisor.")
