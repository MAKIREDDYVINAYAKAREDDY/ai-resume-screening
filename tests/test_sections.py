from app.resume.section_parser import parse_sections


def test_section_parser():

    resume = """
    JOHN DOE

    SUMMARY

    Machine Learning Engineer with 4 years of experience.

    SKILLS

    Python
    SQL
    PyTorch

    EXPERIENCE

    Machine Learning Engineer
    ABC Technologies

    EDUCATION

    B.Tech Computer Science

    PROJECTS

    Resume Screening System
    """

    sections = parse_sections(resume)

    assert "summary" in sections
    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "projects" in sections

    assert "Python" in sections["skills"]