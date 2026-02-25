import './styles.css';
import { invoke } from '@tauri-apps/api/core';

// Connect to FastAPI backend
const API_URL = 'http://localhost:7861';

let currentMode = 'companion';

// DOM Elements
const chatContainer = document.getElementById('chatContainer') as HTMLElement;
const messageInput = document.getElementById('messageInput') as HTMLInputElement;
const sendBtn = document.getElementById('sendBtn') as HTMLElement;
const typingIndicator = document.getElementById('typingIndicator') as HTMLElement;
const modeButtons = document.querySelectorAll('.mode-btn');

// Mode switching
modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.getAttribute('data-mode') || 'companion';
        console.log('Mode switched to:', currentMode);
    });
});

// NAEYLA Token - Keep this safe!
const NAEYLA_TOKEN = import.meta.env.VITE_NAEYLA_TOKEN || 'default-dev-token';
let backendReady = false;

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function ensureBackendReady() {
    try {
        const ok = await invoke<boolean>('ensure_backend');
        if (!ok) {
            addMessage('Backend is taking longer than expected to start. Please wait a bit and try again.', 'naeyla');
            return false;
        }
    } catch {
        // If Tauri invoke fails (e.g., running in a browser), we still try HTTP health checks.
    }

    for (let attempt = 0; attempt < 12; attempt++) {
        try {
            const response = await fetch(`${API_URL}/health?token=${NAEYLA_TOKEN}`, {
                headers: {
                    'Authorization': `Bearer ${NAEYLA_TOKEN}`
                }
            });
            if (response.ok) {
                backendReady = true;
                return true;
            }
        } catch {
            // ignore and retry
        }
        await sleep(500);
    }

    addMessage('Backend is not responding. Please check that it started successfully.', 'naeyla');
    return false;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    if (!backendReady) {
        const ok = await ensureBackendReady();
        if (!ok) return;
    }

    addMessage(message, 'user');
    messageInput.value = '';
    typingIndicator.classList.remove('hidden');

    try {
        console.log('Sending with Authorization:', `Bearer ${NAEYLA_TOKEN}`);  // DEBUG
        
        const response = await fetch(`${API_URL}/chat?token=${NAEYLA_TOKEN}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${NAEYLA_TOKEN}`
            },
            body: JSON.stringify({
                message: message,
                mode: currentMode
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                addMessage('Auth error. Check that VITE_NAEYLA_TOKEN matches NAEYLA_TOKEN in the backend .env.', 'naeyla');
                typingIndicator.classList.add('hidden');
                return;
            }
            addMessage(`Backend error (${response.status}). Check backend logs.`, 'naeyla');
            typingIndicator.classList.add('hidden');
            return;
        }

        const data = await response.json();
        typingIndicator.classList.add('hidden');
        addMessage(data.response, 'naeyla');

    } catch (error) {
        console.error('Error:', error);
        typingIndicator.classList.add('hidden');
        addMessage('Sorry, I encountered an error. Is the backend running on port 7861?', 'naeyla');
    }
}


// Add message to chat
function addMessage(text: string, sender: 'user' | 'naeyla') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Focus input on load
window.addEventListener('DOMContentLoaded', () => {
    messageInput.focus();
    console.log('Naeyla UI loaded! Make sure backend is running on http://localhost:7861');
    ensureBackendReady();
});
