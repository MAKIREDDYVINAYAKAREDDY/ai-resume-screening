import requests
import streamlit as st


# ============================================================
# API CONFIGURATION
# ============================================================

import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

LOGIN_API_URL = f"{API_BASE_URL}/auth/login"
REGISTER_API_URL = f"{API_BASE_URL}/auth/register"
ME_API_URL = f"{API_BASE_URL}/auth/me"

SCREEN_API_URL = f"{API_BASE_URL}/screen"
RESULTS_API_URL = f"{API_BASE_URL}/results"
HISTORY_API_URL = f"{API_BASE_URL}/history"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "screening_results" not in st.session_state:
    st.session_state["screening_results"] = None

if "selected_history_run" not in st.session_state:
    st.session_state["selected_history_run"] = None


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def is_authenticated():
    return bool(
        st.session_state.get(
            "access_token"
        )
    )


def auth_headers():
    token = st.session_state.get(
        "access_token"
    )

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }


def clear_authentication():
    st.session_state["access_token"] = None
    st.session_state["current_user"] = None
    st.session_state["screening_results"] = None
    st.session_state["selected_history_run"] = None


def login_user(username, password):
    try:
        response = requests.post(
            LOGIN_API_URL,
            data={
                "username": username,
                "password": password,
            },
            timeout=30,
        )

    except requests.RequestException as exc:
        return False, f"Could not connect to API: {exc}"

    if response.status_code != 200:
        try:
            data = response.json()
            message = data.get(
                "message",
                data.get(
                    "detail",
                    response.text,
                ),
            )
        except ValueError:
            message = response.text

        return False, (
            f"Login failed: {message}"
        )

    try:
        data = response.json()
    except ValueError:
        return False, "API returned an invalid login response."

    token = data.get(
        "access_token"
    )

    user = data.get(
        "user"
    )

    if not token or not user:
        return False, (
            "Login response did not contain "
            "a valid access token or user."
        )

    st.session_state[
        "access_token"
    ] = token

    st.session_state[
        "current_user"
    ] = user

    return True, None


def register_user(
    username,
    email,
    password,
):
    try:
        response = requests.post(
            REGISTER_API_URL,
            json={
                "username": username,
                "email": email,
                "password": password,
            },
            timeout=30,
        )

    except requests.RequestException as exc:
        return False, (
            f"Could not connect to API: {exc}"
        )

    if response.status_code not in (200, 201):
        try:
            data = response.json()

            message = data.get(
                "message",
                data.get(
                    "detail",
                    response.text,
                ),
            )

        except ValueError:
            message = response.text

        return False, (
            f"Registration failed: {message}"
        )

    return True, None


def validate_current_session():
    if not is_authenticated():
        return False

    try:
        response = requests.get(
            ME_API_URL,
            headers=auth_headers(),
            timeout=15,
        )

    except requests.RequestException:
        return True

    if response.status_code == 200:

        try:
            st.session_state[
                "current_user"
            ] = response.json()
        except ValueError:
            pass

        return True

    if response.status_code == 401:
        clear_authentication()
        return False

    return True


# ============================================================
# LOGIN / REGISTRATION PAGE
# ============================================================

