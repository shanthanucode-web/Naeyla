import './styles.css';
import { http } from '@tauri-apps/plugin-http';

const API_URL = 'http://localhost:7861';
const NAEYLA_TOKEN = 'naeyla-xs-dev-token-change-in-prod';

let currentMode = 'companion';

const chatContainer = document.getElementById('chatContainer') as HTMLElement;
const messageInput = document.getElementById('messageInput') as HTMLInputElement;
const sendBtn = document.getElementById('sendBtn') as HTMLElement;
const typingIndicator = document.getElementById('typingIndicator') as HTMLElement;
const modeButtons = document.querySelectorAll('.mode-btn');

modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.getAttribute('data-mode') || 'companion';
        console.log('Mode switched to:', currentMode);
    });
});

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    typingIndicator.classList.remove('hidden');

    try {
        const response = await http.post(`${API_URL}/chat?token=${NAEYLA_TOKEN}`, {
            message: message,
            mode: currentMode
        });

        const data = response.data as any;
        typingIndicator.classList.add('hidden');
        addMessage(data.response, 'naeyla');

    } catch (error) {
        console.error('Error:', error);
        typingIndicator.classList.add('hidden');
        addMessage('Sorry, I encountered an error. Is the backend running on port 7861?', 'naeyla');
    }
}

function addMessage(text: string, sender: 'user' | 'naeyla') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    console.log('Naeyla UI loaded! Make sure backend is running on http://localhost:7861');
});
