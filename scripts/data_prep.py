import datetime
import json
import time
import csv
from collections import defaultdict
import os


def parse_release_date(date_str):
    """Convert various date formats to datetime object"""
    try:
        # Try different date formats
        for fmt in ["%Y-%m-%d", "%b %d, %Y", "%d %b, %Y"]:
            try:
                date = datetime.datetime.strptime(date_str, fmt)
                # If date is before 2015, return May 1st, 2015
                if date.year < 2015:
                    return datetime.datetime(2015, 5, 1)
                return date
            except ValueError:
                continue
        # If no format matches, return default date
        return datetime.datetime(2015, 5, 1)
    except:
        return datetime.datetime(2015, 5, 1)


def extract_monthly_data(json_data, release_date):
    price_data = defaultdict(lambda: {"final_price": None})
    player_data = defaultdict(lambda: {"avg_players": 0, "max_players": 0})
    review_data = defaultdict(
        lambda: {
            "avg_positive": 0,
            "avg_negative": 0,
            "total_positive": 0,
            "total_negative": 0,
        }
    )
    last_known_price = None
    for entry in json_data:
        if entry["series"][0]["name"] == "Final price":
            for price_entry in entry["series"][0]["data"]:
                month_year = time.strftime(
                    "%b-%y", time.localtime(price_entry["x"] / 1000)
                )
                current_price = round(price_entry["y"], 2)
                if current_price is None:
                    price_data[month_year]["final_price"] = last_known_price
                else:
                    price_data[month_year]["final_price"] = current_price
                    if current_price > 0:
                        last_known_price = current_price

        elif entry["series"][0]["name"] == "Players":
            for player_entry in entry["series"][2]["data"]:
                if player_entry[1] is not None:
                    month_year = time.strftime(
                        "%b-%y", time.localtime(player_entry[0] / 1000)
                    )
                    player_data[month_year]["total_players"] = (
                        player_data[month_year].get("total_players", 0)
                        + player_entry[1]
                    )
                    player_data[month_year]["count"] = (
                        player_data[month_year].get("count", 0) + 1
                    )
                    player_data[month_year]["max_players"] = max(
                        player_data[month_year]["max_players"], player_entry[1]
                    )

            for month, data in player_data.items():
                if data["count"] > 0:
                    data["avg_players"] = round(
                        data["total_players"] / data["count"], 2
                    )

        elif entry["series"][0]["name"] == "Positive reviews":
            start_date = parse_release_date(release_date)
            for i, (pos, neg) in enumerate(
                zip(entry["series"][0]["data"], entry["series"][1]["data"])
            ):
                if pos is not None and neg is not None:
                    current_date = start_date + datetime.timedelta(days=i)
                    month_year = current_date.strftime("%b-%y")
                    review_data[month_year]["total_positive"] += pos
                    review_data[month_year]["total_negative"] += abs(neg)
                    review_data[month_year]["count"] = (
                        review_data[month_year].get("count", 0) + 1
                    )

    # Calculate review averages
    for month, data in review_data.items():
        if data["count"] > 0:
            data["avg_positive"] = round(data["total_positive"] / data["count"], 2)
            data["avg_negative"] = round(data["total_negative"] / data["count"], 2)

    return price_data, player_data, review_data


def add_to_csv(price_data, player_data, review_data, output_file, appid):
    headers = [
        "appid",
        "Month-Year",
        "Avg players (month)",
        "Max players (month)",
        "Price",
        "Positive Reviews",
        "Negative reviews",
        "Avg Positive reviews",
        "Avg Negative reviews",
    ]

    with open(output_file, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)

        all_months = sorted(
            set(price_data.keys()) | set(player_data.keys()) | set(review_data.keys()),
            key=lambda x: time.strptime(x, "%b-%y"),
        )

        last_known_price = None
        for month in all_months:
            tableau_date = (
                datetime.datetime.strptime(month, "%b-%y")
                .replace(day=1)
                .strftime("%Y-%m-%d")
            )

            current_price = price_data[month]["final_price"]
            if current_price is None:
                price_to_use = last_known_price
            else:
                price_to_use = current_price
                if current_price > 0:
                    last_known_price = current_price
            if price_to_use is None:
                continue

            row = {
                "appid": appid,
                "Month-Year": tableau_date,
                "Avg players (month)": player_data[month]["avg_players"],
                "Max players (month)": player_data[month]["max_players"],
                "Price": price_to_use,
                "Positive Reviews": review_data[month]["total_positive"],
                "Negative reviews": review_data[month]["total_negative"],
                "Avg Positive reviews": review_data[month]["avg_positive"],
                "Avg Negative reviews": review_data[month]["avg_negative"],
            }
            writer.writerow(row)


def main():
    input_dir = r"data/apps"
    output_file = r"temp/steam_data.csv"

    # Read release dates from CSV
    release_dates = {}
    with open("data/steam_games.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            release_dates[row["appid"]] = row["release_date"]

    headers = [
        "appid",
        "Month-Year",
        "Avg players (month)",
        "Max players (month)",
        "Price",
        "Positive Reviews",
        "Negative reviews",
        "Avg Positive reviews",
        "Avg Negative reviews",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            json_file_path = os.path.join(input_dir, filename)
            appid = filename.split(".")[0]

            try:
                with open(json_file_path, "r") as file:
                    json_data = json.load(file)
                release_date = release_dates.get(appid, "2015-05-13")

                price_data, player_data, review_data = extract_monthly_data(
                    json_data, release_date
                )
                add_to_csv(price_data, player_data, review_data, output_file, appid)
                print(f"{filename} - Completed")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    print(f"All data has been added to {output_file}!")


if __name__ == "__main__":
    main()
