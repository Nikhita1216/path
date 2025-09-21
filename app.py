# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# -------------------------
# Configuration & paths
# -------------------------
st.set_page_config(page_title="Career Compass", layout="wide", initial_sidebar_state="expanded")

BASE = Path(".")
AVATAR_DIR = BASE / "images"           # put avatar PNG/JPG files here
COLLEGES_CSV = BASE / "jk_colleges.csv" # must have columns: College,Location,Course,Future_Scope,Study_Materials,Exam_Info
ROADMAPS_CSV = BASE / "career_roadmaps.csv" # optional: columns Career,Step,Detail (or we fallback to built-in)
USERS_CSV = BASE / "users.csv"          # will be created when users sign up
COMPASS_GIF = BASE / "compass.gif"      # optional

# -------------------------
# Utility helpers
# -------------------------
def load_csv_safe(path, fallback_df=None):
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.warning(f"Couldn't read CSV {path.name}: {e}")
            return fallback_df if fallback_df is not None else pd.DataFrame()
    else:
        return fallback_df if fallback_df is not None else pd.DataFrame()

def ensure_users_csv():
    if not USERS_CSV.exists():
        df = pd.DataFrame(columns=["email","password","name","age","gender","location","studying","avatar","your_paths"])
        df.to_csv(USERS_CSV,index=False)

def save_user_record(user_dict):
    ensure_users_csv()
    df = pd.read_csv(USERS_CSV)
    # remove existing with same email
    df = df[df['email'] != user_dict['email']]
    df = pd.concat([df, pd.DataFrame([user_dict])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)

def get_user_by_email(email):
    if USERS_CSV.exists():
        df = pd.read_csv(USERS_CSV)
        row = df[df['email']==email]
        if not row.empty:
            return row.iloc[0].to_dict()
    return None

def list_avatars():
    if AVATAR_DIR.exists():
        imgs = [p for p in AVATAR_DIR.iterdir() if p.suffix.lower() in (".png",".jpg",".jpeg")]
        return sorted(imgs)
    return []

def pil_placeholder_avatar(text="A", size=(300,300), bg="#ffd6f0"):
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(size[0]*0.4))
    except Exception:
        f = ImageFont.load_default()
    w,h = draw.textsize(text, font=f)
    draw.text(((size[0]-w)/2,(size[1]-h)/2), text, fill="#2c2c2c", font=f)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# -------------------------
# Data loading
# -------------------------
# Provide fallback small dataset if user hasn't put a real CSV yet
fallback_colleges = pd.DataFrame([
    {
        "College":"Government Degree College Sopore",
        "Location":"Baramulla",
        "Course":"BSc",
        "Future_Scope":"BSc → Research, MSc, Govt jobs",
        "Study_Materials":"Basic Physics/Chemistry/Maths textbooks",
        "Exam_Info":"University of Kashmir semester exams"
    },
    {
        "College":"Government Degree College Anantnag",
        "Location":"Anantnag",
        "Course":"BA",
        "Future_Scope":"BA → Civil Services, Masters, Teaching",
        "Study_Materials":"History/Pol. Science/English resources",
        "Exam_Info":"University semester exams & state entrance tests"
    }
])

colleges_df = load_csv_safe(COLLEGES_CSV, fallback_df=fallback_colleges)

# Load roadmaps if provided; otherwise we use built-in templates
roadmaps_df = load_csv_safe(ROADMAPS_CSV, fallback_df=None)

