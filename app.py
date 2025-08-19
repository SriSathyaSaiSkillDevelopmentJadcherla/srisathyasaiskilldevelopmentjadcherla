import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure the Gemini AI model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

PAGES = {
    "home": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/index.html",
    "about": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/about.html",
    "programs": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/programs.html",
    "gallery": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/gallery.html",
    "join": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/join.html",
    "contact": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/contact.html",
    "register": "https://srisathyasaiskilldevelopmentjadcherla.github.io/Website/register.html"
}

@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        user_message = request.json['message'].lower()
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # --- MODIFIED: Smarter page selection logic ---
        page_to_fetch = "home" # Default to home page
        
        # Find all keywords mentioned in the user's message
        mentioned_keywords = [keyword for keyword in PAGES if keyword in user_message]
        
        if mentioned_keywords:
            # If keywords were found, pick the longest one as the most specific topic
            page_to_fetch = max(mentioned_keywords, key=len)
        # --- END OF MODIFICATION ---

        url_to_fetch = PAGES.get(page_to_fetch)
        print(f"User mentioned '{page_to_fetch}', fetching content from: {url_to_fetch}")
        page_context = get_text_from_url(url_to_fetch)

        if not page_context:
             return jsonify({'reply': "Sorry, I couldn't access the required information to answer that."})

        prompt = f"""
        You are a helpful and friendly AI assistant for the "Sri Sathya Sai Skill Development Centre" website.
        Your name is "chat bot".
        Answer the user's question based ONLY on the following context I've scraped from the '{page_to_fetch}' page.
        If the information is not in the context, say that you can only answer based on the provided page content.
        You MUST be able to respond in both English and Telugu.

        CONTEXT FROM {page_to_fetch.upper()} PAGE:
        ---
        {page_context}
        ---

        USER'S QUESTION:
        "{user_message}"
        """

        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        
        return jsonify({'reply': response.text})

    except Exception as e:
        print(f"An error occurred in /chat: {e}")
        return jsonify({'error': 'Failed to get response from AI'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)