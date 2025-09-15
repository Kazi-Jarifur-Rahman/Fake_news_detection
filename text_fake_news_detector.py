import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Get API keys
api_key = os.getenv("GEMINI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cx = os.getenv("GOOGLE_CX")

if not api_key:
    raise ValueError("Gemini API key not found. Please add it in the .env file.")
if not google_api_key or not google_cx:
    raise ValueError("Google API Key or CX not found. Please add them in the .env file.")

# Set API Key for Gemini
os.environ["GEMINI_API_KEY"] = api_key
genai.configure(api_key=api_key)

# Instantiate Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={google_cx}"
    response = requests.get(url)

    if response.status_code == 200:
        search_results = response.json()
        return search_results.get("items", [])
    else:
        return []

def is_wikipedia_url(url):
    parsed = urlparse(url)
    return "wikipedia.org" in parsed.netloc and "/wiki/" in parsed.path

def get_wikipedia_summary(url):
    try:
        # Extract page title from URL
        title = url.split("/wiki/")[-1]
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        headers = {
            "User-Agent": "FactCheckBot/1.0 (https://example.com)"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "⚠️ No summary found.")
        else:
            return f"⚠️ Wikipedia API error. Status code: {response.status_code}"
    except Exception as e:
        return f"⚠️ Error accessing Wikipedia summary: {str(e)[:200]}"

def is_trusted_source(url):
    trusted_domains = ['wikipedia.org', 'bbc.com', 'nytimes.com', 'timesofindia.indiatimes.com', 'espn.com']
    domain = urlparse(url).netloc
    return any(domain in url for domain in trusted_domains)

def extract_snippet_from_search_results(results):
    for result in results:
        snippet = result.get("snippet", "")
        url = result.get("link", "")
        if is_trusted_source(url):
            return snippet, url
    return None, None

def extract_text_from_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"⚠️ HTTP error {response.status_code} while accessing the URL."

        soup = BeautifulSoup(response.text, 'html.parser')

        # DEBUG
        print(f"🔍 Page HTML length: {len(response.text)}")

        content_div = soup.find('div', class_='mw-parser-output')
        if not content_div:
            print("⚠️ Couldn't find 'mw-parser-output' div.")
            paragraphs = soup.find_all('p')
        else:
            paragraphs = content_div.find_all(['p', 'ul', 'ol', 'li'])

        print(f"🧾 Found {len(paragraphs)} content blocks inside 'mw-parser-output'.")
        text = ' '.join([tag.get_text(strip=True) for tag in paragraphs if tag.get_text(strip=True)])

        print(f"📝 Extracted text length: {len(text)}")
        if not text:
            return "⚠️ No textual content found on the page."

        return text.strip()[:8000]

    except Exception as e:
        return f"⚠️ Error extracting content from URL: {str(e)[:200]}"

def format_simple_result(text):
    return f"✅ Fact-Check Result:\n\n{text}\n"

def fact_check_input(input_text: str) -> str:
    if input_text.startswith("http://") or input_text.startswith("https://"):
        print("🌐 URL detected. Extracting content...")
        if is_wikipedia_url(input_text):
            extracted = get_wikipedia_summary(input_text)
        else:
            extracted = extract_text_from_url(input_text)
        prompt = f"""
Analyze the following webpage content and determine if it is factually accurate and unbiased.

Summarize major claims, then assess their truthfulness.

Webpage Content:
\"\"\"
{extracted}
\"\"\"
"""
    else:
        print("🧠 Claim detected. Fact-checking statement...")
        prompt = f"""
You are a highly factual AI.

Evaluate the following claim for truthfulness. Respond in this format:

Truth: "True" or "False"
Explanation: Short reason why.

Claim: "{input_text}"
"""

    response = model.generate_content(prompt)

    if "I am not certain" in response.text or "uncertain" in response.text:
        print("💡 Searching for the most recent information...")
        search_results = google_search(input_text)

        if search_results:
            snippet, source_url = extract_snippet_from_search_results(search_results)
            if snippet:
                return f"⚡ Found recent info from a trusted source:\n\n{snippet}\n\nDetails: {source_url}"
            else:
                return "⚠️ No trusted source found in recent search results."
        else:
            return "⚠️ Unable to search for real-time data."

    return format_simple_result(response.text.strip())

# Running the interactive loop
"""
while True:
    user_input = input("\n📝 Enter a claim or URL to fact-check (or type 'exit' to quit):\n> ")
    if user_input.lower() in ["exit", "quit"]:
        break

    result = fact_check_input(user_input)
    print("\n" + result)
"""