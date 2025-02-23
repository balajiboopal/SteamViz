import sqlite3


def create_database():
    conn = sqlite3.connect("data/steam_apps.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS apps (
        appid TEXT PRIMARY KEY,
        name TEXT,
        type TEXT,
        required_age INTEGER,
        is_free BOOLEAN,
        short_description TEXT,
        capsule_image TEXT,
        developers TEXT,
        publishers TEXT,
        release_date TEXT,
        platforms TEXT,
        metacritic_score INTEGER,
        categories TEXT,
        genres TEXT,
        price TEXT,
        movies TEXT
    )
    """
    )
    conn.commit()
    conn.close()
    print("Database created and ready to use!")


if __name__ == "__main__":
    create_database()