# -------------------------
# Predefined quiz (15 questions)
# -------------------------
QUIZ = [
    {"id":1,"q":"Do you enjoy solving logical or numerical problems?","type":"choice","opts":["Yes","No"],"tags":["science","tech"]},
    {"id":2,"q":"Do you enjoy studying living systems or helping people medically?","type":"choice","opts":["Yes","No"],"tags":["medical"]},
    {"id":3,"q":"Do you enjoy reading, writing or arts?","type":"choice","opts":["Yes","No"],"tags":["arts","creative"]},
    {"id":4,"q":"Do you enjoy working with computers and coding?","type":"choice","opts":["Yes","No"],"tags":["tech"]},
    {"id":5,"q":"Do you like working with numbers, money, and business concepts?","type":"choice","opts":["Yes","No"],"tags":["commerce","business"]},
    {"id":6,"q":"Do you enjoy practical hands-on work (lab, workshop, kitchen)?","type":"choice","opts":["Yes","No"],"tags":["vocational","practical"]},
    {"id":7,"q":"Are you interested in national defense or serving in uniformed services?","type":"choice","opts":["Yes","No"],"tags":["defense"]},
    {"id":8,"q":"Do you enjoy sports or physical training?","type":"choice","opts":["Yes","No"],"tags":["sports"]},
    {"id":9,"q":"Do you enjoy designing, visual composition or UX/UI?","type":"choice","opts":["Yes","No"],"tags":["design","creative"]},
    {"id":10,"q":"Do you prefer structured, rule-based work over freeform creativity?","type":"choice","opts":["Yes","No"],"tags":["structured"]},
    {"id":11,"q":"Do you enjoy research, reading papers and deep analysis?","type":"choice","opts":["Yes","No"],"tags":["research","science"]},
    {"id":12,"q":"Are you interested in entrepreneurship and running a business?","type":"choice","opts":["Yes","No"],"tags":["business"]},
    {"id":13,"q":"Would you consider a career in teaching or counseling?","type":"choice","opts":["Yes","No"],"tags":["teaching"]},
    {"id":14,"q":"Do you enjoy culinary arts, food science or hospitality?","type":"choice","opts":["Yes","No"],"tags":["culinary"]},
    {"id":15,"q":"Are you comfortable with public speaking and leadership roles?","type":"choice","opts":["Yes","No"],"tags":["leadership","admin"]},
]

# Mapping tags -> suggested careers (simplified clusters; extend as needed)
TAG_TO_CAREERS = {
    "science":["Scientist","Researcher","Lab Technician","Biotechnologist"],
    "tech":["Software Engineer","Data Scientist","AI Specialist","IT Support"],
    "medical":["Doctor","Nurse","Physiotherapist","Medical Lab Technician"],
    "arts":["Writer","Historian","Fine Artist","Teacher"],
    "creative":["Graphic Designer","Animator","Photographer","Content Creator"],
    "commerce":["Accountant","Business Analyst","Economist"],
    "business":["Entrepreneur","MBA / Management roles","Product Manager"],
    "vocational":["Diploma Technician","Mechanic","Culinary Professional"],
    "defense":["Army Officer","Navy Officer","Airforce Officer","Defense Scientist"],
    "sports":["Athlete","Coach","Sports Physiotherapist"],
    "design":["UX/UI Designer","Interior Designer","Industrial Designer"],
    "structured":["Accountant","Law","Admin"],
    "research":["Research Scientist","Academic"],
    "teaching":["School Teacher","Lecturer","Counselor"],
    "culinary":["Chef","Food Technologist"],
    "leadership":["Manager","Civil Services"]
}

# -------------------------
# Session state defaults (no reruns used)
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "signup_step" not in st.session_state:
    st.session_state.signup_step = 0
if "current_user" not in st.session_state:
    st.session_state.current_user = None  # dict
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []  # list of (question_id, answer)
if "suggested" not in st.session_state:
    st.session_state.suggested = []     # list of career strings
if "selected_career" not in st.session_state:
    st.session_state.selected_career = None
if "notifications" not in st.session_state:
    st.session_state.notifications = []  # messages

# -------------------------
# Helper UI pieces
# -------------------------
def top_header():
    st.markdown("""
        <div style="display:flex;align-items:center;gap:12px">
            <div style="font-size:28px;font-weight:700;color:#333">Career Compass</div>
            <div style="color:#7a6cff">Your personalized guide — focused on Jammu & Kashmir government colleges</div>
        </div>
        """, unsafe_allow_html=True)

def show_avatar_preview(path_or_none):
    if path_or_none:
        p = Path(path_or_none)
        if p.exists():
            st.image(str(p), width=140)
            return
    # fallback placeholder
    buf = pil_placeholder_avatar("U", size=(140,140))
    st.image(buf)

def progress_bar_for_quiz():
    total = len(QUIZ)
    current = st.session_state.quiz_index
    pct = int((current/total)*100)
    st.progress(pct)

def compute_suggestions_from_answers(answers):
    # answers: list of dicts with 'question_id' and 'answer' or tags
    tag_counts = {}
    for item in answers:
        qid = item.get("question_id")
        ans = item.get("answer")
        if ans == "Yes":
            # find quiz entry
            quiz_item = next((q for q in QUIZ if q['id']==qid), None)
            if quiz_item:
                for tag in quiz_item.get("tags",[]):
                    tag_counts[tag] = tag_counts.get(tag,0)+1
    # transform tag_counts to career list (ranked)
    career_scores = {}
    for tag, count in tag_counts.items():
        careers = TAG_TO_CAREERS.get(tag, [])
        for c in careers:
            career_scores[c] = career_scores.get(c,0)+count
    # sort by score desc
    sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return [c for c,score in sorted_careers]

