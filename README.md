# WhatsApp Chatbot with Flask & Node.js

A powerful WhatsApp chatbot that processes text messages and documents using the WhatsApp Business API and Groq AI. Available in both Python (Flask) and Node.js implementations.

## 🌟 Features

- 💬 Real-time text message processing
- 📄 Document analysis (PDF, DOC, DOCX, TXT)
- 🤖 AI-powered responses using Groq
- 🌐 Multi-language support
- ⚡ Fast response times
- 🔒 Secure webhook handling

## 🛠️ Tech Stack

- Backend: Node.js/Express or Python/Flask
- AI: Groq API
- Document Processing: pdf-parse, mammoth (Node.js) or PyPDF2, python-docx (Python)
- Deployment: Vercel

## 📋 Requirements

- Node.js ≥18.0.0 or Python ≥3.9
- WhatsApp Business API access
- Groq API key
- Meta Developer Account

## 🔑 Environment Variables

```env
WHATSAPP_TOKEN=your_whatsapp_token
PHONE_NUMBER_ID=your_phone_number_id
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=compound-beta
```

## 🚀 Quick Start

### Node.js Version

1. Clone the repository:
```bash
git clone https://github.com/Raufjatoi/WP_Chatbot.git
cd wp-chatbot
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file with your credentials

4. Run locally:
```bash
npm start
```

### Python Version

1. Clone the repository:
```bash
git clone https://github.com/Raufjatoi/WP_Chatbot.git
cd wp-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials

4. Run locally:
```bash
python app.py
```

## 📦 Deployment

### Vercel Deployment

1. Push your code to GitHub
2. Import your repository to Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy!

### Manual Deployment

1. Set up your server (Node.js ≥18.0.0 or Python ≥3.9)
2. Clone the repository
3. Install dependencies
4. Set up environment variables
5. Run with PM2 or similar process manager

## 📄 Supported File Types

- PDF files (`.pdf`)
- Word documents (`.doc`, `.docx`)
- Text files (`.txt`)

## 🔧 Webhook Configuration

1. Set your webhook URL in Meta Developer Portal:
   ```
   https://your-domain.com/webhook
   ```
2. Set verification token: `raufbot123`
3. Subscribe to messages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

[Abdul Rauf Jatoi](https://rauf-psi.vercel.app/)

## 🙏 Acknowledgments

- WhatsApp Business API Team
- Groq AI Team
- All contributors


