# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import os
# ---------------------------
# Configuration / Paths
# ---------------------------
st.set_page_config(page_title="Career Compass",page_icon="🧭", layout="wide")
BASE = Path(".")
IMAGES_DIRS = [BASE / "images", BASE / "avatars"]
COLLEGES_PATHS = [BASE / "jk_colleges.csv", Path("/mnt/data/jk_colleges.csv")]
COMPASS_GIF = BASE / "compass.gif"
USERS_CSV = BASE / "users.csv"

# ---------------------------
# Utility helpers
# ---------------------------
def load_colleges():
    for p in COLLEGES_PATHS:
        if p.exists():
            try:
                df = pd.read_csv(p)
                # normalize column names (allow older formats)
                df.columns = [c.strip() for c in df.columns]
                # prefer these column names:
                # Accept either (College_Name, District, Courses_Offered) or (College,Location,Course,...)
                # Convert common variants to standard names used below
                if "College_Name" in df.columns and "Courses_Offered" in df.columns:
                    df = df.rename(columns={
                        "College_Name":"College",
                        "District":"Location",
                        "Courses_Offered":"Course"
                    })
                # ensure required columns exist or add empty
                for col in ["College","Location","Course","Future_Scope","Study_Materials","Exam_Info"]:
                    if col not in df.columns:
                        df[col] = ""
                return df[["College","Location","Course","Future_Scope","Study_Materials","Exam_Info"]]
            except Exception as e:
                st.warning(f"Could not read colleges CSV at {p}: {e}")
    # fallback sample
    return pd.DataFrame([{
        "College":"Government Degree College Sopore",
        "Location":"Baramulla",
        "Course":"BSc",
        "Future_Scope":"Research, MSc, Govt jobs",
        "Study_Materials":"Physics/Chemistry/Math notes",
        "Exam_Info":"University exams (CUET/JKCET)"
    }])

def ensure_users_csv():
    if not USERS_CSV.exists():
        pd.DataFrame(columns=["email","password","name","age","gender","location","studying","avatar","your_paths"]).to_csv(USERS_CSV,index=False)

