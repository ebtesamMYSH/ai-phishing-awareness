import streamlit as st
import json
import os
import time
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="AI Tutor Phishing Awareness Training",
    layout="centered",
    initial_sidebar_state="collapsed"
)

with open("training_content.json", "r", encoding="utf-8") as f:
    training = json.load(f)

with open("test_content.json", "r", encoding="utf-8") as f:
    test_items = json.load(f)

if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "language" not in st.session_state:
    st.session_state.language = "en"
if "role" not in st.session_state:
    st.session_state.role = ""
if "learn_index" not in st.session_state:
    st.session_state.learn_index = 0
if "test_index" not in st.session_state:
    st.session_state.test_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""
if "zoom_image" not in st.session_state:
    st.session_state.zoom_image = False


def rerun_app():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def next_page(page):
    st.session_state.page = page
    rerun_app()


def t(en, ar):
    return ar if st.session_state.language == "ar" else en


def get_language_label():
    return "Arabic" if st.session_state.language == "ar" else "English"


def show_image(path):
    try:
        st.image(path, use_container_width=True)
    except TypeError:
        st.image(path, use_column_width=True)


def get_next_participant_id(filename):
    if not os.path.exists(filename):
        return "P001"

    try:
        existing_df = pd.read_csv(filename)
        if existing_df.empty or "participant_id" not in existing_df.columns:
            return "P001"

        ids = existing_df["participant_id"].dropna().astype(str).tolist()
        numbers = []

        for pid in ids:
            if pid.startswith("P"):
                try:
                    numbers.append(int(pid.replace("P", "")))
                except ValueError:
                    pass

        if not numbers:
            return "P001"

        next_number = max(numbers) + 1
        return f"P{next_number:03d}"

    except Exception:
        return "P001"


def save_participant_summary():
    os.makedirs("participant_data", exist_ok=True)

    csv_filename = "participant_data/all_participants_responses.csv"
    excel_filename = "participant_data/all_participants_responses.xlsx"

    if not st.session_state.participant_id:
        st.session_state.participant_id = get_next_participant_id(csv_filename)

    completed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    responses = st.session_state.responses

    total_score_10 = sum(1 for r in responses if r["is_correct"])

    phishing_score_6 = sum(
        1 for r in responses
        if r["correct_answer"] == "Phishing" and r["is_correct"]
    )

    legitimate_score_4 = sum(
        1 for r in responses
        if r["correct_answer"] == "Legitimate" and r["is_correct"]
    )

    overall_percentage = round((total_score_10 / 10) * 100, 2)
    phishing_percentage = round((phishing_score_6 / 6) * 100, 2)
    legitimate_percentage = round((legitimate_score_4 / 4) * 100, 2)

    row = {
        "participant_id": st.session_state.participant_id,
        "completed_time": completed_time,
        "language": get_language_label(),
        "role": st.session_state.role,
        "learning_completed": "Yes"
    }

    for i in range(1, 11):
        row[f"image{i}_answer"] = ""
        row[f"image{i}_reason"] = ""

    for r in responses:
        q = r["question_number"]
        row[f"image{q}_answer"] = r["selected_answer"]
        row[f"image{q}_reason"] = r["reason"]

    row["total_score_10"] = total_score_10
    row["phishing_score_6"] = phishing_score_6
    row["legitimate_score_4"] = legitimate_score_4
    row["overall_percentage"] = overall_percentage
    row["phishing_percentage"] = phishing_percentage
    row["legitimate_percentage"] = legitimate_percentage

    new_row_df = pd.DataFrame([row])

    if os.path.exists(csv_filename):
        existing_df = pd.read_csv(csv_filename)
        updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
    else:
        updated_df = new_row_df

    updated_df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

    try:
        updated_df.to_excel(excel_filename, index=False, engine="openpyxl")
    except Exception:
        pass


