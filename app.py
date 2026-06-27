import streamlit as st
import json
import os
import base64

# ملاحظة: يجب أن يكون أول أمر في السكربت لإعدادات الواجهة والبروجكتر
st.set_page_config(page_title="منصة المعلم الذكية - إصدار الملفات المتعددة", layout="wide")

# 1. إعداد اسم المستخدم وكلمة المرور الخاصة بك
USER_CORRECT = "teacher1"
PASSWORD_CORRECT = "my_secret_pass_123"

# ملفات الحفظ التلقائي على جهازك
STUDENTS_FILE = "students_data.json"
LESSONS_FILE = "lessons_data.json"

# دالة للتحقق من تسجيل الدخول
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
                st.rerun() # إعادة تنشيط الصفحة لفتح المنصة
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة!")
        return False
    return True

# دالات شحن وحفظ البيانات تلقائياً
def load_data():
    students = {"أحمد": 10, "سارة": 15, "محمد": 8}
    lessons = {}
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            students = json.load(f)
    if os.path.exists(LESSONS_FILE):
        with open(LESSONS_FILE, "r", encoding="utf-8") as f:
            lessons = json.load(f)
    return students, lessons

def save_students():
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.students, f, ensure_ascii=False, indent=4)

def save_lessons():
    with open(LESSONS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.lessons, f, ensure_ascii=False, indent=4)

