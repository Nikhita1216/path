import streamlit as st
import json
import os

DATA_PATH = os.path.join("data","career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DB = json.load(f)

CAREER_DB = DB.get("careers", {})
COLLEGE_DB = DB.get("colleges", [])
NOTIFS = DB.get("notifications", [])

def show_roadmap(career, user_profile=None):
    info = CAREER_DB.get(career)
    if not info:
        st.warning("No roadmap available for this career.")
        return
    st.header(f"🚀 Roadmap: {career}")
    st.write(info.get("notes",""))
    st.subheader("Which Course / Degree?")
    for d in info.get("degrees", []):
        st.write("- " + d)
    st.subheader("Sample Govt Colleges (J&K)")
    for c in info.get("sample_colleges", []):
        st.write("- " + c)
    st.subheader("Future Scope / Jobs")
    for s in info.get("future_scope", []):
        st.write("- " + s)
    st.subheader("Study Materials")
    st.write("- SWAYAM / NPTEL / local college resources / e-books (add links later)")
    st.subheader("Notifications for this career")
    for n in NOTIFS:
        if n.get("career")==career:
            st.info(n.get("msg"))