def save_user_record(user: dict):
    ensure_users_csv()
    df = pd.read_csv(USERS_CSV)
    df = df[df['email'] != user['email']]  # remove old
    df = pd.concat([df, pd.DataFrame([user])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)

def get_user_by_email(email):
    ensure_users_csv()
    df = pd.read_csv(USERS_CSV)
    row = df[df['email'] == email]
    if not row.empty:
        return row.iloc[0].to_dict()
    return None

def list_avatars():
    imgs = []
    for d in IMAGES_DIRS:
        if d.exists():
            imgs += sorted([p for p in d.iterdir() if p.suffix.lower() in [".png",".jpg",".jpeg"]])
    return imgs

def placeholder_image(text="U", size=(240,240), bg="#ffd6f0"):
    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", int(size[0]*0.4))
    except Exception:
        f = ImageFont.load_default()
    w,h = draw.textsize(text, font=f)
    draw.text(((size[0]-w)/2,(size[1]-h)/2), text, fill="#222", font=f)
    b = io.BytesIO()
    img.save(b, format="PNG")
    b.seek(0)
    return b

# ---------------------------
# Load data
# ---------------------------
colleges_df = load_colleges()

# ---------------------------
# Predefined Quiz (15 questions)
# ---------------------------
QUIZ = [
    {"id":1,"q":"Do you enjoy solving logical or numerical problems?","opts":["Yes","No"],"tags":["science","tech"]},
    {"id":2,"q":"Do you enjoy biology/medical topics and helping people medically?","opts":["Yes","No"],"tags":["medical"]},
    {"id":3,"q":"Do you enjoy reading, writing or arts?","opts":["Yes","No"],"tags":["arts","creative"]},
    {"id":4,"q":"Do you enjoy coding, building software or apps?","opts":["Yes","No"],"tags":["tech"]},
    {"id":5,"q":"Do you like working with money, business or commerce?","opts":["Yes","No"],"tags":["commerce","business"]},
    {"id":6,"q":"Do you enjoy hands-on/practical work (labs, workshops, kitchens)?","opts":["Yes","No"],"tags":["vocational"]},
    {"id":7,"q":"Are you interested in defense and uniformed services?","opts":["Yes","No"],"tags":["defense"]},
    {"id":8,"q":"Do you enjoy sports, fitness, or physical training?","opts":["Yes","No"],"tags":["sports"]},
    {"id":9,"q":"Do you like designing graphics, UX or visual products?","opts":["Yes","No"],"tags":["design","creative"]},
    {"id":10,"q":"Do you prefer structured/rule-based work vs freeform creativity?","opts":["Structured","Creative"],"tags":["structured","creative"]},
    {"id":11,"q":"Do you enjoy research, experiments and in-depth study?","opts":["Yes","No"],"tags":["research"]},
    {"id":12,"q":"Are you inclined toward entrepreneurship or running a business?","opts":["Yes","No"],"tags":["business"]},
    {"id":13,"q":"Would you consider a career in teaching or counseling?","opts":["Yes","No"],"tags":["teaching"]},
    {"id":14,"q":"Do you like cooking, food science or hospitality?","opts":["Yes","No"],"tags":["culinary"]},
    {"id":15,"q":"Are you comfortable with public speaking and leadership roles?","opts":["Yes","No"],"tags":["leadership"]},
]

# tag->careers mapping (expandable)
TAG_CAREER_MAP = {
    "science":["Scientist","Researcher","Lab Technician","Biotechnologist"],
    "tech":["Software Engineer","Data Scientist","IT Specialist","Web Developer"],
    "medical":["Doctor","Nurse","Medical Lab Technician","Physiotherapist"],
    "arts":["Writer","Teacher","Historian"],
    "creative":["Graphic Designer","Animator","Content Creator"],
    "commerce":["Accountant","Business Analyst","Economist"],
    "business":["Entrepreneur","Manager","BBA roles"],
    "vocational":["Diploma Technician","Mechanic","Culinary Professional"],
    "defense":["Army Officer","Navy Officer","Airforce Officer"],
    "sports":["Athlete","Coach","Sports Physiotherapist"],
    "design":["UX Designer","Product Designer"],
    "structured":["Accountant","Law"],
    "research":["Research Scientist","Academic"],
    "teaching":["Teacher","Lecturer","Counselor"],
    "culinary":["Chef","Food Technologist"],
    "leadership":["Manager","Civil Services"]
}

# Roadmaps templates: simple multi-step lists (extendable)
ROADMAP_TEMPLATES = {
    "Software Engineer":["12th (Maths/Comp Sci)","B.Tech / BSc CS / BCA","Internship & Projects","Jobs / Startups / Higher Studies"],
    "Data Scientist":["12th (Maths)","BSc / BStat / BTech + Statistics/CS","Projects & Internships","Jobs / Research / Masters"],
    "Doctor":["12th (PCB)","MBBS (Medical College)","Internship / Residency","Specialization / Practice / Research"],
    "Engineer":["12th (PCM)","B.Tech / B.E.","Internship & Placements","MTech / Industry"],
    "Army Officer":["12th / Graduation","NDA / CDS / SSB","Commission & Training","Service & Leadership"],
    "Chef":["Schooling","Culinary Diploma / BSc Food Tech","Apprenticeship","Restaurant / Own Business"],
    "Teacher":["12th","BA / BEd / BSc + BEd","Practice & Certifications","School / College Teaching"],
    "Graphic Designer":["12th","B.Des / Diploma in Design","Portfolio & Internships","Agency / Freelance / In-house"],
}

# ---------------------------
# Session state defaults
# ---------------------------
if "menu" not in st.session_state: st.session_state.menu = "login"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "temp_signup" not in st.session_state: st.session_state.temp_signup = None
if "current_user" not in st.session_state: st.session_state.current_user = None
if "quiz_index" not in st.session_state: st.session_state.quiz_index = 0
if "quiz_answers" not in st.session_state: st.session_state.quiz_answers = []  # list of dicts {qid, answer}
if "suggested_careers" not in st.session_state: st.session_state.suggested_careers = []
if "selected_career" not in st.session_state: st.session_state.selected_career = None
if "notifications" not in st.session_state: st.session_state.notifications = ["Welcome to Career Compass — Complete the quiz to get personalized suggestions!"]

# ---------------------------
# UI helpers
# ---------------------------
def header_area():
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px">
      <div style="font-size:28px;font-weight:700;color:#333">Career Compass</div>
      <div style="color:#7a6cff">Personalized career & college guidance — Jammu & Kashmir focus</div>
    </div>
    """, unsafe_allow_html=True)

def show_avatar(user):
    try:
        avatar = user.get("avatar","")
        if avatar and Path(avatar).exists():
            st.image(str(avatar), width=120)
        else:
            st.image(placeholder_image(user.get("name","U")), width=120)
    except Exception:
        st.image(placeholder_image("U"), width=120)

def placeholder_image(text, size=(160,160)):
    b = placeholder_image_bytes(text, size)
    return b

def placeholder_image_bytes(text="U", size=(160,160)):
    img = Image.new("RGB", size, "#ffd6f0")
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", int(size[0]*0.4))
    except Exception:
        f = ImageFont.load_default()
    w,h = d.textsize(text, font=f)
    d.text(((size[0]-w)/2,(size[1]-h)/2), text, fill="#222", font=f)
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return buf

def compute_suggestions():
    # count tags from answers
    tag_counts = {}
    for a in st.session_state.quiz_answers:
        if a["answer"] in ("Yes","Structured","Creative"):  # treat Structured/Creative as positive selections
            q = next((q for q in QUIZ if q["id"]==a["qid"]), None)
            if q:
                for tag in q.get("tags",[]):
                    tag_counts[tag] = tag_counts.get(tag,0)+1
    # map tag_counts to careers
    career_scores = {}
    for tag, ccount in tag_counts.items():
        careers = TAG_CAREER_MAP.get(tag, [])
        for c in careers:
            career_scores[c] = career_scores.get(c,0) + ccount
    # sort top careers
    sorted_c = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    return [c for c,_ in sorted_c]

def show_colleges_for_career(career):
    # try to match by common token
    df = colleges_df.copy()
    if df.empty:
        st.info("Colleges dataset not provided. Place jk_colleges.csv in your project folder.")
        return
    token = career.split()[0]
    mask = df['Course'].astype(str).str.contains(token, case=False, na=False)
    results = df[mask]
    # fallback mapping
    alt = {
        "Engineer":"BTech",
        "Doctor":"MBBS",
        "Scientist":"BSc",
        "Software":"BCA,BSc,BE,BTech",
        "Accountant":"BCom",
        "Teacher":"BA,BEd"
    }
    if results.empty and token in alt:
        for key in alt[token].split(","):
            results = pd.concat([results, df[df['Course'].astype(str).str.contains(key, case=False, na=False)]])
    if results.empty:
        st.info("No government colleges in dataset match that career. Try searching by course in Colleges tab.")
        return
    for _, row in results.drop_duplicates().iterrows():
        st.markdown(f"""
            <div style='background:#fff1f3;padding:14px;border-radius:10px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,0.06)'>
                <b>{row.get('College','')}</b> — <span style='color:#666'>{row.get('Location','')}</span><br>
                <b>Course:</b> {row.get('Course','')}<br>
                <b>Future Scope:</b> {row.get('Future_Scope','')}<br>
                <b>Study Materials:</b> {row.get('Study_Materials','')}<br>
                <b>Exam Info:</b> {row.get('Exam_Info','')}
            </div>
        """, unsafe_allow_html=True)

# ---------------------------
# Top header + sidebar
# ---------------------------
header_area()
st.markdown("---")

with st.sidebar:
    st.markdown("### Navigation")
    if not st.session_state.logged_in:
        choice = st.radio("", ["Login / Sign up", "About Us"])
        st.session_state.menu = "auth" if choice=="Login / Sign up" else "about"
    else:
        choice = st.radio("", ["Home","Quiz","Suggested Careers","Colleges","Notifications","Profile","About Us"])
        st.session_state.menu = choice

    st.markdown("---")
    if st.session_state.logged_in and st.session_state.current_user:
        u = st.session_state.current_user
        try:
            if u.get("avatar") and Path(u["avatar"]).exists():
                st.image(u["avatar"], width=100)
            else:
                st.image(placeholder_image_bytes(u.get("name","U")), width=100)
        except Exception:
            st.image(placeholder_image_bytes("U"), width=100)
        st.markdown(f"**{u.get('name','')}**")
        st.markdown(u.get("email",""))
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = []
            st.session_state.suggested_careers = []
            st.session_state.selected_career = None
            st.session_state.notifications.append("You logged out.")

# ---------------------------
# AUTH: Login / Signup / Profile setup
# ---------------------------
if not st.session_state.logged_in:
    st.header("Login or Sign up")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        login_email = st.text_input("Email", key="login_email")
        login_pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login", key="btn_login"):
            user = get_user_by_email(login_email)
            if user and str(user.get("password","")) == str(login_pwd):
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.session_state.menu = "Home"
                st.success(f"Welcome back, {user.get('name','User')}!")
            else:
                st.error("Invalid credentials or user not found.")
    with col2:
        st.subheader("Sign up (email + password)")
        signup_email = st.text_input("Email for signup", key="signup_email")
        signup_pwd = st.text_input("Password for signup", type="password", key="signup_pwd")
        if st.button("Start Sign up", key="btn_start_signup"):
            if signup_email and signup_pwd:
                if get_user_by_email(signup_email):
                    st.error("Email already registered. Login instead.")
                else:
                    st.session_state.temp_signup = {"email":signup_email,"password":signup_pwd}
                    st.info("Now go to Profile tab to complete signup (enter name, age, choose avatar).")
                    # set menu to Profile so user can click
                    st.session_state.menu = "Profile"
            else:
                st.warning("Enter both email and password to start signup.")

    st.markdown("---")
    st.markdown("Why sign up? So you can save your paths, get notifications, and revisit quiz results.")
    st.stop()

# ---------------------------
# LOGGED-IN: main pages
# ---------------------------
menu = st.session_state.menu

# HOME
if menu == "Home":
    st.header("Welcome to Career Compass")
    if COMPASS_GIF.exists():
        try:
            st.image(str(COMPASS_GIF), width=220)
        except Exception:
            pass
    st.markdown("> “Education is the key to unlocking your future.”")
    st.write("Pastel UI, easy navigation. Start by taking the quiz to get personalized career suggestions.")

# PROFILE (complete signup or edit)
elif menu == "Profile":
    st.header("Profile Setup / Edit")
    # if user doesn't yet exist (signup in progress)
    if st.session_state.temp_signup and not st.session_state.current_user:
        st.info("Finish signup: enter profile details below.")
        name = st.text_input("Full name", key="p_name")
        age = st.number_input("Age", 10, 100, key="p_age")
        gender = st.selectbox("Gender", ["Male","Female","Other"], key="p_gender")
        location = st.text_input("Location / District", key="p_location")
        studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"], key="p_studying")
        st.write("Choose avatar (if folder images exist) or leave blank for default.")
        avatars = list_avatars()
        selected_avatar = st.selectbox("Avatar (choose file path)", [""] + [str(p) for p in avatars], key="p_avatar")
        if st.button("Complete Signup & Save Profile"):
            user = {
                "email": st.session_state.temp_signup["email"],
                "password": st.session_state.temp_signup["password"],
                "name": name,
                "age": age,
                "gender": gender,
                "location": location,
                "studying": studying,
                "avatar": selected_avatar,
                "your_paths":""
            }
            save_user_record(user)
            st.session_state.current_user = user
            st.session_state.logged_in = True
            st.session_state.temp_signup = None
            st.success("Signup complete — welcome!")
    else:
        # edit existing profile
        user = st.session_state.current_user
        if not user:
            st.info("No profile found — use Signup to create one.")
        else:
            st.image(user.get("avatar") or placeholder_image_bytes(user.get("name","U")), width=120)
            new_name = st.text_input("Full Name", value=user.get("name",""))
            new_age = st.number_input("Age", 10, 100, value=int(user.get("age") or 18))
            new_gender = st.selectbox("Gender", ["Male","Female","Other"], index=["Male","Female","Other"].index(user.get("gender","Male")))
            new_location = st.text_input("Location / District", value=user.get("location",""))
            new_studying = st.selectbox("Currently studying", ["Schooling","Intermediate/Diploma","BTech/BSc","Other"], index=0)
            if st.button("Save Profile Changes"):
                user['name']=new_name; user['age']=new_age; user['gender']=new_gender
                user['location']=new_location; user['studying']=new_studying
                save_user_record(user)
                st.session_state.current_user = user
                st.success("Profile updated.")

# QUIZ
elif menu == "Quiz":
    st.header("Personalized Career Quiz")
    total = len(QUIZ)
    idx = st.session_state.quiz_index
    st.write(f"Question {idx+1} of {total}")
    st.progress(int((idx/total)*100))
    if idx < total:
        q = QUIZ[idx]
        st.subheader(q["q"])
        if q["opts"] == ["Structured","Creative"]:
            ans = st.radio("Select", q["opts"], key=f"q_{q['id']}")
        else:
            ans = st.radio("Select", q["opts"], key=f"q_{q['id']}")
        cola, colb = st.columns(2)
        with cola:
            if st.button("Previous") and idx>0:
                # move back one and remove last stored answer if exists
                if st.session_state.quiz_answers:
                    st.session_state.quiz_answers.pop()
                st.session_state.quiz_index = idx-1
        with colb:
            if st.button("Next"):
                # record answer
                st.session_state.quiz_answers.append({"qid":q["id"], "answer":ans})
                st.session_state.quiz_index = idx+1
    else:
        st.success("Quiz completed!")
        # compute suggestions
        suggestions = compute_suggestions()
        if not suggestions:
            # fallback: pick some generic careers
            suggestions = ["Software Engineer","Engineer","Teacher","Chef","Army Officer"]
        st.session_state.suggested_careers = suggestions
        st.markdown("### Suggested Careers (click to view roadmap & colleges)")
        cols = st.columns(min(4, len(suggestions)))
        for i, c in enumerate(suggestions):
            with cols[i % 4]:
                if st.button(c, key=f"suggest_{i}"):
                    st.session_state.selected_career = c
                    st.session_state.menu = "Suggested Careers"
        if st.button("Retake Quiz"):
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = []
            st.session_state.suggested_careers = []
            st.session_state.selected_career = None

# SUGGESTED CAREERS -> ROADMAP + COLLEGES
elif menu == "Suggested Careers":
    st.header("Suggested Careers & Roadmaps")
    if not st.session_state.suggested_careers:
        st.info("No suggestions yet — take quiz first.")
    else:
        if st.session_state.selected_career is None:
            st.write("Click a career to view full roadmap + matching J&K government colleges.")
            for i,c in enumerate(st.session_state.suggested_careers):
                if st.button(c, key=f"pickc_{i}"):
                    st.session_state.selected_career = c
        else:
            c = st.session_state.selected_career
            st.subheader(f"{c} — Roadmap")
            steps = ROADMAP_TEMPLATES.get(c, ["12th / Relevant Diploma","Undergrad Degree","Internship / Projects","Jobs / Higher Studies"])
            for s in steps:
                st.markdown(f"- {s}")
            st.subheader("Matching Government Colleges in Jammu & Kashmir")
            show_colleges_for_career(c)
            if st.button("Back to suggestions"):
                st.session_state.selected_career = None

# COLLEGES (search/filter)
elif menu == "Colleges":
    st.header("Government Colleges — Jammu & Kashmir")
    if colleges_df.empty:
        st.info("No colleges CSV found. Place 'jk_colleges.csv' in project folder.")
    else:
        c1,c2,c3 = st.columns(3)
        with c1:
            q_course = st.text_input("Search Course (partial)", value="")
        with c2:
            q_loc = st.text_input("Search Location/District (partial)", value="")
        with c3:
            maxr = st.number_input("Max results", min_value=1, max_value=200, value=50)
        df = colleges_df.copy()
        if q_course:
            df = df[df['Course'].astype(str).str.contains(q_course, case=False, na=False)]
        if q_loc:
            df = df[df['Location'].astype(str).str.contains(q_loc, case=False, na=False)]
        st.write(f"Showing {min(len(df), maxr)} results")
        for _, r in df.head(maxr).iterrows():
            st.markdown(f"""
                <div style='background:#fff1f3;padding:12px;border-radius:12px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,0.06)'>
                    <b>{r.get('College','')}</b> — <span style='color:#666'>{r.get('Location','')}</span><br>
                    <b>Course:</b> {r.get('Course','')}<br>
                    <b>Future Scope:</b> {r.get('Future_Scope','')}<br>
                    <b>Study Materials:</b> {r.get('Study_Materials','')}<br>
                    <b>Exam Info:</b> {r.get('Exam_Info','')}
                </div>
            """, unsafe_allow_html=True)

# NOTIFICATIONS
elif menu == "Notifications":
    st.header("Notifications")
    if not st.session_state.notifications:
        st.info("No notifications yet.")
    else:
        for n in reversed(st.session_state.notifications):
            st.success(n)

# ABOUT US
elif menu == "About Us":
    st.header("About Career Compass (SIH Project)")
    st.markdown("""
    **Problem statement:** Many students and parents are unclear about the importance of graduation,
    what degree courses offer and how courses map to careers. Career Compass helps students (especially
    in Jammu & Kashmir) choose suitable streams, explore government colleges, and plan roadmaps.
    """)
    st.subheader("Contact")
    st.write("- Email: support@careercompass.in")
    st.write("- Phone: +91 98765 43210")
    st.write("- Address: 123 Education Lane, Srinagar, Jammu & Kashmir")

# ---------------------------
# End of app
# ---------------------------
