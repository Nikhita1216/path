import forum

menu = ["Home", "Career Guidance", "Discussion Forum"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.title("Career Advisor")
    st.write("Welcome!")
elif choice == "Career Guidance":
    # Call your career_tree / quiz logic
    pass
elif choice == "Discussion Forum":
    forum.forum_ui()
