import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="منصة المعلم الذكية - النسخة السحابية", layout="wide")

# إعداد اسم المستخدم وكلمة المرور الخاصة بك
USER_CORRECT = "teacher1"
PASSWORD_CORRECT = "123"

# ==================== الاتصال بقاعدة بيانات جوجل ====================
@st.cache_resource
def init_gsheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # قراءة المفتاح السري من الخزنة
    creds_dict = json.loads(st.secrets["GOOGLE_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    # فتح ملف الإكسل عن طريق الرابط المخفي في الخزنة (الورقة الأولى)
    sheet = client.open_by_url(st.secrets["SHEET_URL"]).sheet1
    return sheet

# دالة لتحميل البيانات من جوجل شيت (الخلية A1 للطلاب، A2 للدروس)
def load_data(sheet):
    try:
        students_str = sheet.acell('A1').value
        lessons_str = sheet.acell('A2').value
        
        students = json.loads(students_str) if students_str else {}
        lessons = json.loads(lessons_str) if lessons_str else {}
        return students, lessons
    except:
        return {}, {}

# دالات لحفظ البيانات فوراً في جوجل شيت
def save_students(sheet):
    sheet.update_acell('A1', json.dumps(st.session_state.students, ensure_ascii=False))

def save_lessons(sheet):
    sheet.update_acell('A2', json.dumps(st.session_state.lessons, ensure_ascii=False))

# ====================================================================

# دالة تحويل روابط جوجل درايف
def make_drive_preview(link):
    if "drive.google.com" in link and "/d/" in link:
        try:
            file_id = link.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"
        except:
            return link
    return link

def check_password():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 تسجيل الدخول للمنصة التعليمية")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            if username == USER_CORRECT and password == PASSWORD_CORRECT:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة!")
        return False
    return True

# ----------------- بداية تشغيل المنصة -----------------
if check_password():
    
    # الاتصال بجوجل شيت بمجرد تسجيل الدخول
    sheet = init_gsheets()
    
    if 'students' not in st.session_state or 'lessons' not in st.session_state:
        st.session_state.students, st.session_state.lessons = load_data(sheet)

    st.markdown("""
        <style>
        body, div, h1, h2, h3, p, button, label, input, span, th, td { direction: RTL !important; text-align: right !important; font-family: 'Cairo', sans-serif; }
        .stButton>button { width: 100%; font-weight: bold; }
        .student-box { background-color: #f0f2f6; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
        .file-counter { background-color: #e1f5fe; padding: 5px 10px; border-radius: 5px; font-weight: bold; text-align: center !important; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

    st.title("👨‍🏫 منصة التدريس السحابية الذكية")
    st.write("---")

    with st.sidebar:
        st.header("🛠️ إعداد الصف والتحضير")
        
        with st.expander("👥 إدارة أسماء الطلاب", expanded=False):
            new_student = st.text_input("اسم الطالب الجديد:")
            if st.button("➕ إضافة الطالب"):
                if new_student and new_student not in st.session_state.students:
                    st.session_state.students[new_student] = 0
                    save_students(sheet)
                    st.rerun()
                    
            student_to_delete = st.selectbox("حذف طالب:", [""] + list(st.session_state.students.keys()))
            if student_to_delete != "" and st.button("🗑️ حذف الطالب المختار"):
                del st.session_state.students[student_to_delete]
                save_students(sheet)
                st.rerun()

        st.write("---")

        with st.expander("✨ إضافة درس جديد", expanded=True):
            lesson_name = st.text_input("اسم الدرس:")
            yt_links_area = st.text_area("روابط الفيديوهات (رابط في كل سطر):")
            drive_links_area = st.text_area("روابط ملفات جوجل درايف (رابط في كل سطر):")
            
            if st.button("💾 حفظ الدرس السحابي"):
                if lesson_name:
                    yt_list = [line.strip() for line in yt_links_area.split("\n") if line.strip()]
                    drive_list = [line.strip() for line in drive_links_area.split("\n") if line.strip()]
                    
                    st.session_state.lessons[lesson_name] = {"youtube": yt_list, "drive_links": drive_list}
                    save_lessons(sheet)
                    st.success(f"تم حفظ الدرس بنجاح في قاعدة البيانات!")
                    st.rerun()
                else:
                    st.error("الرجاء كتابة اسم للدرس.")

        st.write("---")
        st.subheader("📚 قائمة الدروس")
        all_lessons = list(st.session_state.lessons.keys())
        selected_lesson = st.selectbox("اختر الدرس المراد شرحه الآن:", ["-- اختر درساً --"] + all_lessons)

    col_content, col_students = st.columns([2, 1])

    with col_students:
        st.subheader("🏆 نقاط الطلاب")
        for student, points in list(st.session_state.students.items()):
            st.markdown(f'<div class="student-box">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: st.write(f"**{student}** : `{points} ن` ")
            with c2:
                if st.button("➕", key=f"p_{student}"):
                    st.session_state.students[student] += 1
                    save_students(sheet)
                    st.rerun()
            with c3:
                if st.button("➖", key=f"m_{student}"):
                    st.session_state.students[student] -= 1
                    save_students(sheet)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_content:
        if selected_lesson and selected_lesson != "-- اختر درساً --":
            st.subheader(f"📖 الدرس الحالي: {selected_lesson}")
            current_lesson = st.session_state.lessons[selected_lesson]
            
            tab_yt, tab_drive = st.tabs(["📺 الفيديوهات", "☁️ ملفات جوجل درايف"])
            
            with tab_yt:
                yt_urls = current_lesson.get("youtube", [])
                if yt_urls:
                    st.markdown(f'<div class="file-counter">يوجد {len(yt_urls)} فيديو متاح</div>', unsafe_allow_html=True)
                    video_choice = st.selectbox("اختر الفيديو:", [f"فيديو رقم {i+1}" for i in range(len(yt_urls))])
                    idx = [f"فيديو رقم {i+1}" for i in range(len(yt_urls))].index(video_choice)
                    try:
                        st.video(yt_urls[idx])
                    except:
                        st.error("❌ رابط غير صالح.")
                else:
                    st.info("لا توجد فيديوهات.")
                    
            with tab_drive:
                drive_urls = current_lesson.get("drive_links", [])
                if drive_urls:
                    st.markdown(f'<div class="file-counter">يوجد {len(drive_urls)} ملف متاح للمشاهدة</div>', unsafe_allow_html=True)
                    drive_choice = st.selectbox("اختر الملف:", [f"ملف درايف رقم {i+1}" for i in range(len(drive_urls))])
                    idx = [f"ملف درايف رقم {i+1}" for i in range(len(drive_urls))].index(drive_choice)
                    
                    raw_link = drive_urls[idx]
                    preview_link = make_drive_preview(raw_link)
                    
                    st.markdown(f'<iframe src="{preview_link}" width="100%" height="600" allow="autoplay"></iframe>', unsafe_allow_html=True)
                    st.write("---")
                    st.markdown(f'[🚀 اضغط هنا لفتح الملف في نافذة مكبرة]({raw_link})')
                else:
                    st.info("لا توجد ملفات مرفوعة على جوجل درايف لهذا الدرس.")
        else:
            st.info("👋 الرجاء اختيار درس للبدء في الشرح!")
