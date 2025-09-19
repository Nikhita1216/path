import streamlit as st

# Simple adaptive quiz tree stored here
quiz_tree = {
    "start": {
        "q": "What are your main interests?",
        "options": ["Photography", "Culinary", "Horticulture", "Engineering", "Medicine", "Design/Art", "Business/Finance"]
    },
    "Photography": {
        "q": "Photography — do you prefer studio editing or outdoor shooting?",
        "options": ["Editing/Studio", "Outdoor/Field", "Both"]
    },
    "Culinary": {
        "q": "Culinary — are you into cooking, baking, or kitchen management?",
        "options": ["Cooking", "Baking", "Management"]
    },
    "Horticulture": {
        "q": "Horticulture — would you like labs, farm work or agribusiness?",
        "options": ["Labs", "Farm Work", "Agri-business"]
    },
    "Engineering": {
        "q": "Engineering — which stream appeals to you?",
        "options": ["Computers", "Mechanical", "Civil", "Electrical"]
    },
    "Medicine": {
        "q": "Medicine — clinical practice or allied health?",
        "options": ["Clinical (MBBS)", "Allied Health / Paramedical"]
    }
}

def init_state():
    if "quiz_step" not in st.session_state:
        st.session_state.quiz_step = "start"
    if "quiz_path" not in st.session_state:
        st.session_state.quiz_path = []

def reset_quiz():
    st.session_state.quiz_step = "start"
    st.session_state.quiz_path = []
    if "quiz_result" in st.session_state:
        del st.session_state["quiz_result"]

def quiz_ui():
    init_state()
    st.header("🔎 Personalized Career Quiz")
    current = st.session_state.quiz_step
    node = quiz_tree[current]
    st.write(f"**Q:** {node['q']}")
    choice = st.radio("Select one:", node['options'], key="quiz_radio")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next"):
            st.session_state.quiz_path.append(choice)
            if choice in quiz_tree:
                st.session_state.quiz_step = choice
            else:
                st.session_state.quiz_result = choice
                st.success(f"Final choice captured: {choice}")
    with col2:
        if st.button("Reset Quiz"):
            reset_quiz()

    if "quiz_result" in st.session_state:
        st.write("### Quiz path:")
        st.write(st.session_state.quiz_path)
        return st.session_state.quiz_path
    return None
