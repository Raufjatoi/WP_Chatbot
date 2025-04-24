# app.py
import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = os.environ.get('GROQ_MODEL', 'compound-beta')

# WhatsApp Webhook Verification
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args.get("hub.verify_token") == "raufbot123":
            return request.args["hub.challenge"], 200
    return "Verification failed", 403

# WhatsApp Message Receiver
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = message["from"]
        
        # Handle text messages
        if "text" in message:
            user_text = message["text"]["body"]
            reply_text = ask_groq(user_text)
            send_whatsapp_message(from_number, reply_text)
            
        # Handle document messages
        elif "document" in message:
            print("Document received!")  # Debug log
            doc_id = message["document"]["id"]
            doc_name = message["document"]["filename"]
            print(f"Document ID: {doc_id}, Filename: {doc_name}")  # Debug log
            
            try:
                # Download the file
                file_content = download_whatsapp_file(doc_id)
                print("File downloaded successfully")  # Debug log
                
                # Extract text based on file type
                file_text = extract_file_text(file_content, doc_name)
                print(f"Extracted text length: {len(file_text)}")  # Debug log
                
                if not file_text.strip():
                    send_whatsapp_message(from_number, "The document appears to be empty or I couldn't extract its content. Please make sure the file is not password protected and contains readable text.")
                    return "ok", 200
                
                # Process with Groq
                prompt = (
                    "Please analyze the following document and provide a detailed summary of its contents. "
                    "If it's a structured document, describe its main sections and key points.\n\n"
                    f"Document content:\n{file_text[:4000]}"  # Limiting to 4000 chars to avoid token limits
                )
                
                print("Sending to Groq for analysis...")  # Debug log
                reply_text = ask_groq(prompt)
                print(f"Groq response received, length: {len(reply_text)}")  # Debug log
                
                if reply_text:
                    send_whatsapp_message(from_number, reply_text)
                else:
                    send_whatsapp_message(from_number, "Sorry, I couldn't generate a response for this document. Please try again.")
                    
            except Exception as e:
                print(f"Error processing document: {str(e)}")  # Debug log
                send_whatsapp_message(from_number, "Sorry, I encountered an error while processing your document. Please make sure it's a supported format (PDF, DOC, DOCX, or TXT) and try again.")

    except Exception as e:
        print(f"Error in webhook: {str(e)}")  # Debug log
        send_whatsapp_message(from_number, "Sorry, I encountered an error processing your message.")
    return "ok", 200

# Groq API Call
def ask_groq(user_prompt):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {"role": "system", "content": "You're a multilingual helpful assistant."},
                {"role": "user", "content": user_prompt}
            ],
            "model": GROQ_MODEL
        }
        print(f"Sending request to Groq with prompt length: {len(user_prompt)}")  # Debug log
        
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=data, headers=headers)
        
        if not res.ok:
            print(f"Groq API error: {res.status_code} - {res.text}")  # Debug log
            return "Sorry, I encountered an error processing your request. Please try again."
            
        response_json = res.json()
        print(f"Groq API response: {response_json}")  # Debug log
        
        if "choices" not in response_json or not response_json["choices"]:
            print("No choices in Groq response")  # Debug log
            return "Sorry, I received an empty response. Please try again."
            
        return response_json["choices"][0]["message"]["content"]
        
    except Exception as e:
        print(f"Error in ask_groq: {str(e)}")  # Debug log
        return "Sorry, I encountered an error while processing your request. Please try again."

# WhatsApp Send Message
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)

def download_whatsapp_file(file_id):
    # First, get the file URL
    url = f"https://graph.facebook.com/v17.0/{file_id}"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        print(f"Error getting file URL: {response.text}")  # Debug log
        raise Exception("Failed to get file URL")
        
    file_url = response.json()["url"]
    
    # Download the actual file
    response = requests.get(file_url, headers=headers)
    if not response.ok:
        print(f"Error downloading file: {response.text}")  # Debug log
        raise Exception("Failed to download file")
        
    return response.content

def extract_file_text(file_content, filename):
    # Save temporary file
    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    text = ""
    try:
        if filename.lower().endswith('.txt'):
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        elif filename.lower().endswith('.pdf'):
            import PyPDF2
            with open(temp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
        
        elif filename.lower().endswith(('.doc', '.docx')):
            import docx
            doc = docx.Document(temp_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise Exception(f"Unsupported file format: {filename}")
            
    except Exception as e:
        print(f"Error extracting text from {filename}: {str(e)}")  # Debug log
        raise e
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return text

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
