import requests
import pandas as pd
import io

url = "https://docs.google.com/spreadsheets/d/1J3YOR97ZIKYPC0VVN9BOtAkL6Qxe9CIidAet2Q2sxlQ/edit?gid=0#gid=0"
base_url = url.split("/edit")[0]
gid = "0"

# New format
export_url = f"{base_url}/gviz/tq?tqx=out:csv&gid={gid}"
print(f"Testing URL: {export_url}")

# Test with User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
try:
    response = requests.get(export_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Downloading first few bytes...")
        print(response.text[:200])
    else:
        print("Failed.")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