# 2. تشغيل قفل الأمان والتحقق من الهوية
if check_password():
    
    # تحضير جلسة العمل (Session State) داخل نظام الأمان
    if 'students' not in st.session_state or 'lessons' not in st.session_state:
        st.session_state.students, st.session_state.lessons = load_data()

    # تحسين مظهر الواجهة بالـ CSS لدعم اللغة العربية والخطوط المريحة للعين
    st.markdown("""
        <style>
        body, div, h1, h2, h3, p, button, label, input, span, th, td {
            direction: RTL !important;
            text-align: right !important;
            font-family: 'Cairo', sans-serif;
        }
        .stButton>button {
            width: 100%;
            font-weight: bold;
        }
        .student-box {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 5px;
        }
        .file-counter {
            background-color: #e1f5fe;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            text-align: center !important;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("👨‍🏫 منصة التدريس الذكية (دعم المحتوى المتعدد)")
    st.write("---")

    # ==================== القائمة الجانبية (Sidebar) ====================
    with st.sidebar:
        st.header("🛠️ إعداد الصف والتحضير")
        
        # 1. إدارة الطلاب
        with st.expander("👥 إدارة أسماء الطلاب", expanded=False):
            new_student = st.text_input("اسم الطالب الجديد:")
            if st.button("➕ إضافة الطالب"):
                if new_student and new_student not in st.session_state.students:
                    st.session_state.students[new_student] = 0
                    save_students()
                    st.rerun()
                    
            student_to_delete = st.selectbox("حذف طالب:", [""] + list(st.session_state.students.keys()))
            if student_to_delete != "" and st.button("🗑️ حذف الطالب المختارت"):
                del st.session_state.students[student_to_delete]
                save_students()
                st.rerun()

        st.write("---")

        # 2. إنشاء درس جديد وحفظ متطلباته المتعددة
        with st.expander("✨ إنشاء درس جديد (متعدد الملفات)", expanded=True):
            lesson_name = st.text_input("اسم الدرس الجديد:")
            
            # إدخال الفيديوهات كمشروع نصي مفصول بأسطر
            yt_links_area = st.text_area("روابط اليوتيوب (ضع كل رابط في سطر منفصل):")
            
            # تفعيل خاصية الرفع المتعدد عبر accept_multiple_files=True
            pdfs_uploaded = st.file_uploader("ارفع ملفات PDF / بوربوينت (يمكن اختيار أكثر من ملف):", type=['pdf'], accept_multiple_files=True)
            htmls_uploaded = st.file_uploader("ارفع ملفات HTML التفاعلية (يمكن اختيار أكثر من ملف):", type=['html'], accept_multiple_files=True)
            imgs_uploaded = st.file_uploader("ارفع الصور التوضيحية (يمكن اختيار أكثر من صورة):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            
            if st.button("💾 حفظ الدرس بمحتوياته"):
                if lesson_name:
                    # معالجة روابط اليوتيوب وتحويلها لقائمة
                    yt_list = [line.strip() for line in yt_links_area.split("\n") if line.strip()]
                    
                    # معالجة الملفات المتعددة وتحويلها إلى كود نصي للحفظ
                    pdf_list = [base64.b64encode(f.read()).decode('utf-8') for f in pdfs_uploaded] if pdfs_uploaded else []
                    html_list = [f.read().decode("utf-8") for f in htmls_uploaded] if htmls_uploaded else []
                    img_list = [base64.b64encode(f.read()).decode('utf-8') for f in imgs_uploaded] if imgs_uploaded else []
                    
                    # تخزين الدرس كقوائم داخل الـ JSON
                    st.session_state.lessons[lesson_name] = {
                        "youtube": yt_list,
                        "pdf": pdf_list,
                        "html": html_list,
                        "image": img_list
                    }
                    save_lessons()
                    st.success(f"تم حفظ الدرس '{lesson_name}' ويحتوي على كمية ملفات غنية!")
                    st.rerun()
                else:
                    st.error("الرجاء كتابة اسم للدرس أولاً")

        st.write("---")
        
        # 3. اختيار الدرس الحالي
        st.subheader("📚 قائمة الدروس السابقة")
        all_lessons = list(st.session_state.lessons.keys())
        selected_lesson = st.selectbox("اختر الدرس المراد شرحه الآن:", ["-- اختر درساً --"] + all_lessons)

    # ==================== قسم العرض الرئيسي (الشاشة والطلاب) ====================
    col_content, col_students = st.columns([2, 1])

    # --- لوحة تحكم النقاط (اليسار) ---
    with col_students:
        st.subheader("🏆 نقاط الطلاب")
        for student, points in list(st.session_state.students.items()):
            st.markdown(f'<div class="student-box">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.write(f"**{student}** : `{points} ن` ")
            with c2:
                if st.button("➕", key=f"p_{student}"):
                    st.session_state.students[student] += 1
                    save_students()
                    st.rerun()
            with c3:
                if st.button("➖", key=f"m_{student}"):
                    st.session_state.students[student] -= 1
                    save_students()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- شاشة عرض المحتوى المتعدد (اليمين) ---
    with col_content:
        if selected_lesson and selected_lesson != "-- اختر درساً --":
            st.subheader(f"📖 الدرس الحالي: {selected_lesson}")
            current_lesson = st.session_state.lessons[selected_lesson]
            
            tab_yt, tab_pdf, tab_html, tab_img = st.tabs(["📺 الفيديوهات", "📄 ملفات PDF", "🎮 الألعاب التفاعلية", "🖼️ معرض الصور"])
            
            with tab_yt:
                yt_urls = current_lesson.get("youtube", [])
                if yt_urls:
                    st.markdown(f'<div class="file-counter">يوجد {len(yt_urls)} فيديو متاح لهذا الدرس</div>', unsafe_allow_html=True)
                    video_choice = st.selectbox("اختر الفيديو المُراد تشغيله:", [f"فيديو رقم {i+1}" for i in range(len(yt_urls))])
                    idx = [f"فيديو رقم {i+1}" for i in range(len(yt_urls))].index(video_choice)
                    
                    url = yt_urls[idx]
                    if "watch?v=" in url:
                        url = url.replace("watch?v=", "embed/")
                    st.markdown(f'<iframe width="100%" height="450" src="{url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                else:
                    st.info("لا توجد فيديوهات مضافة.")
                    
            with tab_pdf:
                pdf_files = current_lesson.get("pdf", [])
                if pdf_files:
                    st.markdown(f'<div class="file-counter">يوجد {len(pdf_files)} ملف PDF متاح</div>', unsafe_allow_html=True)
                    pdf_choice = st.selectbox("اختر الملف/العرض المُراد عرضه:", [f"ملف رقم {i+1}" for i in range(len(pdf_files))])
                    idx = [f"ملف رقم {i+1}" for i in range(len(pdf_files))].index(pdf_choice)
                    
                    pdf_b64 = pdf_files[idx]
                    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="500" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.info("لا توجد ملفات PDF.")
                    
            with tab_html:
                html_files = current_lesson.get("html", [])
                if html_files:
                    st.markdown(f'<div class="file-counter">يوجد {len(html_files)} لعبة/ملف تفاعلي متاح</div>', unsafe_allow_html=True)
                    html_choice = st.selectbox("اختر اللعبة التفاعلية المُراد تشغيله:", [f"لعبة رقم {i+1}" for i in range(len(html_files))])
                    idx = [f"لعبة رقم {i+1}" for i in range(len(html_files))].index(html_choice)
                    
                    st.components.v1.html(html_files[idx], height=550, scrolling=True)
                else:
                    st.info("لا توجد ألعاب تفاعلية HTML.")
                    
            with tab_img:
                img_files = current_lesson.get("image", [])
                if img_files:
                    st.markdown(f'<div class="file-counter">يوجد {len(img_files)} صورة في المعرض</div>', unsafe_allow_html=True)
                    img_choice = st.selectbox("اختر الصورة المراد تكبيرها وشرحها للطلاب:", [f"صورة رقم {i+1}" for i in range(len(img_files))])
                    idx = [f"صورة رقم {i+1}" for i in range(len(img_files))].index(img_choice)
                    
                    st.image(base64.b64decode(img_files[idx]), use_container_width=True)
                else:
                    st.info("لا توجد صور مضافة.")
        else:
            st.info("👋 الرجاء اختيار درس من القائمة الجانبية لعرض محتوياته المتعددة والبدء في الشرح!")