const express = require('express');
const axios = require('axios');
const multer = require('multer');
const fs = require('fs');
const pdf = require('pdf-parse');
const mammoth = require('mammoth');

const app = express();
app.use(express.json());

const WHATSAPP_TOKEN = process.env.WHATSAPP_TOKEN;
const PHONE_NUMBER_ID = process.env.PHONE_NUMBER_ID;
const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_MODEL = process.env.GROQ_MODEL || 'compound-beta';

// Webhook verification
app.get('/webhook', (req, res) => {
    if (
        req.query['hub.mode'] === 'subscribe' &&
        req.query['hub.verify_token'] === 'raufbot123'
    ) {
        res.send(req.query['hub.challenge']);
    } else {
        res.sendStatus(403);
    }
});

// Handle incoming messages
app.post('/webhook', async (req, res) => {
    try {
        const data = req.body;
        const message = data.entry[0].changes[0].value.messages[0];
        const from = message.from;

        if (message.text) {
            // Handle text messages
            const userText = message.text.body;
            const reply = await askGroq(userText);
            await sendWhatsAppMessage(from, reply);
        } 
        else if (message.document) {
            // Handle documents
            const docId = message.document.id;
            const docName = message.document.filename;
            
            try {
                const fileContent = await downloadWhatsAppFile(docId);
                const fileText = await extractFileText(fileContent, docName);
                
                if (!fileText.trim()) {
                    await sendWhatsAppMessage(from, "The document appears to be empty or unreadable.");
                    return res.sendStatus(200);
                }

                const prompt = `Please analyze this document and provide a summary:\n\n${fileText.substring(0, 4000)}`;
                const reply = await askGroq(prompt);
                await sendWhatsAppMessage(from, reply);
            } catch (error) {
                console.error('Document processing error:', error);
                await sendWhatsAppMessage(from, "Sorry, I couldn't process this document. Please try again.");
            }
        }

        res.sendStatus(200);
    } catch (error) {
        console.error('Webhook error:', error);
        res.sendStatus(500);
    }
});

// Groq API integration
async function askGroq(prompt) {
    try {
        const response = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
            messages: [
                { role: "system", content: "You're a multilingual helpful assistant." },
                { role: "user", content: prompt }
            ],
            model: GROQ_MODEL
        }, {
            headers: {
                'Authorization': `Bearer ${GROQ_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.choices[0].message.content;
    } catch (error) {
        console.error('Groq API error:', error);
        return "Sorry, I encountered an error. Please try again.";
    }
}

// Send WhatsApp message
async function sendWhatsAppMessage(to, message) {
    try {
        await axios.post(
            `https://graph.facebook.com/v17.0/${PHONE_NUMBER_ID}/messages`,
            {
                messaging_product: "whatsapp",
                to: to,
                type: "text",
                text: { body: message }
            },
            {
                headers: {
                    'Authorization': `Bearer ${WHATSAPP_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            }
        );
    } catch (error) {
        console.error('WhatsApp API error:', error);
    }
}

// Download WhatsApp file
async function downloadWhatsAppFile(fileId) {
    const response = await axios.get(
        `https://graph.facebook.com/v17.0/${fileId}`,
        {
            headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` }
        }
    );

    const fileUrl = response.data.url;
    const fileResponse = await axios.get(fileUrl, {
        headers: { 'Authorization': `Bearer ${WHATSAPP_TOKEN}` },
        responseType: 'arraybuffer'
    });

    return fileResponse.data;
}

// Extract text from files
async function extractFileText(fileContent, filename) {
    const tempPath = `temp_${filename}`;
    fs.writeFileSync(tempPath, fileContent);

    try {
        if (filename.toLowerCase().endsWith('.txt')) {
            return fs.readFileSync(tempPath, 'utf-8');
        }
        else if (filename.toLowerCase().endsWith('.pdf')) {
            const data = await pdf(fileContent);
            return data.text;
        }
        else if (filename.toLowerCase().endsWith('.docx')) {
            const result = await mammoth.extractRawText({ path: tempPath });
            return result.value;
        }
        throw new Error('Unsupported file format');
    } finally {
        if (fs.existsSync(tempPath)) {
            fs.unlinkSync(tempPath);
        }
    }
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

module.exports = app;