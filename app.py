from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ডেটাবেস ফাইল পাথ (Render-এ রিড-ওনলি হতে পারে, তাই মেমোরিতে রাখলাম)
# SQLite এর বদলে আমরা ডিকশনারি ব্যবহার করছি (সিম্পল ক্যাশ)

cache = {}

def get_contact_info(number):
    try:
        url = f"https://www.truecaller.com/search/{number}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name_tag = soup.find("h1", class_="name")
        name = name_tag.text.strip() if name_tag else "Unknown"
        
        img_tag = soup.find("img", class_="profile-photo")
        photo_url = img_tag['src'] if img_tag else ""
        
        return name, photo_url
    except Exception as e:
        print(f"Scraping error: {e}")
        return number, "https://via.placeholder.com/150"

@app.route('/lookup', methods=['GET'])
def lookup():
    number = request.args.get('number')
    if not number:
        return jsonify({"error": "Number required"}), 400
    
    # ক্যাশ চেক
    if number in cache:
        return jsonify(cache[number])
    
    name, photo = get_contact_info(number)
    data = {"number": number, "name": name, "photo": photo}
    cache[number] = data
    return jsonify(data)

@app.route('/')
def home():
    return "TrueCaller Backend is Running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)