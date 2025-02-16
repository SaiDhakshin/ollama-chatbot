require('dotenv').config();
const express = require('express');
const cors = require('cors');
const g4f = require("g4f");
const axios = require("axios");
const { OpenAI } = require('openai');

const app = express();
app.use(express.json());
app.use(cors({
    origin: 'http://localhost:5173', // Allow only your Vue app
    methods: ['GET', 'POST'],        // Specify allowed methods
    allowedHeaders: ['Content-Type'] // Allow content type header
}));

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.post('/chat', async (req, res) => {
    try {
        const { message } = req.body;
        
        const response = await axios.post("http://localhost:11434/api/generate", {
            model: "llama3.2", // Change this if using another model
            prompt: message,
            stream: false
        });
        
        res.json({ reply: response.data.response });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Something went wrong!' });
    }
});

app.listen(5001, () => console.log('Server running on port 5001'));