from app.ml.embedding_matcher import semantic_similarity


def main():

    resume = """
    Machine Learning Engineer with four years of experience
    developing predictive models using Python, Scikit-learn,
    TensorFlow, Pandas and NumPy.
    """

    job = """
    We are looking for an engineer with experience building
    and deploying machine learning and deep learning models
    using Python and modern ML frameworks.
    """

    score = semantic_similarity(
        resume,
        job,
    )

    print("=" * 60)
    print("SEMANTIC EMBEDDING TEST")
    print("=" * 60)

    print(
        f"Semantic similarity: {score:.2f}%"
    )


if __name__ == "__main__":
    main()
