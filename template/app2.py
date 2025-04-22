from flask import Flask, request, jsonify, render_template
import trafilatura
import re

app = Flask(__name__)
stored_content = []

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_url(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return clean_text(trafilatura.extract(downloaded))
    return ""

def find_best_match(question, documents):
    question_words = set(re.findall(r'\w+', question.lower()))
    best_score, best_sentence = 0, ""
    for doc in documents:
        for sentence in re.split(r'(?<=[.!?])\s+', doc):
            score = sum(1 for word in question_words if word in sentence.lower())
            if score > best_score:
                best_score, best_sentence = score, sentence
    return best_sentence or "No relevant information found."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest():
    urls = request.json.get('urls', [])
    for url in urls:
        text = extract_text_from_url(url)
        if text:
            stored_content.append(text)
    return jsonify({"message": "URLs processed successfully!"})

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    answer = find_best_match(question, stored_content)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
