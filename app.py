import streamlit as st

# Minimal career dataset
career_db = {
    "Culinary": {
        "tags": ["creative", "hands-on", "hospitality"],
        "degrees": ["Diploma in Culinary Arts", "B.Sc Hospitality"],
        "colleges": ["Govt Polytechnic Jammu (Travel & Tourism)", "Vocational Centres"],
        "scope": ["Chef", "Restaurant Manager", "Catering Entrepreneur"]
    },
    "Photography": {
        "tags": ["creative", "visual", "field-work"],
        "degrees": ["Diploma in Photography", "B.Des (Photography)", "Short Courses"],
        "colleges": ["GDC Jammu (short courses)", "Polytechnic CDTP"],
        "scope": ["Freelance Photographer", "Photojournalist"]
    },
    "Horticulture": {
        "tags": ["biology", "outdoors", "environment"],
        "degrees": ["B.Sc Horticulture"],
        "colleges": ["GDC Shopian"],
        "scope": ["Nurseries", "Agri-business", "Plant Breeder"]
    }
}

# Simple quiz options
quiz_options = {
    "start": {
        "q": "What are your main interests?",
        "options": ["Cooking/Food", "Photography/Visuals", "Biology/Nature"]
    }
}

# Map quiz answers to tags
answer_map = {
    "Cooking/Food": ["creative", "hands-on", "hospitality"],
    "Photography/Visuals": ["creative", "visual", "field-work"],
    "Biology/Nature": ["biology", "outdoors", "environment"]
}

st.title("🎓 Career Guidance Test Model")

# Run quiz
st.header("Quiz")
q = quiz_options["start"]
choice = st.radio(q["q"], q["options"])

if st.button("Get Recommendation"):
    user_tags = answer_map.get(choice, [])
    # Scoring
    best = None
    best_score = -1
    for career, info in career_db.items():
        score = len(set(user_tags) & set(info["tags"]))
        if score > best_score:
            best, best_score = career, score

    if best:
        st.subheader(f"✅ Recommended Career: {best}")
        st.write("**Why:** Matching tags:", ", ".join(set(user_tags) & set(career_db[best]["tags"])))

        st.subheader("Which Courses/Degrees?")
        for d in career_db[best]["degrees"]:
            st.write("-", d)

        st.subheader("Sample Govt Colleges")
        for c in career_db[best]["colleges"]:
            st.write("-", c)

        st.subheader("Future Scope")
        for s in career_db[best]["scope"]:
            st.write("-", s)
    else:
        st.warning("No matching career found.")
