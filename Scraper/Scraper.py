from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

# ---------------------------
# Setup
# ---------------------------
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://www.umu.se/kalender/")

WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "eventlink"))
)

titles = driver.find_elements(By.CLASS_NAME, "TitleLargeScreen")
links = driver.find_elements(By.CLASS_NAME, "eventlink")
descriptions = driver.find_elements(By.CLASS_NAME, "beskrivning")
days = driver.find_elements(By.CLASS_NAME, "day")
dates = driver.find_elements(By.CLASS_NAME, "date")
months = driver.find_elements(By.CLASS_NAME, "month")
durations = driver.find_elements(By.CLASS_NAME, "duration")
plats_list = driver.find_elements(By.CLASS_NAME, "plats")

print("Fetched first elements")
#Collect event info
events = []
for title, link, description, day, date, month, duration, plats in zip(
    titles, links, descriptions, days, dates, months, durations, plats_list
):
    href = link.get_attribute("href")
    events.append({
        "title": title.text.strip(),
        "href": href.strip(),
        "description": description.text.strip(),
        "day": day.text.strip(),
        "date": date.text.strip(),
        "month": month.text.strip(),
        "duration": duration.text.strip(),
        "plats": plats.text.strip()
    })

#Extract info for each event from the href
for event in events:
    driver.execute_script(f"window.open('{event['href']}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])


    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "p"))
    )


    print("Fetched data for: " + driver.find_element(By.TAG_NAME, "h1").text.strip())

    paragraphs = driver.find_elements(By.TAG_NAME, "p")

# Combine all paragraph texts into one string
    full_text = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
    full_text.replace("901 87 Umeå Tel: 090-786 50 00 Hitta till oss Kontakta oss Press och media Institutioner och enheter Om webbplatsen Tillgänglighet på umu.se Personuppgifter Hantera kakor Facebook Instagram TikTok Youtube LinkedIn Denna webbplats använder kakor (cookies) som lagras i din webbläsare. Vissa kakor är nödvändiga för att sidan ska fungera korrekt och andra är valbara. Du väljer vilka du vill tillåta.", "")

    try:
        event["full_description"] = full_text
    except:
        event["full_description"] = "(no detailed description found)"

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

driver.quit()

# Display results
formatted_events = []

for e in events:
    formatted_events.append({
        "Title": e["title"],
        "Link": e["href"],
        "Date": f"{e['day']} {e['date']} {e['month']}",
        "Duration": e["duration"],
        "Plats": e["plats"],
        "Description": e["description"],
        "Full description": e["full_description"]
    })

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(formatted_events, f, ensure_ascii=False, indent=4)
