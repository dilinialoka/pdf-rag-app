from flask import Flask, request

import requests

app = Flask(__name__)

# Store PDF text globally (simple version)
pdf_text = ""

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>PDF AI Chat</title>
        <style>
            body {
                margin: 0;
                font-family: Arial;
                background: #0f172a;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .chat-container {
                width: 500px;
                height: 650px;
                background: #1e293b;
                border-radius: 15px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            }

            .header {
                padding: 15px;
                background: #38bdf8;
                color: black;
                font-weight: bold;
                text-align: center;
            }

            .content {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
            }

            .message {
                background: #334155;
                padding: 10px;
                border-radius: 10px;
                margin-bottom: 10px;
            }

            .input-box {
                display: flex;
                padding: 10px;
                background: #0f172a;
            }

            input {
                flex: 1;
                padding: 10px;
                border: none;
                border-radius: 8px;
                outline: none;
            }

            button {
                margin-left: 10px;
                padding: 10px 15px;
                border: none;
                background: #38bdf8;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
            }

            button:hover {
                background: #0ea5e9;
            }

            .upload {
                padding: 10px;
                background: #0f172a;
                border-bottom: 1px solid #334155;
            }

            input[type="file"] {
                color: white;
            }
        </style>
    </head>

    <body>
        <div class="chat-container">

            <div class="header">📄 PDF AI Chatbot</div>

            <div class="upload">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file">
                    <button type="submit">Upload</button>
                </form>
            </div>

            <div class="content">
                <div class="message">👋 Upload a PDF and ask questions below!</div>
            </div>

            <div class="input-box">
                <form action="/ask" method="post" style="display:flex; width:100%;">
                    <input type="text" name="question" placeholder="Ask something...">
                    <button type="submit">Send</button>
                </form>
            </div>

        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    global pdf_text
    
    file = request.files['file']
    file.save("uploaded.pdf")

    from pypdf import PdfReader
    reader = PdfReader("uploaded.pdf")

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    pdf_text = text

    return "PDF uploaded successfully!"

import requests

@app.route('/ask', methods=['POST'])
def ask():
    global pdf_text

    question = request.form['question']

    prompt = f"""
You are a helpful assistant.
Answer ONLY using the PDF content below.

PDF:
{pdf_text}

Question:
{question}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    answer = response.json()["response"]

    return f"""
    <html>
    <body style="font-family:Arial; background:#0f172a; color:white; padding:30px;">
        <h2>🤖 Answer</h2>
        <div style="background:#1e293b; padding:20px; border-radius:10px;">
            {answer}
        </div>
        <br>
        <a href="/" style="color:#38bdf8;">⬅ Back</a>
    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(debug=True)