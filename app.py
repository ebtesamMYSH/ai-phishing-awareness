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

defaults = {
    "page": "welcome",
    "language": "en",
    "role": "",
    "role_choice": "",
    "other_role_text": "",
    "learn_index": 0,
    "test_index": 0,
    "responses": [],
    "participant_id": "",
    "zoom_image": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
                except:
                    pass

        if not numbers:
            return "P001"

        return f"P{max(numbers)+1:03d}"

    except:
        return "P001"


def save_participant_summary():

    os.makedirs("participant_data", exist_ok=True)

    csv_filename = "participant_data/all_participants_responses.csv"
    excel_filename = "participant_data/all_participants_responses.xlsx"

    if not st.session_state.participant_id:
        st.session_state.participant_id = get_next_participant_id(csv_filename)

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

    row = {
        "participant_id": st.session_state.participant_id,
        "completed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

    row["overall_percentage"] = round((total_score_10 / 10) * 100, 2)
    row["phishing_percentage"] = round((phishing_score_6 / 6) * 100, 2)
    row["legitimate_percentage"] = round((legitimate_score_4 / 4) * 100, 2)

    new_row_df = pd.DataFrame([row])

    if os.path.exists(csv_filename):
        existing_df = pd.read_csv(csv_filename)
        updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
    else:
        updated_df = new_row_df

    updated_df.to_csv(csv_filename, index=False, encoding="utf-8-sig")

    try:
        updated_df.to_excel(excel_filename, index=False, engine="openpyxl")
    except:
        pass


def apply_global_style():

    direction = "rtl" if st.session_state.language == "ar" else "ltr"
    align = "right" if st.session_state.language == "ar" else "left"

    st.markdown(f"""
    <style>

    #MainMenu,
    footer,
    header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stHeader"],
    [data-testid="stFooter"],
    [data-testid="stDeployButton"],
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK,
    .st-emotion-cache-z5fcl4,
    .st-emotion-cache-1dp5vir,
    .st-emotion-cache-79elbk,
    .st-emotion-cache-1wbqy5l,
    iframe {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* hide fullscreen image button */
    [data-testid="StyledFullScreenButton"],
    button[title="View fullscreen"],
    button[aria-label="View fullscreen"],
    [class*="fullscreen"],
    [class*="FullScreen"] {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }

    .stApp {
        background: linear-gradient(180deg, #F7F9FC 0%, #FFFFFF 100%);
        direction: {direction};
    }

    .block-container {
        max-width: 1100px !important;
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1,h2,h3,h4,p,label,div,span {
        text-align: {align};
        color: #111827 !important;
    }

    img {
        border-radius: 12px !important;
        opacity: 1 !important;
        filter: none !important;
    }

    .welcome-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 6px 22px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    .main-title {
        font-size: clamp(1.8rem,4vw,2.7rem);
        color: #123B73;
        font-weight: 800;
        line-height: 1.35;
        margin-bottom: 1rem;
    }

    .intro-text {
        color: #475569;
        font-size: 1.05rem;
        line-height: 1.8;
    }

    .section-label {
        font-size: 1.2rem;
        font-weight: 700;
        color: #123B73;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .helper-text {
        color: #4B5563;
        margin-bottom: 1rem;
    }

    .stButton {
        text-align: center !important;
    }

    .stButton > button {
        border-radius: 12px !important;
        border: 1px solid #CBD5E1 !important;
        background: white !important;
        color: #111827 !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        padding: 0.6rem 1rem !important;
        width: auto !important;
    }

    .stButton > button:hover {
        border-color: #123B73 !important;
        color: #123B73 !important;
    }

    textarea {
        min-height: 120px !important;
        border-radius: 12px !important;
    }

    .center-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 6px 22px rgba(0,0,0,0.05);
        text-align: center;
        max-width: 760px;
        margin: auto;
    }

    .completion-title {
        color: #123B73;
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .completion-text {
        color: #475569;
        line-height: 1.8;
    }

    .privacy-box {
        background: white;
        border: 1px solid #CBD5E1;
        border-radius: 14px;
        padding: 1rem;
        margin-top: 1.2rem;
        text-align: center;
    }

    @media (max-width: 768px) {

        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 100% !important;
        }

        .welcome-card {
            padding: 1.2rem !important;
        }

        .main-title {
            font-size: 2rem !important;
            line-height: 1.4 !important;
        }

        .intro-text {
            font-size: 1rem !important;
            line-height: 1.8 !important;
        }

        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }

        [data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
        }

        div[data-testid="stButton"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }

        div[data-testid="stButton"] > button {
            margin-left: auto !important;
            margin-right: auto !important;
            min-width: 150px !important;
            max-width: 260px !important;
            display: block !important;
        }

        img {
            opacity: 1 !important;
            filter: none !important;
        }
    }

    </style>
    """, unsafe_allow_html=True)


def set_role(role_value):

    st.session_state.role_choice = role_value

    if role_value != "Other":
        st.session_state.role = role_value
    else:
        st.session_state.role = ""

    rerun_app()


def role_button(label, value):

    selected = st.session_state.role_choice == value

    display_label = f"✓ {label}" if selected else label

    if st.button(display_label, key=f"role_{value}"):
        set_role(value)


def welcome_page():

    st.markdown(f"""
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
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section-label">
        {t("Select your preferred language", "اختر اللغة المناسبة")}
    </div>

    <div class="helper-text">
        {t(
            "You can continue in English or Arabic.",
            "يمكنك المتابعة باللغة العربية أو الإنجليزية."
        )}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("English"):
            st.session_state.language = "en"
            rerun_app()

    with col2:
        if st.button("العربية"):
            st.session_state.language = "ar"
            rerun_app()

    st.markdown(f"""
    <div class="section-label">
        {t("What is your role?", "ما هو مجال عملك؟")}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.language == "ar":
        role_labels = [
            ("سريري", "Clinical"),
            ("إداري / إدارة", "Admin / Management"),
            ("تقنية المعلومات", "IT / Informatics"),
            ("أخرى", "Other")
        ]
    else:
        role_labels = [
            ("Clinical", "Clinical"),
            ("Admin / Management", "Admin / Management"),
            ("IT / Informatics", "IT / Informatics"),
            ("Other", "Other")
        ]

    for label, value in role_labels:
        role_button(label, value)

    if st.session_state.role_choice == "Other":

        other_text = st.text_input(
            t("Please specify your role", "يرجى كتابة مجال عملك"),
            value=st.session_state.other_role_text
        )

        st.session_state.other_role_text = other_text.strip()

        if st.session_state.other_role_text:
            st.session_state.role = f"Other: {st.session_state.other_role_text}"
        else:
            st.session_state.role = ""

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        t("Start Training", "ابدأ التدريب"),
        key="start_training_button"
    ):

        if not st.session_state.role_choice:

            st.warning(
                t(
                    "Please select your role before starting.",
                    "يرجى اختيار مجال عملك قبل البدء."
                )
            )

        elif (
            st.session_state.role_choice == "Other"
            and not st.session_state.other_role_text
        ):

            st.warning(
                t(
                    "Please write your role before starting.",
                    "يرجى كتابة مجال عملك قبل البدء."
                )
            )

        else:
            next_page("learning")


def learning_page():

    keys = list(training.keys())

    key = keys[st.session_state.learn_index]

    item = training[key]

    st.title(
        t(
            "AI Tutor-Guided Learning Phase",
            "مرحلة التعلم الموجّه بالذكاء الاصطناعي"
        )
    )

    st.progress(
        (st.session_state.learn_index + 1) / len(keys)
    )

    st.write(
        t(
            f"Example {st.session_state.learn_index + 1} of {len(keys)}",
            f"مثال {st.session_state.learn_index + 1} من {len(keys)}"
        )
    )

    col1, col2 = st.columns([1.4, 1])

    with col1:

        show_image(item["image"])

    with col2:

        st.subheader(
            t(item["title_en"], item["title_ar"])
        )

        if st.button(
            t(
                "Explain with AI Tutor",
                "اشرح بالذكاء الاصطناعي"
            )
        ):

            with st.spinner(
                t(
                    "AI Tutor is analysing...",
                    "يقوم الذكاء الاصطناعي بالتحليل..."
                )
            ):

                time.sleep(1.5)

            st.session_state[f"show_{key}"] = True

            rerun_app()

        if st.session_state.get(f"show_{key}", False):

            st.markdown(
                "### 🤖 "
                + t("AI Tutor Analysis", "تحليل الذكاء الاصطناعي")
            )

            st.markdown(
                "#### "
                + t("What is suspicious?", "ما الشيء المشبوه؟")
            )

            st.write(
                t(item["what_en"], item["what_ar"])
            )

            st.markdown(
                "#### "
                + t("Why is it risky?", "لماذا يعتبر خطيراً؟")
            )

            st.write(
                t(item["risk_en"], item["risk_ar"])
            )

            st.markdown(
                "#### "
                + t("Learning Tip", "نصيحة تعليمية")
            )

            st.success(
                t(item["tip_en"], item["tip_ar"])
            )

    viewed = st.session_state.get(f"show_{key}", False)

    if st.session_state.learn_index < len(keys) - 1:

        if st.button(
            t("Next Example", "الصورة التالية")
        ):

            if not viewed:

                st.warning(
                    t(
                        "Please view the explanation first.",
                        "يرجى الاطلاع على الشرح أولاً."
                    )
                )

            else:

                st.session_state.learn_index += 1

                rerun_app()

    else:

        if st.button(
            t("Complete Learning", "إنهاء التعلم")
        ):

            if not viewed:

                st.warning(
                    t(
                        "Please view the explanation first.",
                        "يرجى الاطلاع على الشرح أولاً."
                    )
                )

            else:
                next_page("learning_complete")


def learning_complete_page():

    st.markdown(f"""
    <div class="center-card">
        <h2 class="completion-title">
            {t(
                "You completed the learning phase successfully.",
                "لقد أنهيت مرحلة التعلم بنجاح."
            )}
        </h2>

        <div class="completion-text">
            {t(
                "You can now continue to the assessment.",
                "يمكنك الآن الانتقال إلى الاختبار."
            )}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        t("Continue to Assessment", "الانتقال إلى الاختبار")
    ):
        next_page("post_test")


def set_test_choice(choice):

    key = f"selected_choice_{st.session_state.test_index}"

    st.session_state[key] = choice

    rerun_app()


def post_test_page():

    item = test_items[st.session_state.test_index]

    image_path = os.path.join(
        "images_test",
        item["image"]
    )

    choice_key = f"selected_choice_{st.session_state.test_index}"

    if choice_key not in st.session_state:
        st.session_state[choice_key] = None

    st.title(
        t("Assessment", "الاختبار")
    )

    st.progress(
        (st.session_state.test_index + 1)
        / len(test_items)
    )

    st.write(
        t(
            f"Question {st.session_state.test_index + 1} of {len(test_items)}",
            f"السؤال {st.session_state.test_index + 1} من {len(test_items)}"
        )
    )

    if st.session_state.zoom_image:

        show_image(image_path)

        if st.button(
            t(
                "↙ Return to normal size",
                "↙ الرجوع للحجم الطبيعي"
            )
        ):

            st.session_state.zoom_image = False

            rerun_app()

        return

    col1, col2 = st.columns([1.5, 1])

    with col1:

        show_image(image_path)

        if st.button(
            t(
                "🔍 View larger image",
                "🔍 عرض الصورة بحجم أكبر"
            )
        ):

            st.session_state.zoom_image = True

            rerun_app()

    with col2:

        st.markdown(
            f"### {t('Is this message phishing or legitimate?', 'هل هذه الرسالة تصيد إلكتروني أم شرعية؟')}"
        )

        selected = st.session_state[choice_key]

        phishing_label = (
            t("✓ Phishing", "✓ تصيد إلكتروني")
            if selected == "Phishing"
            else t("Phishing", "تصيد إلكتروني")
        )

        legitimate_label = (
            t("✓ Legitimate", "✓ رسالة شرعية")
            if selected == "Legitimate"
            else t("Legitimate", "رسالة شرعية")
        )

        if st.button(
            phishing_label,
            key=f"phishing_btn_{st.session_state.test_index}"
        ):
            set_test_choice("Phishing")

        if st.button(
            legitimate_label,
            key=f"legitimate_btn_{st.session_state.test_index}"
        ):
            set_test_choice("Legitimate")

        reason = st.text_area(
            t("Why?", "لماذا؟"),
            key=f"reason_{st.session_state.test_index}"
        )

        if st.button(
            t("Next", "التالي")
        ):

            choice = st.session_state[choice_key]

            if not choice:

                st.warning(
                    t(
                        "Please select an answer before continuing.",
                        "يرجى اختيار إجابة."
                    )
                )

                return

            if reason.strip() == "":

                st.warning(
                    t(
                        "Please write your reason.",
                        "يرجى كتابة السبب."
                    )
                )

                return

            correct_answer = item["correct_answer"]

            is_correct = choice == correct_answer

            st.session_state.responses.append({

                "participant_id":
                    st.session_state.participant_id,

                "time":
                    datetime.now().isoformat(),

                "language":
                    get_language_label(),

                "role":
                    st.session_state.role,

                "question_number":
                    st.session_state.test_index + 1,

                "image":
                    item["image"],

                "selected_answer":
                    choice,

                "correct_answer":
                    correct_answer,

                "is_correct":
                    is_correct,

                "reason":
                    reason
            })

            st.session_state.zoom_image = False

            if (
                st.session_state.test_index
                < len(test_items) - 1
            ):

                st.session_state.test_index += 1

                rerun_app()

            else:

                save_participant_summary()

                next_page("final")


def final_page():

    st.markdown(f"""
    <div class="center-card">

        <h2 class="completion-title">
            {t(
                "Thank you for completing the experiment",
                "شكراً لك على إكمال التجربة"
            )}
        </h2>

        <div class="completion-text">
            {t(
                "We appreciate your participation.",
                "نقدّر مشاركتك القيمة."
            )}
        </div>
    </div>

    <div class="privacy-box">

        🔒<br>

        {t(
            "All responses and data will be securely recorded for research purposes only.",
            "سيتم تسجيل جميع إجاباتك وبياناتك بشكل آمن لأغراض البحث فقط."
        )}

    </div>
    """, unsafe_allow_html=True)


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
