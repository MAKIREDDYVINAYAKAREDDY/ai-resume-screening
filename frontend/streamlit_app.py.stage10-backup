import requests
import streamlit as st


API_URL = "http://localhost:8000/api/screen"


st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
)


st.title("📄 AI Resume Screening & Job Matching")
st.caption(
    "AI-assisted candidate matching using Ollama "
    "and transparent scoring."
)


# --------------------------------------------------
# JOB DESCRIPTION
# --------------------------------------------------

st.header("1. Job Description")

job_description = st.text_area(
    "Paste the job description",
    height=300,
    placeholder=(
        "Paste the complete job description here..."
    ),
)


# --------------------------------------------------
# RESUME UPLOAD
# --------------------------------------------------

st.header("2. Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload candidate resumes",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)


# --------------------------------------------------
# SCREENING
# --------------------------------------------------

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
                API_URL,
                data={
                    "job_description": job_description
                },
                files=files,
                timeout=600,
            )

        except requests.RequestException as exc:

            st.error(
                f"Could not connect to API: {exc}"
            )

            st.stop()

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

    st.session_state["screening_results"] = results


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

if "screening_results" in st.session_state:

    results = st.session_state[
        "screening_results"
    ]

    st.divider()

    st.header("3. Candidate Ranking")

    # ----------------------------------------------
    # FILTER
    # ----------------------------------------------

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

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

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
                f"{filtered_results[0]['final_score']:.1f}%",
            )

        else:

            st.metric(
                "Top Match",
                "—",
            )

    with summary_cols[2]:

        if filtered_results:

            average = sum(
                result["final_score"]
                for result in filtered_results
            ) / len(filtered_results)

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

    # ----------------------------------------------
    # RANKING TABLE
    # ----------------------------------------------

    st.subheader("Ranking")

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
                "Candidate": result[
                    "candidate_name"
                ],
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

    # ----------------------------------------------
    # CANDIDATE DETAILS
    # ----------------------------------------------

    st.divider()

    st.subheader("Candidate Details")

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

        score = selected["final_score"]

        if score >= 80:

            status = "🟢 Strong Match"

        elif score >= 60:

            status = "🟡 Moderate Match"

        else:

            status = "🔴 Weak Match"

        st.markdown(
            f"## {selected['candidate_name']}"
        )

        st.markdown(
            f"### {status} — {score:.1f}%"
        )

        # ------------------------------------------
        # SCORE BREAKDOWN
        # ------------------------------------------

        st.markdown(
            "### Score Breakdown"
        )

        score_columns = st.columns(3)

        metrics = [
            (
                "Required Skills",
                selected["skill_score"],
            ),
            (
                "Preferred Skills",
                selected[
                    "preferred_skill_score"
                ],
            ),
            (
                "Experience",
                selected[
                    "experience_score"
                ],
            ),
            (
                "Education",
                selected[
                    "education_score"
                ],
            ),
            (
                "Seniority",
                selected[
                    "seniority_score"
                ],
            ),
            (
                "Semantic Match",
                selected[
                    "semantic_score"
                ],
            ),
        ]

        for index, (label, value) in enumerate(
            metrics
        ):

            with score_columns[index % 3]:

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

        # ------------------------------------------
        # SKILLS
        # ------------------------------------------

        st.markdown(
            "### Skills"
        )

        matched = selected[
            "matched_skills"
        ]

        missing = selected[
            "missing_skills"
        ]

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

        # ------------------------------------------
        # SENIORITY
        # ------------------------------------------

        st.markdown(
            "### Seniority"
        )

        seniority_col1, seniority_col2 = (
            st.columns(2)
        )

        with seniority_col1:

            st.write(
                "Candidate:"
            )

            st.write(
                selected.get(
                    "candidate_seniority"
                )
                or "Not detected"
            )

        with seniority_col2:

            st.write(
                "Required:"
            )

            st.write(
                selected.get(
                    "required_seniority"
                )
                or "Not specified"
            )

        # ------------------------------------------
        # EXPLANATION
        # ------------------------------------------

        explanation = selected.get(
            "explanation",
            {},
        )

        st.markdown(
            "### AI-Assisted Explanation"
        )

        if explanation.get("summary"):

            st.info(
                explanation["summary"]
            )

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
            "llm_concerns",
            [],
        )

        if concerns:

            st.markdown(
                "**Concerns**"
            )

            for concern in concerns:

                st.warning(
                    f"• {concern}"
                )

        # ------------------------------------------
        # DISCLAIMER
        # ------------------------------------------

        st.divider()

        st.caption(
            "This system provides job-relevant "
            "decision support only. It should not "
            "be used as an autonomous hiring or "
            "rejection system."
        )
