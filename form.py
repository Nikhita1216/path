import streamlit as st
import sqlite3

# Initialize DB
def init_db():
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS forum
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  question TEXT,
                  answer TEXT)''')
    conn.commit()
    conn.close()

def add_question(user, question):
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute("INSERT INTO forum (user, question, answer) VALUES (?, ?, ?)", (user, question, ""))
    conn.commit()
    conn.close()

def add_answer(q_id, answer):
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute("UPDATE forum SET answer=? WHERE id=?", (answer, q_id))
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute("SELECT * FROM forum")
    rows = c.fetchall()
    conn.close()
    return rows

# Forum UI
def forum_ui():
    st.header("💬 Career Discussion Forum")
    
    user = st.text_input("Enter your name:")
    question = st.text_area("Ask a question:")
    if st.button("Post Question"):
        if user and question:
            add_question(user, question)
            st.success("✅ Question posted successfully!")

    st.subheader("All Discussions")
    discussions = get_all()
    for d in discussions:
        st.write(f"**Q{d[0]} by {d[1]}:** {d[2]}")
        if d[3]:
            st.info(f"Answer: {d[3]}")
        else:
            ans = st.text_area(f"Reply to Q{d[0]}:")
            if st.button(f"Post Answer to Q{d[0]}"):
                add_answer(d[0], ans)
                st.success("✅ Answer posted successfully!")
