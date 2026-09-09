import sqlite3
from pathlib import Path


DB_PATH = Path("resume_screening.db")


NEW_COLUMNS = {
    "screening_run_id": "INTEGER",
    "preferred_skill_score": "REAL DEFAULT 0.0",
    "seniority_score": "REAL DEFAULT 0.0",
    "resume_skills": "TEXT DEFAULT ''",
    "job_required_skills": "TEXT DEFAULT ''",
    "job_preferred_skills": "TEXT DEFAULT ''",
    "candidate_seniority": "TEXT",
    "required_seniority": "TEXT",
    "explanation_summary": "TEXT DEFAULT ''",
    "explanation_strengths": "TEXT DEFAULT ''",
    "explanation_concerns": "TEXT DEFAULT ''",
}


def main():
    if not DB_PATH.exists():
        print("Database does not exist.")
        print("It will be created automatically when the API starts.")
        return

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name='screening_results'
            """
        )

        if cursor.fetchone() is None:
            print("screening_results table does not exist yet.")
            return

        cursor.execute("PRAGMA table_info(screening_results)")
        existing_columns = {
            row[1]
            for row in cursor.fetchall()
        }

        for column_name, column_definition in NEW_COLUMNS.items():
            if column_name not in existing_columns:
                print(f"Adding column: {column_name}")
                cursor.execute(
                    f"""
                    ALTER TABLE screening_results
                    ADD COLUMN {column_name} {column_definition}
                    """
                )
            else:
                print(f"Already exists: {column_name}")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS screening_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title VARCHAR(255) NOT NULL DEFAULT 'Untitled Job',
                job_description TEXT NOT NULL DEFAULT '',
                candidate_count INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_screening_runs_created_at
            ON screening_runs(created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            ix_screening_results_screening_run_id
            ON screening_results(screening_run_id)
            """
        )

        connection.commit()

        print()
        print("Stage 7 database migration completed successfully.")

        cursor.execute("PRAGMA table_info(screening_results)")
        columns = [row[1] for row in cursor.fetchall()]

        print()
        print("screening_results columns:")
        for column in columns:
            print(f"  - {column}")

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        )

        print()
        print("Database tables:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