def apply_global_style():
    direction = "rtl" if st.session_state.language == "ar" else "ltr"
    align = "right" if st.session_state.language == "ar" else "left"

    st.markdown(
        f"""
        <style>
        /* Hide Streamlit default UI */
        #MainMenu,
        footer,
        header,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stHeader"],
        [data-testid="stFooter"],
        [data-testid="stDeployButton"],
        .stDeployButton,
        .viewerBadge_container__1QSob,
        .viewerBadge_link__1S137,
        .styles_viewerBadge__1yB5_,
        .viewerBadge_container,
        .viewerBadge_link,
        .viewerBadge,
        a[href*="github.com"],
        a[href*="streamlit.io"] {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
        }}

        iframe {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
        }}

        .stApp {{
            background: linear-gradient(180deg, #F7F9FC 0%, #FFFFFF 100%) !important;
            direction: {direction};
        }}

        .block-container {{
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 1120px !important;
        }}

        h1, h2, h3, h4, p, label, div, span {{
            text-align: {align};
            overflow-wrap: break-word !important;
            word-wrap: break-word !important;
            color: #111827 !important;
            opacity: 1 !important;
        }}

        img {{
            max-width: 100% !important;
            height: auto !important;
            opacity: 1 !important;
            filter: none !important;
            -webkit-filter: none !important;
        }}

        .main-title {{
            color: #123B73 !important;
            font-size: clamp(1.7rem, 5vw, 2.4rem) !important;
            font-weight: 800 !important;
            line-height: 1.3 !important;
            margin-bottom: 0.8rem !important;
        }}

        .intro-text {{
            color: #475569 !important;
            font-size: clamp(0.95rem, 3.5vw, 1.05rem) !important;
            line-height: 1.7 !important;
            max-width: 850px !important;
        }}

        .welcome-card {{
            background: #FFFFFF !important;
            border: 1px solid #E3EAF3 !important;
            border-radius: 20px !important;
            padding: 2rem 2.2rem !important;
            box-shadow: 0 8px 28px rgba(18, 59, 115, 0.08) !important;
            margin-top: 1rem !important;
        }}

        .section-label {{
            color: #123B73 !important;
            font-weight: 700 !important;
            font-size: 1.15rem !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.5rem !important;
        }}

        .helper-text {{
            color: #4B5563 !important;
            font-size: 0.95rem !important;
            margin-bottom: 1rem !important;
        }}

        .center-card {{
            background: #FFFFFF !important;
            border: 1px solid #E3EAF3 !important;
            border-radius: 20px !important;
            padding: 2.5rem 2rem !important;
            box-shadow: 0 8px 28px rgba(18, 59, 115, 0.08) !important;
            text-align: center !important;
            max-width: 760px !important;
            margin: 2rem auto 1.5rem auto !important;
        }}

        .center-card * {{
            text-align: center !important;
        }}

        .icon-large {{
            font-size: 3rem !important;
            margin-bottom: 0.8rem !important;
        }}

        .completion-title {{
            color: #123B73 !important;
            font-size: clamp(1.3rem, 5vw, 1.7rem) !important;
            font-weight: 800 !important;
            margin-bottom: 0.5rem !important;
        }}

        .completion-text {{
            color: #475569 !important;
            font-size: 1.05rem !important;
            line-height: 1.7 !important;
        }}

        .privacy-box {{
            background: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 14px !important;
            padding: 1rem 1.3rem !important;
            max-width: 760px !important;
            margin: 1rem auto !important;
            color: #334155 !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            box-shadow: 0 4px 16px rgba(18, 59, 115, 0.05) !important;
        }}

        .privacy-box * {{
            text-align: center !important;
        }}

        /* Buttons */
        .stButton > button {{
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border-radius: 12px !important;
            border: 1px solid #CBD5E1 !important;
            padding: 0.65rem 1.1rem !important;
            font-weight: 600 !important;
            white-space: normal !important;
            min-height: 48px !important;
            box-shadow: none !important;
        }}

        .stButton > button:hover {{
            border-color: #123B73 !important;
            color: #123B73 !important;
            background-color: #F8FBFF !important;
        }}

        .stButton > button[kind="primary"] {{
            background-color: #123B73 !important;
            color: #FFFFFF !important;
            border-color: #123B73 !important;
        }}

        .stButton > button[kind="primary"]:hover {{
            background-color: #0E2F5C !important;
            color: #FFFFFF !important;
            border-color: #0E2F5C !important;
        }}

        /* Radio: make options readable and remove weird dark mobile styling */
        .stRadio label,
        .stRadio div,
        .stRadio span,
        .stRadio p,
        [data-testid="stMarkdownContainer"],
        [data-testid="stWidgetLabel"],
        label {{
            color: #111827 !important;
            opacity: 1 !important;
        }}

        div[role="radiogroup"] {{
            gap: 0.65rem !important;
        }}

        div[role="radiogroup"] label {{
            background: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
            margin-bottom: 0.65rem !important;
            width: 100% !important;
            color: #111827 !important;
            opacity: 1 !important;
            box-shadow: none !important;
        }}

        div[role="radiogroup"] label * {{
            color: #111827 !important;
            opacity: 1 !important;
        }}

        div[role="radiogroup"] svg {{
            color: #111827 !important;
            fill: #111827 !important;
            opacity: 1 !important;
        }}

        textarea {{
            min-height: 120px !important;
            color: #111827 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 12px !important;
        }}

        input {{
            color: #111827 !important;
            background-color: #FFFFFF !important;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-top: 1rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
                max-width: 100% !important;
            }}

            .main-title {{
                font-size: 1.9rem !important;
                line-height: 1.35 !important;
            }}

            .intro-text {{
                font-size: 1.02rem !important;
                line-height: 1.8 !important;
            }}

            .welcome-card {{
                padding: 1.25rem !important;
                border-radius: 16px !important;
            }}

            .center-card {{
                padding: 1.4rem !important;
                margin-top: 1rem !important;
            }}

            .privacy-box {{
                padding: 1rem !important;
            }}

            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
                gap: 0.8rem !important;
            }}

            [data-testid="column"] {{
                width: 100% !important;
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }}

            .stButton > button {{
                width: 100% !important;
                margin-bottom: 0.6rem !important;
                font-size: 1rem !important;
            }}

            h1 {{
                font-size: 1.75rem !important;
                line-height: 1.35 !important;
            }}

            h2 {{
                font-size: 1.45rem !important;
            }}

            h3 {{
                font-size: 1.22rem !important;
            }}

            p, div, label, span {{
                font-size: 1rem !important;
                line-height: 1.7 !important;
            }}

            img {{
                border-radius: 12px !important;
                opacity: 1 !important;
                filter: none !important;
                -webkit-filter: none !important;
            }}

            .stImage,
            [data-testid="stImage"] {{
                opacity: 1 !important;
                filter: none !important;
                -webkit-filter: none !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def welcome_page():
    st.markdown(
        f"""
        <div class="welcome-card">
            <div class="main-title">
                {t(
                    "AI Tutor Phishing Awareness Training for Healthcare Employees",
                    "تدريب التوعية بالتصيد الإلكتروني باستخدام الذكاء الاصطناعي للموظفين الصحيين"
                )}
            </div>
            <div class="intro-text">
                {t(
                    "This interactive training will help you identify phishing attempts using guided AI Tutor explanations followed by a short assessment.",
                    "سيساعدك هذا التدريب التفاعلي على التعرّف على محاولات التصيد الإلكتروني من خلال شرح موجه باستخدام الذكاء الاصطناعي، يتبعه اختبار قصير."
                )}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="section-label">
            {t("Select your preferred language", "اختر اللغة المناسبة")}
        </div>
        <div class="helper-text">
            {t("You can continue in English or Arabic.", "يمكنك المتابعة باللغة العربية أو الإنجليزية.")}
        </div>
        """,
        unsafe_allow_html=True
    )

    lang_col1, lang_col2 = st.columns(2)

    with lang_col1:
        if st.button("English"):
            st.session_state.language = "en"
            rerun_app()

    with lang_col2:
        if st.button("العربية"):
            st.session_state.language = "ar"
            rerun_app()

    st.markdown(
        f"""
        <div class="section-label">
            {t("What is your role?", "ما هو مجال عملك؟")}
        </div>
        """,
        unsafe_allow_html=True
    )

    role_options_en = ["Clinical", "Admin / Management", "IT / Informatics", "Other"]
    role_options_ar = ["سريري", "إداري / إدارة", "تقنية المعلومات", "أخرى"]

    role_map = {
        "Clinical": "Clinical",
        "Admin / Management": "Admin / Management",
        "IT / Informatics": "IT / Informatics",
        "Other": "Other",
        "سريري": "Clinical",
        "إداري / إدارة": "Admin / Management",
        "تقنية المعلومات": "IT / Informatics",
        "أخرى": "Other"
    }

    displayed_roles = role_options_ar if st.session_state.language == "ar" else role_options_en

    selected_role = st.radio(
        "",
        displayed_roles,
        index=None,
        horizontal=False,
        label_visibility="collapsed"
    )

    if selected_role:
        st.session_state.role = role_map[selected_role]

    if st.button(t("Start Training", "ابدأ التدريب")):
        if not st.session_state.role:
            st.warning(
                t(
                    "Please select your role before starting.",
                    "يرجى اختيار مجال عملك قبل البدء."
                )
            )
        else:
            next_page("learning")


def learning_page():
    keys = list(training.keys())
    key = keys[st.session_state.learn_index]
    item = training[key]

    st.title(t("AI Tutor-Guided Learning Phase", "مرحلة التعلم الموجّه بالذكاء الاصطناعي"))
    st.progress((st.session_state.learn_index + 1) / len(keys))

    st.write(t(
        f"Example {st.session_state.learn_index + 1} of {len(keys)}",
        f"مثال {st.session_state.learn_index + 1} من {len(keys)}"
    ))

    col1, col2 = st.columns([1.45, 1])

    with col1:
        show_image(item["image"])

    with col2:
        st.subheader(t(item["title_en"], item["title_ar"]))

        if st.button(t("Explain with AI Tutor", "اشرح بالذكاء الاصطناعي التعليمي")):
            with st.spinner(
                t(
                    "🤖 AI Tutor is analysing the phishing indicators...",
                    "🤖 يقوم الذكاء الاصطناعي بتحليل مؤشرات التصيد الإلكتروني..."
                )
            ):
                time.sleep(1.5)

            st.session_state[f"show_{key}"] = True
            rerun_app()

        if st.session_state.get(f"show_{key}", False):
            st.markdown("### 🤖 " + t("AI Tutor Analysis", "تحليل الذكاء الاصطناعي التعليمي"))
            st.caption(t(
                "AI-guided phishing awareness explanation",
                "شرح توعوي موجه بالذكاء الاصطناعي"
            ))

            st.markdown("#### " + t("What is suspicious?", "ما الشيء المشبوه؟"))
            st.write(t(item["what_en"], item["what_ar"]))

            st.markdown("#### " + t("Why is it risky?", "لماذا يعتبر خطيراً؟"))
            st.write(t(item["risk_en"], item["risk_ar"]))

            st.markdown("#### " + t("Learning Tip", "نصيحة تعليمية"))
            st.success(t(item["tip_en"], item["tip_ar"]))

            st.caption(t(
                "AI-assisted educational explanation reviewed for consistency.",
                "شرح تعليمي مدعوم بالذكاء الاصطناعي وتمت مراجعته لضمان الاتساق."
            ))

    explanation_viewed = st.session_state.get(f"show_{key}", False)

    if st.session_state.learn_index < len(keys) - 1:
        if st.button(t("Next Example", "الصورة التالية")):
            if not explanation_viewed:
                st.warning(t(
                    "Please view the AI Tutor explanation before moving to the next example.",
                    "يرجى الاطلاع على شرح الذكاء الاصطناعي التعليمي قبل الانتقال إلى الصورة التالية."
                ))
            else:
                st.session_state.learn_index += 1
                rerun_app()
    else:
        if st.button(t("Complete Learning", "إنهاء التعلم")):
            if not explanation_viewed:
                st.warning(t(
                    "Please view the AI Tutor explanation before completing the learning phase.",
                    "يرجى الاطلاع على شرح الذكاء الاصطناعي التعليمي قبل إنهاء مرحلة التعلم."
                ))
            else:
                next_page("learning_complete")


def learning_complete_page():
    st.markdown(
        f"""
        <div class="center-card">
            <div class="icon-large">🎓</div>
            <div class="completion-title">
                {t("You have successfully completed the learning phase.", "لقد أنهيت مرحلة التعلم بنجاح.")}
            </div>
            <div class="completion-text">
                {t("You can now continue to the assessment.", "يمكنك الآن الانتقال إلى الاختبار.")}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(t("Continue to Assessment", "الانتقال إلى الاختبار")):
        next_page("post_test")


def post_test_page():
    item = test_items[st.session_state.test_index]
    image_path = os.path.join("images_test", item["image"])
    choice_key = f"selected_choice_{st.session_state.test_index}"

    if choice_key not in st.session_state:
        st.session_state[choice_key] = None

    st.title(t("Assessment", "الاختبار"))
    st.progress((st.session_state.test_index + 1) / len(test_items))

    st.write(t(
        f"Question {st.session_state.test_index + 1} of {len(test_items)}",
        f"السؤال {st.session_state.test_index + 1} من {len(test_items)}"
    ))

    if st.session_state.zoom_image:
        show_image(image_path)

        if st.button(t("↙ Return to normal size", "↙ الرجوع للحجم الطبيعي")):
            st.session_state.zoom_image = False
            rerun_app()

        return

    col1, col2 = st.columns([1.55, 1])

    with col1:
        show_image(image_path)

        if st.button(t("🔍 View larger image", "🔍 عرض الصورة بحجم أكبر")):
            st.session_state.zoom_image = True
            rerun_app()

    with col2:
        st.markdown(
            f"### {t('Is this message phishing or legitimate?', 'هل هذه الرسالة تصيد إلكتروني أم رسالة شرعية؟')}"
        )

        phishing_selected = st.session_state[choice_key] == "Phishing"
        legitimate_selected = st.session_state[choice_key] == "Legitimate"

        b1, b2 = st.columns(2)

        with b1:
            if st.button(
                t("Phishing", "تصيد إلكتروني"),
                key=f"phishing_btn_{st.session_state.test_index}",
                type="primary" if phishing_selected else "secondary"
            ):
                st.session_state[choice_key] = "Phishing"
                rerun_app()

        with b2:
            if st.button(
                t("Legitimate", "رسالة شرعية"),
                key=f"legitimate_btn_{st.session_state.test_index}",
                type="primary" if legitimate_selected else "secondary"
            ):
                st.session_state[choice_key] = "Legitimate"
                rerun_app()

        reason = st.text_area(
            t("Why?", "لماذا؟"),
            key=f"reason_{st.session_state.test_index}"
        )

        if st.button(t("Next", "التالي")):
            choice = st.session_state[choice_key]

            if not choice:
                st.warning(t(
                    "Please select an answer before continuing.",
                    "يرجى اختيار إجابة قبل المتابعة."
                ))
                return

            if reason.strip() == "":
                st.warning(t(
                    "Please write your reason before continuing.",
                    "يرجى كتابة السبب قبل المتابعة."
                ))
                return

            selected_answer = choice
            correct_answer = item["correct_answer"]
            is_correct = selected_answer == correct_answer

            st.session_state.responses.append({
                "participant_id": st.session_state.participant_id,
                "time": datetime.now().isoformat(),
                "language": get_language_label(),
                "role": st.session_state.role,
                "question_number": st.session_state.test_index + 1,
                "image": item["image"],
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "reason": reason
            })

            st.session_state.zoom_image = False

            if st.session_state.test_index < len(test_items) - 1:
                st.session_state.test_index += 1
                rerun_app()
            else:
                save_participant_summary()
                next_page("final")


def final_page():
    st.markdown(
        f"""
        <div class="center-card">
            <div class="icon-large">✅</div>
            <div class="completion-title">
                {t("Thank you for completing the experiment", "شكراً لك على إكمال التجربة")}
            </div>
            <div class="completion-text">
                {t("We appreciate your time and valuable participation.", "نقدر وقتك ومشاركتك القيمة.")}
                <br>
                {t("Your contribution helps enhance phishing cybersecurity awareness.", "مساهمتك تساعد في تعزيز الوعي الأمني بالتصيد الاحتيالي.")}
            </div>
            <div class="icon-large">🎉</div>
        </div>

        <div class="privacy-box">
            🔒<br>
            {t(
                "All responses and data will be securely recorded for research purposes only. Your privacy and data confidentiality are fully protected.",
                "سيتم تسجيل جميع إجاباتك وبياناتك بشكل آمن لأغراض البحث فقط. خصوصيتك وسرية بياناتك محمية بالكامل."
            )}
        </div>
        """,
        unsafe_allow_html=True
    )


apply_global_style()

if st.session_state.page == "welcome":
    welcome_page()
elif st.session_state.page == "learning":
    learning_page()
elif st.session_state.page == "learning_complete":
    learning_complete_page()
elif st.session_state.page == "post_test":
    post_test_page()
elif st.session_state.page == "final":
    final_page()
