import requests
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === SETTINGS ===
GITHUB_TOKEN = "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"  # Replace with your actual token (or set as env var)
REPO = "YORI212/yt-downloader"           # Your GitHub repo in user/repo format
FILE_PATH = "cookies.txt"                 # File to update in the repo
BRANCH = "main"                          # Branch name

def extract_youtube_cookies():
    chrome_driver_path = "/usr/bin/chromedriver"  # Change path if needed
    user_data_dir = "/tmp/chrome-user-data"       # temp dir for user data (headless)
    profile_dir = "Default"

    options = Options()
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(f"profile-directory={profile_dir}")
    options.add_argument("--headless=new")        # Run headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.youtube.com")
    time.sleep(5)  # Wait for full load & cookies

    cookies = driver.get_cookies()
    driver.quit()

    # Write cookies in Netscape format
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in cookies:
            domain = c["domain"]
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = c["path"]
            secure = "TRUE" if c.get("secure") else "FALSE"
            expiry = str(c.get("expiry", int(time.time()) + 3600))
            name = c["name"]
            value = c["value"]
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

    print("✅ Cookies saved to cookies.txt")

def update_github_file():
    with open(FILE_PATH, "rb") as f:
        content = f.read()
        b64_content = base64.b64encode(content).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get current file SHA
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"❌ Failed to get file info: {r.json()}")
        return False

    sha = r.json().get("sha")

    data = {
        "message": "Auto update cookies.txt",
        "content": b64_content,
        "branch": BRANCH,
        "sha": sha
    }

    r = requests.put(url, headers=headers, json=data)
    if r.status_code in [200, 201]:
        print("✅ cookies.txt updated on GitHub.")
        return True
    else:
        print(f"❌ Failed to update file: {r.json()}")
        return False

if __name__ == "__main__":
    extract_youtube_cookies()
    update_github_file()
