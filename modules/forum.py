import sqlite3
import streamlit as st

DB = "forum.db"

def init_forum():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS forum
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, question TEXT, answer TEXT)''')
    conn.commit()
    conn.close()

def add_question(user, question):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO forum (user, question, answer) VALUES (?, ?, ?)", (user, question, ""))
    conn.commit()
    conn.close()

def add_answer(qid, answer):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE forum SET answer=? WHERE id=?", (answer, qid))
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, user, question, answer FROM forum ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# initialize
init_forum()

def forum_ui():
    st.header("💬 Discussion Forum")
    user = st.text_input("Your name", key="forum_user")
    txt = st.text_area("Ask a question")
    if st.button("Post Question"):
        if user and txt.strip():
            add_question(user, txt.strip())
            st.success("Question posted!")
    st.subheader("All discussions")
    rows = get_all()
    for r in rows:
        qid, user, question, answer = r
        st.write(f"**Q{qid} — {question}** (by {user})")
        if answer:
            st.info("Answer: " + answer)
        else:
            ans = st.text_area(f"Reply to Q{qid}", key=f"ans_{qid}")
            if st.button(f"Post Answer {qid}", key=f"btn_ans_{qid}"):
                if ans.strip():
                    add_answer(qid, ans.strip())
                    st.success("Answer posted!")