def render_authentication():

    st.title(
        "📄 AI Resume Screening"
    )

    st.caption(
        "Secure AI-powered resume screening "
        "and job matching platform."
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Register",
        ]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader(
            "Login to your account"
        )

        with st.form(
            "login_form"
        ):

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            login_button = st.form_submit_button(
                "🔐 Login",
                type="primary",
                use_container_width=True,
            )

        if login_button:

            if not username.strip():
                st.error(
                    "Please enter your username."
                )

            elif not password:
                st.error(
                    "Please enter your password."
                )

            else:

                with st.spinner(
                    "Signing you in..."
                ):

                    success, error = login_user(
                        username.strip(),
                        password,
                    )

                if success:

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

                else:

                    st.error(
                        error
                    )

    # ========================================================
    # REGISTRATION
    # ========================================================

    with register_tab:

        st.subheader(
            "Create a recruiter account"
        )

        st.info(
            "New accounts are created with the "
            "recruiter role. Administrator accounts "
            "are not created through public registration."
        )

        with st.form(
            "register_form"
        ):

            new_username = st.text_input(
                "Username",
                placeholder="Choose a username",
                key="register_username",
            )

            new_email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="register_email",
            )

            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Minimum 8 characters",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Repeat your password",
                key="register_confirm_password",
            )

            register_button = st.form_submit_button(
                "📝 Create Account",
                use_container_width=True,
            )

        if register_button:

            if len(
                new_username.strip()
            ) < 3:

                st.error(
                    "Username must contain at least 3 characters."
                )

            elif not new_email.strip():

                st.error(
                    "Please enter your email address."
                )

            elif len(new_password) < 8:

                st.error(
                    "Password must contain at least 8 characters."
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                with st.spinner(
                    "Creating your account..."
                ):

                    success, error = register_user(
                        new_username.strip(),
                        new_email.strip(),
                        new_password,
                    )

                if success:

                    st.success(
                        "Registration successful. "
                        "You can now log in."
                    )

                else:

                    st.error(
                        error
                    )


# ============================================================
# STATUS
# ============================================================

def get_status(score):

    if score >= 80:
        return "💀 Strong Match"

    elif score >= 60:
        return "😈 Moderate Match"

    return "🤡 Weak Match"


# ============================================================
# HISTORY API
# ============================================================

def load_history():

    try:

        response = requests.get(
            HISTORY_API_URL,
            headers=auth_headers(),
            timeout=15,
        )

    except requests.RequestException as exc:

        return None, (
            f"Could not connect to API: {exc}"
        )

    if response.status_code == 401:

        clear_authentication()

        return None, (
            "Your session has expired. "
            "Please log in again."
        )

    if response.status_code != 200:

        return None, (
            f"API Error {response.status_code}: "
            f"{response.text}"
        )

    return response.json(), None


def load_history_detail(run_id):

    try:

        response = requests.get(
            f"{HISTORY_API_URL}/{run_id}",
            headers=auth_headers(),
            timeout=15,
        )

    except requests.RequestException as exc:

        return None, (
            f"Could not connect to API: {exc}"
        )

    if response.status_code == 401:

        clear_authentication()

        return None, (
            "Your session has expired. "
            "Please log in again."
        )

    if response.status_code == 403:

        return None, (
            "You do not have permission "
            "to access this screening run."
        )

    if response.status_code != 200:

        return None, (
            f"API Error {response.status_code}: "
            f"{response.text}"
        )

    return response.json(), None


def delete_history(run_id):

    try:

        response = requests.delete(
            f"{HISTORY_API_URL}/{run_id}",
            headers=auth_headers(),
            timeout=15,
        )

    except requests.RequestException as exc:

        return False, (
            f"Could not connect to API: {exc}"
        )

    if response.status_code == 401:

        clear_authentication()

        return False, (
            "Your session has expired. "
            "Please log in again."
        )

    if response.status_code == 403:

        return False, (
            "You do not have permission "
            "to delete this screening run."
        )

    if response.status_code != 200:

        return False, (
            f"API Error {response.status_code}: "
            f"{response.text}"
        )

    return True, None


# ============================================================
# DISPLAY CANDIDATE
# ============================================================

def display_candidate(result):

    score = result["final_score"]

    st.markdown(
        f"## {result['candidate_name']}"
    )

    st.markdown(
        f"### {get_status(score)} — {score:.1f}%"
    )

    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    st.markdown(
        "### Score Breakdown"
    )

    score_columns = st.columns(3)

    metrics = [
        (
            "Required Skills",
            result.get(
                "skill_score",
                0,
            ),
        ),
        (
            "Preferred Skills",
            result.get(
                "preferred_skill_score",
                0,
            ),
        ),
        (
            "Experience",
            result.get(
                "experience_score",
                0,
            ),
        ),
        (
            "Education",
            result.get(
                "education_score",
                0,
            ),
        ),
        (
            "Seniority",
            result.get(
                "seniority_score",
                0,
            ),
        ),
        (
            "Semantic Match",
            result.get(
                "semantic_score",
                0,
            ),
        ),
    ]

    for index, (label, value) in enumerate(
        metrics
    ):

        with score_columns[
            index % 3
        ]:

            st.metric(
                label,
                f"{value:.1f}%",
            )

            st.progress(
                min(
                    max(
                        value / 100,
                        0.0,
                    ),
                    1.0,
                )
            )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    st.markdown(
        "### Skills"
    )

    matched = result.get(
        "matched_skills",
        [],
    )

    missing = result.get(
        "missing_skills",
        [],
    )

    skill_col1, skill_col2 = st.columns(2)

    with skill_col1:

        st.markdown(
            "**Matched Required Skills**"
        )

        if matched:

            for skill in matched:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.info(
                "No required skills matched."
            )

    with skill_col2:

        st.markdown(
            "**Missing Required Skills**"
        )

        if missing:

            for skill in missing:

                st.error(
                    f"✗ {skill}"
                )

        else:

            st.success(
                "All required skills matched."
            )

    # --------------------------------------------------------
    # SENIORITY
    # --------------------------------------------------------

    st.markdown(
        "### Seniority"
    )

    seniority_col1, seniority_col2 = (
        st.columns(2)
    )

    with seniority_col1:

        st.write("Candidate:")

        st.write(
            result.get(
                "candidate_seniority"
            )
            or "Not detected"
        )

    with seniority_col2:

        st.write("Required:")

        st.write(
            result.get(
                "required_seniority"
            )
            or "Not specified"
        )

    # --------------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------------

    explanation = result.get(
        "explanation",
        {},
    )

    st.markdown(
        "### AI-Assisted Explanation"
    )

    summary = explanation.get(
        "summary",
        "",
    )

    if summary:

        st.info(summary)

    strengths = explanation.get(
        "strengths",
        [],
    )

    if strengths:

        st.markdown(
            "**Strengths**"
        )

        for strength in strengths:

            st.success(
                f"✓ {strength}"
            )

    concerns = explanation.get(
        "concerns",
        explanation.get(
            "llm_concerns",
            [],
        ),
    )

    if concerns:

        st.markdown(
            "**Concerns**"
        )

        for concern in concerns:

            st.warning(
                f"• {concern}"
            )


# ============================================================
# NEW SCREENING PAGE
# ============================================================

def render_new_screening():

    st.title(
        "📄 AI Resume Screening & Job Matching"
    )

    st.caption(
        "AI-assisted candidate matching using "
        "Ollama and transparent scoring."
    )

    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    st.header(
        "1. Job Description"
    )

    job_description = st.text_area(
        "Paste the job description",
        height=300,
        placeholder=(
            "Paste the complete job description here..."
        ),
    )

    # --------------------------------------------------------
    # RESUME UPLOAD
    # --------------------------------------------------------

    st.header(
        "2. Upload Resumes"
    )

    uploaded_files = st.file_uploader(
        "Upload candidate resumes",
        type=[
            "pdf",
            "docx",
            "txt",
        ],
        accept_multiple_files=True,
    )

    # --------------------------------------------------------
    # SCREENING
    # --------------------------------------------------------

    screen_button = st.button(
        "🚀 Screen Resumes",
        type="primary",
        use_container_width=True,
    )

    if screen_button:

        if not job_description.strip():

            st.error(
                "Please provide a job description."
            )

            st.stop()

        if not uploaded_files:

            st.error(
                "Please upload at least one resume."
            )

            st.stop()

        files = []

        for uploaded_file in uploaded_files:

            files.append(
                (
                    "resumes",
                    (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    ),
                )
            )

        with st.spinner(
            "Analyzing job description and resumes..."
        ):

            try:

                response = requests.post(
                    SCREEN_API_URL,
                    headers=auth_headers(),
                    data={
                        "job_description": (
                            job_description
                        )
                    },
                    files=files,
                    timeout=600,
                )

            except requests.RequestException as exc:

                st.error(
                    f"Could not connect to API: {exc}"
                )

                st.stop()

        if response.status_code == 401:

            clear_authentication()

            st.error(
                "Your session has expired. "
                "Please log in again."
            )

            st.rerun()

        if response.status_code != 200:

            st.error(
                f"API Error {response.status_code}: "
                f"{response.text}"
            )

            st.stop()

        results = response.json()

        if not results:

            st.warning(
                "No screening results were returned."
            )

            st.stop()

        st.session_state[
            "screening_results"
        ] = results

        st.success(
            "Screening completed successfully."
        )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if (
        st.session_state.get(
            "screening_results"
        ) is None
    ):

        return

    results = st.session_state[
        "screening_results"
    ]

    st.divider()

    st.header(
        "3. Candidate Ranking"
    )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        minimum_score = st.slider(
            "Minimum Match Score",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )

    with col2:

        sort_order = st.selectbox(
            "Sort Candidates",
            [
                "Highest Match",
                "Lowest Match",
                "Candidate Name",
            ],
        )

    filtered_results = [
        result
        for result in results
        if result["final_score"]
        >= minimum_score
    ]

    if sort_order == "Highest Match":

        filtered_results.sort(
            key=lambda x: x["final_score"],
            reverse=True,
        )

    elif sort_order == "Lowest Match":

        filtered_results.sort(
            key=lambda x: x["final_score"]
        )

    else:

        filtered_results.sort(
            key=lambda x: x["candidate_name"]
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_cols = st.columns(4)

    with summary_cols[0]:

        st.metric(
            "Candidates",
            len(filtered_results),
        )

    with summary_cols[1]:

        if filtered_results:

            st.metric(
                "Top Match",
                (
                    f"{filtered_results[0]['final_score']:.1f}%"
                ),
            )

        else:

            st.metric(
                "Top Match",
                "—",
            )

    with summary_cols[2]:

        if filtered_results:

            average = (
                sum(
                    result["final_score"]
                    for result in filtered_results
                )
                / len(filtered_results)
            )

            st.metric(
                "Average Match",
                f"{average:.1f}%",
            )

        else:

            st.metric(
                "Average Match",
                "—",
            )

    with summary_cols[3]:

        strong_count = sum(
            1
            for result in filtered_results
            if result["final_score"] >= 80
        )

        st.metric(
            "80%+ Matches",
            strong_count,
        )

    # --------------------------------------------------------
    # RANKING TABLE
    # --------------------------------------------------------

    st.subheader(
        "Ranking"
    )

    table_data = []

    for index, result in enumerate(
        filtered_results,
        start=1,
    ):

        score = result["final_score"]

        if score >= 80:
            status = "Strong"

        elif score >= 60:
            status = "Moderate"

        else:
            status = "Weak"

        table_data.append(
            {
                "Rank": index,
                "Candidate": (
                    result["candidate_name"]
                ),
                "Match": f"{score:.1f}%",
                "Status": status,
                "Required Skills": (
                    f"{result['skill_score']:.1f}%"
                ),
                "Preferred Skills": (
                    f"{result['preferred_skill_score']:.1f}%"
                ),
                "Experience": (
                    f"{result['experience_score']:.1f}%"
                ),
                "Education": (
                    f"{result['education_score']:.1f}%"
                ),
                "Seniority": (
                    f"{result['seniority_score']:.1f}%"
                ),
                "Semantic": (
                    f"{result['semantic_score']:.1f}%"
                ),
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # CANDIDATE DETAILS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Candidate Details"
    )

    candidate_names = [
        result["candidate_name"]
        for result in filtered_results
    ]

    if candidate_names:

        selected_candidate = st.selectbox(
            "Select candidate",
            candidate_names,
        )

        selected = next(
            result
            for result in filtered_results
            if result["candidate_name"]
            == selected_candidate
        )

        display_candidate(
            selected
        )

    else:

        st.info(
            "No candidates match the selected "
            "minimum score."
        )

    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    st.divider()

    st.caption(
        "This system provides job-relevant "
        "decision support only. It should not "
        "be used as an autonomous hiring or "
        "rejection system."
    )


# ============================================================
# SCREENING HISTORY PAGE
# ============================================================

def render_history():

    st.title(
        "🕘 Screening History"
    )

    st.caption(
        "Previously completed resume screening runs "
        "stored in the database."
    )

    history, error = load_history()

    if error:

        st.error(error)
        return

    if not history:

        st.info(
            "No screening history found yet. "
            "Complete a screening first."
        )

        return

    st.subheader(
        f"Previous Screening Runs ({len(history)})"
    )

    for run in history:

        run_id = run["id"]

        job_title = (
            run.get(
                "job_title",
                "Untitled Job",
            )
            or "Untitled Job"
        )

        candidate_count = run.get(
            "candidate_count",
            0,
        )

        top_score = run.get(
            "top_score",
            0.0,
        )

        average_score = run.get(
            "average_score",
            0.0,
        )

        created_at = run.get(
            "created_at",
            "",
        )

        with st.container(
            border=True
        ):

            col1, col2, col3, col4 = (
                st.columns(
                    [3, 1.5, 1.5, 2]
                )
            )

            with col1:

                st.markdown(
                    f"### {job_title}"
                )

                st.caption(
                    f"Screening Run #{run_id}"
                )

            with col2:

                st.metric(
                    "Candidates",
                    candidate_count,
                )

            with col3:

                st.metric(
                    "Top Match",
                    f"{top_score:.1f}%",
                )

            with col4:

                st.metric(
                    "Average",
                    f"{average_score:.1f}%",
                )

                if created_at:

                    st.caption(
                        created_at.replace(
                            "T",
                            " ",
                        )[:19]
                    )

            action_col1, action_col2 = (
                st.columns(2)
            )

            with action_col1:

                view_key = (
                    f"view_history_{run_id}"
                )

                if st.button(
                    "👁️ View Results",
                    key=view_key,
                    use_container_width=True,
                ):

                    st.session_state[
                        "selected_history_run"
                    ] = run_id

                    st.rerun()

            with action_col2:

                delete_key = (
                    f"delete_history_{run_id}"
                )

                if st.button(
                    "🗑️ Delete",
                    key=delete_key,
                    use_container_width=True,
                ):

                    success, delete_error = (
                        delete_history(run_id)
                    )

                    if success:

                        if (
                            st.session_state.get(
                                "selected_history_run"
                            )
                            == run_id
                        ):

                            st.session_state[
                                "selected_history_run"
                            ] = None

                        st.success(
                            "Screening run deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            delete_error
                        )

    # --------------------------------------------------------
    # SELECTED HISTORICAL RUN
    # --------------------------------------------------------

    selected_run_id = st.session_state.get(
        "selected_history_run"
    )

    if selected_run_id is None:

        return

    st.divider()

    detail, error = load_history_detail(
        selected_run_id
    )

    if error:

        st.error(error)
        return

    if not detail:

        st.warning(
            "The selected screening run could "
            "not be found."
        )

        return

    st.header(
        f"📋 {detail.get('job_title', 'Screening Run')}"
    )

    st.caption(
        f"Screening Run #{detail['id']} • "
        f"{detail.get('candidate_count', 0)} candidates • "
        f"{detail.get('created_at', '').replace('T', ' ')[:19]}"
    )

    historical_results = detail.get(
        "results",
        [],
    )

    if not historical_results:

        st.info(
            "This screening run has no candidate results."
        )

        return

    # --------------------------------------------------------
    # HISTORICAL SUMMARY
    # --------------------------------------------------------

    history_cols = st.columns(4)

    scores = [
        result["final_score"]
        for result in historical_results
    ]

    with history_cols[0]:

        st.metric(
            "Candidates",
            len(historical_results),
        )

    with history_cols[1]:

        st.metric(
            "Top Match",
            f"{max(scores):.1f}%",
        )

    with history_cols[2]:

        st.metric(
            "Average Match",
            f"{sum(scores) / len(scores):.1f}%",
        )

    with history_cols[3]:

        strong_count = sum(
            1
            for score in scores
            if score >= 80
        )

        st.metric(
            "80%+ Matches",
            strong_count,
        )

    # --------------------------------------------------------
    # HISTORICAL RANKING
    # --------------------------------------------------------

    st.subheader(
        "Candidate Ranking"
    )

    historical_table = []

    for index, result in enumerate(
        historical_results,
        start=1,
    ):

        score = result["final_score"]

        if score >= 80:
            status = "Strong"

        elif score >= 60:
            status = "Moderate"

        else:
            status = "Weak"

        historical_table.append(
            {
                "Rank": index,
                "Candidate": (
                    result["candidate_name"]
                ),
                "Match": f"{score:.1f}%",
                "Status": status,
                "Required Skills": (
                    f"{result.get('skill_score', 0):.1f}%"
                ),
                "Preferred Skills": (
                    f"{result.get('preferred_skill_score', 0):.1f}%"
                ),
                "Experience": (
                    f"{result.get('experience_score', 0):.1f}%"
                ),
                "Education": (
                    f"{result.get('education_score', 0):.1f}%"
                ),
                "Seniority": (
                    f"{result.get('seniority_score', 0):.1f}%"
                ),
                "Semantic": (
                    f"{result.get('semantic_score', 0):.1f}%"
                ),
            }
        )

    st.dataframe(
        historical_table,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # HISTORICAL CANDIDATE DETAILS
    # --------------------------------------------------------

    st.subheader(
        "Historical Candidate Details"
    )

    historical_names = [
        result["candidate_name"]
        for result in historical_results
    ]

    selected_historical_name = st.selectbox(
        "Select candidate",
        historical_names,
        key=(
            f"historical_candidate_"
            f"{selected_run_id}"
        ),
    )

    selected_historical = next(
        result
        for result in historical_results
        if result["candidate_name"]
        == selected_historical_name
    )

    display_candidate(
        selected_historical
    )

    st.divider()

    st.caption(
        "Historical results are read from the "
        "screening database. This system provides "
        "job-relevant decision support only and "
        "should not be used as an autonomous hiring "
        "or rejection system."
    )


# ============================================================
# AUTHENTICATED APPLICATION
# ============================================================

def render_authenticated_app():

    current_user = st.session_state.get(
        "current_user"
    ) or {}

    username = current_user.get(
        "username",
        "User",
    )

    role = current_user.get(
        "role",
        "recruiter",
    )

    # ========================================================
    # SIDEBAR
    # ========================================================

    st.sidebar.title(
        "📄 AI Resume Screening"
    )

    st.sidebar.caption(
        "Candidate matching dashboard"
    )

    st.sidebar.success(
        f"Logged in as **{username}**"
    )

    st.sidebar.caption(
        f"Role: **{role}**"
    )

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        clear_authentication()
        st.rerun()

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "🔎 New Screening",
            "🕘 Screening History",
        ],
    )

    st.sidebar.divider()

    st.sidebar.info(
        "AI-assisted screening using Ollama, "
        "semantic matching, and transparent "
        "job-relevant scoring."
    )

    # ========================================================
    # ROUTE PAGE
    # ========================================================

    if page == "🔎 New Screening":

        render_new_screening()

    else:

        render_history()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if not is_authenticated():

    render_authentication()

else:

    if validate_current_session():

        render_authenticated_app()

    else:

        render_authentication()
