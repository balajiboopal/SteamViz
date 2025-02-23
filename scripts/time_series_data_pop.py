# Script does not work as the website bans data scraping.
# You can however run the javascript code in the browser console to get the data!

import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Path to your Chrome user profile
CHROME_PROFILE_PATH = "C:/Users/vijay/AppData/Local/Google/Chrome/User Data"

# Target URL
TARGET_URL = "https://steamdb.info/app/1245620/charts/"

# JavaScript to extract Highcharts data
SCRIPT = """
function getHighchartsData() {
    var chartData = [];
    if (typeof Highcharts !== "undefined" && Highcharts.charts) {
        Highcharts.charts.forEach(function (chart, index) {
            if (chart && chart.series) {
                chartData.push({
                    chartIndex: index,
                    series: chart.series.map(function (series) {
                        return {
                            name: series.name,
                            data: series.options.data,
                        };
                    }),
                });
            }
        });
    }
    return chartData;
}

console.log(JSON.stringify(getHighchartsData(), null, 2));
"""

# Set up the WebDriver to use your Chrome profile
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
options.add_argument(
    "--profile-directory=Default"
)  # Adjust if you use a different profile
options.add_argument("--headless=new")  # Optional, for running without UI
options.add_argument("--disable-gpu")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the target URL
    driver.get(TARGET_URL)

    # Execute JavaScript to get chart data
    chart_data = driver.execute_script(SCRIPT)

    # Parse and print the data
    parsed_data = json.loads(chart_data)
    print(json.dumps(parsed_data, indent=2))

    # Save data to a file
    with open("chart_data.json", "w") as file:
        json.dump(parsed_data, file, indent=2)

finally:
    # Clean up
    driver.quit()
