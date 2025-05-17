import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import base64

# === SETTINGS ===
GITHUB_TOKEN = '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'
REPO = 'YORI212/yt-downloader'
FILE_PATH = 'cookies.txt'
BRANCH = 'main'

# === Step 1: Extract YouTube cookies ===
def extract_youtube_cookies():
    chrome_driver_path = r"C:\real\chromedriver.exe"  # ✅ Make sure this path is valid
    user_data_dir = r"C:\Users\Acer\AppData\Local\Google\Chrome for Testing"
    profile_dir = "Default"

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"profile-directory={profile_dir}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless=new")  # ✅ Run Chrome invisibly

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Go to YouTube to ensure cookies are loaded
    driver.get("https://www.youtube.com")
    time.sleep(5)  # Let the page and cookies fully load

    # Extract cookies and save in Netscape format
    cookies = driver.get_cookies()
    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie["domain"]
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = cookie["path"]
            secure = "TRUE" if cookie.get("secure") else "FALSE"
            expiry = str(cookie.get("expiry", int(time.time()) + 3600))
            name = cookie["name"]
            value = cookie["value"]
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

    print("✅ Cookies saved to cookies.txt")
    driver.quit()

# === Step 2: Update GitHub file ===
def update_github():
    # Read cookies.txt and base64 encode it
    with open(FILE_PATH, "rb") as f:
        content = f.read()
        b64_content = base64.b64encode(content).decode()

    # Get the current file SHA (required for update)
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha")

    # Upload the new file
    data = {
        "message": "Auto update cookies.txt",
        "content": b64_content,
        "branch": BRANCH,
        "sha": sha  # If creating a new file, remove this line
    }

    r = requests.put(url, headers=headers, json=data)

    if r.status_code in [200, 201]:
        print("✅ cookies.txt updated on GitHub.")
    else:
        print("❌ Failed to update:", r.json())

# === Main ===
if __name__ == "__main__":
    extract_youtube_cookies()
    update_github()
