import os

import requests
import streamlit as st


API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000",
)


st.set_page_config(
    page_title=(
        "AI Resume Screening"
    ),
    page_icon="📄",
    layout="wide",
)


st.title(
    "📄 AI Resume Screening "
    "& Job Matching"
)

st.caption(
    "Decision-support tool. "
    "Final hiring decisions remain "
    "with human reviewers."
)


job_description = st.text_area(
    "Job Description",
    height=300,
    placeholder=(
        "Paste the complete "
        "job description here..."
    ),
)


resumes = st.file_uploader(
    "Upload Resumes",
    type=[
        "pdf",
        "docx",
        "txt",
    ],
    accept_multiple_files=True,
)


if st.button(
    "Screen Resumes",
    type="primary",
):

    if not job_description.strip():

        st.error(
            "Please enter a "
            "job description."
        )

    elif not resumes:

        st.error(
            "Please upload at "
            "least one resume."
        )

    else:

        multipart_files = [

            (
                "resumes",
                (
                    file.name,
                    file.getvalue(),
                    file.type
                    or "application/octet-stream",
                ),
            )

            for file in resumes
        ]

        try:

            response = requests.post(

                f"{API_URL}/api/screen",

                data={
                    "job_description":
                        job_description
                },

                files=multipart_files,

                timeout=120,
            )

            if response.ok:

                results = (
                    response.json()
                )

                st.success(
                    f"Screened "
                    f"{len(results)} "
                    f"resume(s)."
                )

                for index, result in enumerate(
                    results,
                    start=1,
                ):

                    with st.container(
                        border=True
                    ):

                        col1, col2, col3 = (
                            st.columns(
                                [2, 1, 2]
                            )
                        )

                        col1.subheader(
                            f"#{index} "
                            f"{result['candidate_name']}"
                        )

                        col2.metric(
                            "Match",
                            (
                                f"{result['final_score']:.1f}%"
                            ),
                        )

                        col3.write(
                            "**File:** "
                            f"{result['filename']}"
                        )

                        st.write(
                            "**Skill score:** "
                            f"{result['skill_score']:.1f}%"
                        )

                        st.write(
                            "**Semantic score:** "
                            f"{result['semantic_score']:.1f}%"
                        )

                        st.write(
                            "**Matched:** "
                            + (
                                ", ".join(
                                    result[
                                        "matched_skills"
                                    ]
                                )
                                or "None"
                            )
                        )

                        st.write(
                            "**Missing:** "
                            + (
                                ", ".join(
                                    result[
                                        "missing_skills"
                                    ]
                                )
                                or "None"
                            )
                        )

            else:

                try:

                    detail = (
                        response.json()
                        .get(
                            "detail",
                            response.text,
                        )
                    )

                except Exception:

                    detail = (
                        response.text
                    )

                st.error(
                    f"API error: {detail}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect "
                f"to API: {exc}"
            )
