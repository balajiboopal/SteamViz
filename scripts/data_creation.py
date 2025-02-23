import time
import requests
import sqlite3
import csv


def fetch_steam_data(appid):
    API_URL = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    response = requests.get(API_URL)
    data = response.json()

    if data[str(appid)]["success"]:
        app_data = data[str(appid)]["data"]
        name = app_data.get("name", "")
        type_ = app_data.get("type", "")
        required_age = app_data.get("required_age", 0)
        is_free = app_data.get("is_free", False)
        short_description = app_data.get("short_description", "").capitalize()
        capsule_image = app_data.get("capsule_image", "")
        developers = ", ".join(app_data.get("developers", []))
        publishers = ", ".join(app_data.get("publishers", []))
        release_date = app_data.get("release_date", {}).get("date", "")
        platforms = ", ".join(app_data.get("platforms", {}).keys())
        metacritic_score = app_data.get("metacritic", {}).get("score", "N/A")
        categories = ", ".join(
            [cat["description"] for cat in app_data.get("categories", [])]
        )
        genres = ", ".join(
            [genre["description"] for genre in app_data.get("genres", [])]
        )
        price = app_data.get("price_overview", {}).get("final_formatted", "N/A")

        # Handle movies data more robustly
        if app_data.get("movies"):
            movies = app_data.get("movies")[0].get("webm", {}).get("max", "N/A")
        else:
            movies = "N/A"

        return {
            "appid": str(appid),
            "name": name,
            "type": type_,
            "required_age": required_age,
            "is_free": is_free,
            "short_description": short_description,
            "capsule_image": capsule_image,
            "developers": developers,
            "publishers": publishers,
            "release_date": release_date,
            "platforms": platforms,
            "metacritic_score": metacritic_score,
            "categories": categories,
            "genres": genres,
            "price": price,
            "movies": movies,
        }
    else:
        print(f"Failed to fetch data for appid {appid}")
        return None


# def insert_data_to_db(data):
#     conn = sqlite3.connect("data/steam_apps.db")
#     cursor = conn.cursor()

#     cursor.execute(
#         """
#     INSERT OR REPLACE INTO apps (appid, name, type, required_age, is_free, short_description, capsule_image,
#     developers, publishers, release_date, platforms, metacritic_score, categories, genres, price, movies)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """,
#         (
#             data["appid"],
#             data["name"],
#             data["type"],
#             data["required_age"],
#             data["is_free"],
#             data["short_description"],
#             data["capsule_image"],
#             data["developers"],
#             data["publishers"],
#             data["release_date"],
#             data["platforms"],
#             data["metacritic_score"],
#             data["categories"],
#             data["genres"],
#             data["price"],
#             data["movies"],
#         ),
#     )
#     conn.commit()
#     conn.close()


def save_data_to_csv(data, file_name="data/steam_games.csv"):
    # Define the column headers
    headers = [
        "appid",
        "name",
        "type",
        "required_age",
        "is_free",
        "short_description",
        "capsule_image",
        "developers",
        "publishers",
        "release_date",
        "platforms",
        "metacritic_score",
        "categories",
        "genres",
        "price",
        "movies",
    ]

    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(
            {
                "appid": data["appid"],
                "name": data["name"],
                "type": data["type"],
                "required_age": data["required_age"],
                "is_free": data["is_free"],
                "short_description": data["short_description"],
                "capsule_image": data["capsule_image"],
                "developers": data["developers"],
                "publishers": data["publishers"],
                "release_date": data["release_date"],
                "platforms": data["platforms"],
                "metacritic_score": data["metacritic_score"],
                "categories": data["categories"],
                "genres": data["genres"],
                "price": data["price"],
                "movies": data["movies"],
            }
        )


def get_app_ids():
    response = requests.get("https://steamspy.com/api.php?request=top100forever")
    data = response.json()
    app_ids = list(data.keys())
    print({appid: data[appid]["name"] for appid in app_ids})

    with open("data/steam_games.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_appids = [row["appid"] for row in reader]

    app_ids = list(set(app_ids) - set(existing_appids))
    if len(app_ids) == 0:
        print("No new games to add.")
        exit
    return app_ids


def main():
    app_ids = get_app_ids()
    for appid in app_ids:
        app_data = fetch_steam_data(appid)
        if app_data:
            save_data_to_csv(app_data)
            print(app_data["name"], "ADDED")
            time.sleep(2)


if __name__ == "__main__":
    main()