def show_college_cards_for_career(career):
    # simple partial match on Course column
    df = colleges_df.copy()
    if df.empty:
        st.info("No college dataset found. Place `jk_colleges.csv` in the project folder.")
        return
    # we will try to match using first word of career or common mappings
    tokens = career.split()
    query = tokens[0] if tokens else career
    mask = df['Course'].str.contains(query, case=False, na=False)
    results = df[mask]
    if results.empty:
        # try alternate mapping: e.g., Engineer -> BTech, Technician -> Diploma
        alt_map = {
            "Engineer":"BTech",
            "Doctor":"MBBS",
            "Scientist":"BSc",
            "Accountant":"BCom",
            "Teacher":"BA",
            "Designer":"BDes",
            "Chef":"Diploma",
            "Athlete":"Physical Education"
        }
        alt = alt_map.get(tokens[0], "")
        if alt:
            results = df[df['Course'].str.contains(alt, case=False, na=False)]
    if results.empty:
        st.info("No matching government colleges found for this career in the dataset.")
        return
    # show as cards
    for _, r in results.iterrows():
        st.markdown(f"""
        <div style='background:#fff1f3;border-radius:12px;padding:12px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.08)'>
            <h4 style='margin:0'>{r.get('College', '')} — <small style='color:#666'>{r.get('Location','')}</small></h4>
            <div style='margin-top:6px'>
                <b>Course:</b> {r.get('Course','')} <br>
                <b>Future Scope:</b> {r.get('Future_Scope','')}<br>
                <b>Study Materials:</b> {r.get('Study_Materials','')}<br>
                <b>Exam Info:</b> {r.get('Exam_Info','')}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# Top UI (always)
# -------------------------
top_header()
st.markdown("---")

# Left sidebar: navigation + profile quick
with st.sidebar:
    if st.session_state.current_user:
        st.markdown("### Profile")
        show_avatar_preview(st.session_state.current_user.get("avatar"))
        st.markdown(f"**{st.session_state.current_user.get('name','')}**")
        st.markdown(f"{st.session_state.current_user.get('email','')}")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.menu = "Home"
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = []
            st.session_state.suggested = []
            st.session_state.selected_career = None
    else:
        st.markdown("### Not signed in")

    st.markdown("---")
    st.markdown("### Navigation")
    selection = st.radio("", ["Home","Quiz","Suggested Careers","Colleges","Profile","Notifications","About Us"], index=["Home","Quiz","Suggested Careers","Colleges","Profile","Notifications","About Us"].index(st.session_state.menu))
    st.session_state.menu = selection

# -------------------------
# Authentication (Home area)
# -------------------------
if not st.session_state.logged_in:
    st.header("Sign up / Log in")
    st.info("Create an account (email + password) — profile (name, age, avatar) comes next.")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        email_login = st.text_input("Email (login)", key="login_email")
        pwd_login = st.text_input("Password (login)", type="password", key="login_pwd")
        if st.button("Login", key="btn_login"):
            user = get_user_by_email(email_login)
            if user and str(user.get("password","")) == str(pwd_login):
                st.success("Logged in successfully")
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.session_state.menu = "Home"
                # add a small notification
                st.session_state.notifications.append("Welcome back!")
            else:
                st.error("Invalid credentials (or user doesn't exist). Please sign up if new.")
    with col2:
        st.subheader("Sign up")
        email_s = st.text_input("Email (signup)", key="signup_email")
        pwd_s = st.text_input("Password (signup)", type="password", key="signup_pwd")
        if st.button("Start Signup", key="btn_start_signup"):
            if email_s and pwd_s:
                # create a minimal record and go to profile setup step
                st.session_state.signup_temp = {"email":email_s,"password":pwd_s}
                st.session_state.signup_step = 1
                st.session_state.menu = "Profile"
                st.success("Continue to Profile setup on the Profile tab (left navigation).")
            else:
                st.warning("Enter email and password to start signup.")
    st.markdown("---")
    st.write("If you already signed up but didn't fill profile, click Profile in the navigation to complete setup.")
    st.stop()  # stop here until logged in

# -------------------------
# Logged-in user area
# -------------------------
# Ensure current_user is set for logged users
if st.session_state.logged_in and not st.session_state.current_user:
    # If we just logged in via form, set current_user
    # try to find user by the email in signup_temp or login field
    if "signup_temp" in st.session_state:
        u = get_user_by_email(st.session_state.signup_temp["email"])
        if u:
            st.session_state.current_user = u

# HOME
if st.session_state.menu == "Home":
    st.header("Home")
    if COMPASS_GIF.exists():
        st.image(str(COMPASS_GIF), width=220)
    st.markdown("> “Education and the right guidance unlock future opportunities.”")
    st.write("Use the Quiz tab to answer a short aptitude/interest questionnaire. After finishing, open Suggested Careers to see personalized options, roadmaps and colleges.")
    st.write("Quick actions:")
    c1, c2, c3 = st.columns(3)
    if c1.button("Take Quiz"):
        st.session_state.menu = "Quiz"
    if c2.button("View Colleges"):
        st.session_state.menu = "Colleges"
    if c3.button("Profile"):
        st.session_state.menu = "Profile"

# PROFILE (signup continuation, avatar + details)
elif st.session_state.menu == "Profile":
    st.header("Profile Setup / Edit")
    # if user came from signup_start temp
    if st.session_state.current_user is None and st.session_state.get("signup_temp"):
        temp = st.session_state.signup_temp
        # show profile form
        name = st.text_input("Full name", key="profile_name")
        age = st.number_input("Age", min_value=10, max_value=100, value=18, key="profile_age")
        gender = st.selectbox("Gender", ["Male","Female","Other"], key="profile_gender")
        location = st.text_input("Location (District)", key="profile_location")
        studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"], key="profile_studying")
        st.markdown("Choose avatar:")
        avatar_files = list_avatars()
        avatar_choice = None
        if avatar_files:
            cols = st.columns(min(4,len(avatar_files)))
            for i,p in enumerate(avatar_files):
                with cols[i % 4]:
                    st.image(str(p), width=100)
                    if st.button(f"Pick {i+1}", key=f"pick_{i}"):
                        avatar_choice = str(p)
                        st.session_state.temp_avatar = avatar_choice
        else:
            st.info("No avatar images found in `/avatars` folder. You can upload them to that folder or use the placeholder.")
            avatar_choice = None
        if st.button("Complete Signup"):
            # create user dict and save
            user = {
                "email": temp["email"],
                "password": temp["password"],
                "name": name,
                "age": age,
                "gender": gender,
                "location": location,
                "studying": studying,
                "avatar": st.session_state.get("temp_avatar",""),
                "your_paths":""
            }
            save_user_record(user)
            st.session_state.current_user = user
            st.session_state.logged_in = True
            st.success("Signup complete! Welcome.")
    else:
        # allow editing existing user profile
        user = st.session_state.current_user
        st.image(user.get("avatar") or pil_placeholder_avatar("U"), width=120)
        new_name = st.text_input("Full name", value=user.get("name",""))
        new_age = st.number_input("Age", min_value=10, max_value=100, value=int(user.get("age") or 18))
        new_gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(user.get("gender","Male")))
        new_location = st.text_input("Location (District)", value=user.get("location",""))
        new_studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"],
                                    index=["Schooling","Intermediate/Diploma","BTech/BSc","Other"].index(user.get("studying","Schooling")))
        if st.button("Save Profile Changes"):
            user['name']=new_name; user['age']=new_age; user['gender']=new_gender
            user['location']=new_location; user['studying']=new_studying
            save_user_record(user)
            st.session_state.current_user = user
            st.success("Profile updated.")

# QUIZ (one question at a time, progress)
elif st.session_state.menu == "Quiz":
    st.header("Career Quiz — step-by-step")
    total = len(QUIZ)
    idx = st.session_state.quiz_index
    st.write(f"Progress: {idx}/{total}")
    # show progress visually
    st.progress(min(100, int((idx/total)*100)))
    if idx < total:
        item = QUIZ[idx]
        st.subheader(f"Q{idx+1}. {item['q']}")
        ans = st.radio("Choose:", item['opts'], key=f"q_{item['id']}")
        nav_col1, nav_col2 = st.columns([1,1])
        if nav_col1.button("Previous") and idx>0:
            st.session_state.quiz_index = max(0, idx-1)
            # optionally remove last answer
            if st.session_state.quiz_answers:
                st.session_state.quiz_answers.pop()
        if nav_col2.button("Next"):
            # store answer
            st.session_state.quiz_answers.append({"question_id":item['id'], "answer":ans})
            st.session_state.quiz_index = idx+1
    else:
        st.success("Quiz complete — you can view suggested careers below")
        # compute suggestions
        suggestions = compute_suggestions_from_answers(st.session_state.quiz_answers)
        if not suggestions:
            st.info("No strong matches from quiz; try exploring the Careers tab.")
        else:
            st.session_state.suggested = suggestions
            st.markdown("### Suggested careers (click to view roadmap + colleges)")
            cols = st.columns(min(4, len(suggestions)))
            for i, career in enumerate(suggestions):
                with cols[i % 4]:
                    if st.button(career, key=f"career_btn_{i}"):
                        st.session_state.selected_career = career
                        st.session_state.menu = "Suggested Careers"
            # add notification
            st.session_state.notifications.append(f"New career suggestions: {', '.join(suggestions[:3])}")

# SUGGESTED CAREERS -> show roadmap + colleges when clicked
elif st.session_state.menu == "Suggested Careers":
    st.header("Suggested Careers")
    if not st.session_state.suggested:
        st.info("No suggestions yet — take the quiz.")
    else:
        st.write("Click a career to see roadmap and matching government colleges in J&K.")
        # if selected_career exists, display details
        sel = st.session_state.selected_career
        if sel is None:
            # show clickable list
            for i,c in enumerate(st.session_state.suggested):
                if st.button(c, key=f"show_{i}"):
                    st.session_state.selected_career = c
                    sel = c
        if sel:
            st.subheader(f"{sel} — Roadmap")
            # try roadmaps_df first if available
            if roadmaps_df is not None and not roadmaps_df.empty and 'Career' in roadmaps_df.columns:
                steps = roadmaps_df[roadmaps_df['Career'].str.contains(sel, case=False, na=False)]
                if not steps.empty:
                    for _,r in steps.iterrows():
                        st.markdown(f"- **{r.get('Step','')}** — {r.get('Detail','')}")
                else:
                    # fallback built-in roadmap template
                    display_roadmap_msg = [
                        "Complete 12th / relevant board exams",
                        "Enroll in relevant Bachelor's degree or diploma",
                        "Take internships / projects & certifications",
                        "Apply for jobs / higher studies / competitive exams"
                    ]
                    for s in display_roadmap_msg:
                        st.markdown(f"- {s}")
            else:
                # fallback
                display_roadmap_msg = [
                    "Complete 12th / relevant board exams",
                    "Enroll in relevant Bachelor's degree or diploma",
                    "Take internships / projects & certifications",
                    "Apply for jobs / higher studies / competitive exams"
                ]
                for s in display_roadmap_msg:
                    st.markdown(f"- {s}")

            st.subheader("Government colleges in J&K offering related courses")
            show_college_cards_for_career(sel)

# COLLEGES general listing & search/filter
elif st.session_state.menu == "Colleges":
    st.header("Government Colleges — Jammu & Kashmir")
    if colleges_df.empty:
        st.info("No colleges CSV found. Place `jk_colleges.csv` in project folder with columns: College,Location,Course,Future_Scope,Study_Materials,Exam_Info")
    else:
        # allow filters
        col1, col2, col3 = st.columns(3)
        with col1:
            by_course = st.text_input("Filter by Course (partial)", value="")
        with col2:
            by_location = st.text_input("Filter by Location/District (partial)", value="")
        with col3:
            limit = st.number_input("Max results", min_value=1, max_value=200, value=50)
        df = colleges_df.copy()
        if by_course:
            df = df[df['Course'].str.contains(by_course, case=False, na=False)]
        if by_location:
            df = df[df['Location'].str.contains(by_location, case=False, na=False)]
        st.write(f"Showing {min(len(df),limit)} results")
        for _, r in df.head(limit).iterrows():
            st.markdown(f"""
            <div style='background:#fff1f3;padding:12px;border-radius:12px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,0.06)'>
                <b style='font-size:16px'>{r.get('College','')}</b> — <span style='color:#666'>{r.get('Location','')}</span><br>
                <b>Course:</b> {r.get('Course','')}<br>
                <b>Future Scope:</b> {r.get('Future_Scope','')}<br>
                <b>Study Materials:</b> {r.get('Study_Materials','')}<br>
                <b>Exam Info:</b> {r.get('Exam_Info','')}
            </div>
            """, unsafe_allow_html=True)

# NOTIFICATIONS
elif st.session_state.menu == "Notifications":
    st.header("Notifications")
    if not st.session_state.notifications:
        st.info("No notifications yet — take action (quiz / profile) to generate updates.")
    else:
        for n in st.session_state.notifications[::-1]:
            st.success(n)

# ABOUT US
elif st.session_state.menu == "About Us":
    st.header("About Career Compass")
    st.markdown("""
    **Career Compass** is a lightweight personalized guidance platform focusing on students of Jammu & Kashmir.
    It helps students:
    - discover career clusters from an adaptive quiz,
    - see suggested career roadmaps,
    - find government colleges in J&K that offer relevant courses,
    - save personalized paths in profile.
    """)
    st.markdown("**Contact:** support@careercompass.local  — This is a prototype for hackathon/demo use.")

# end of script
