// ===== js/main.js =====
document.addEventListener('DOMContentLoaded', () => {

    // ----- DOM ELEMENTS -----
    const sidebar = document.getElementById('sidebar');
    const hamburger = document.getElementById('hamburgerBtn');
    const newSessionBtn = document.getElementById('newSessionBtn');
    const historyList = document.getElementById('historyList');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const ttsToggle = document.getElementById('ttsToggle');

    // ----- API CONFIGURATION -----
    const API_URL = 'http://127.0.0.1:8000/perguntar';
    const HEALTH_URL = 'http://127.0.0.1:8000/health';
    let apiOnline = false;

    // ----- STATE -----
    let currentSessionId = Date.now().toString(36) + Math.random().toString(36).slice(2,6);
    let sessions = {};          // { sessionId: [ { role, content, sources? }, ... ] }
    let sessionOrder = [];      // list of IDs in order (most recent at the end)
    let ttsEnabled = false;
    let isProcessing = false;   // prevents multiple sends
    let speechSynth = window.speechSynthesis;
    let utterance = null;
    let audioContextVermelho = null;  // Audio context for voice output
    let destinationNode = null;       // MediaStreamDestination node

    // ----- CHECK API HEALTH -----
    async function checkApiHealth() {
        try {
            const response = await fetch(HEALTH_URL, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                apiOnline = true;
                console.log('✅ API online:', data);
                return true;
            } else {
                apiOnline = false;
                console.warn('⚠️ API offline:', response.status);
                return false;
            }
        } catch (error) {
            apiOnline = false;
            console.warn('⚠️ Error connecting to API:', error.message);
            return false;
        }
    }

    // ----- FUNCTION TO ASK A QUESTION TO THE API -----
    async function askQuestion(question) {
        if (!question || question.trim().length < 3) {
            return {
                error: true,
                message: "Please ask a question with at least 3 characters."
            };
        }

        try {
            const payload = {
                pergunta: question.trim(),
                top_k: 3
            };

            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errorMsg = `Error ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMsg = errorData.detail;
                    }
                } catch (e) {
                    errorMsg = `Error ${response.status}: ${response.statusText}`;
                }

                return {
                    error: true,
                    message: errorMsg,
                    status: response.status
                };
            }

            const data = await response.json();

            return {
                error: false,
                question: data.pergunta,
                answer: data.resposta,
                sources: data.fontes || [],
                data: data
            };

        } catch (error) {
            console.error("❌ Request error:", error);
            return {
                error: true,
                message: "Connection error to the server. Please check if the API is running.",
                details: error.message
            };
        }
    }

    // ----- INITIALIZATION: first session -----
    function initFirstSession() {
        sessions[currentSessionId] = [
            { role: 'bot', content: 'Hello! How can I help you today?' }
        ];
        sessionOrder = [currentSessionId];
        renderHistory();
        renderMessages(currentSessionId);

        // Check API health in the background
        checkApiHealth();
    }

    // ----- RENDER: history (sidebar) -----
    function renderHistory() {
        if (sessionOrder.length === 0) {
            historyList.innerHTML = `<li class="history-placeholder">No conversations yet</li>`;
            return;
        }
        let html = '';
        sessionOrder.forEach((id) => {
            const msgs = sessions[id] || [];
            const firstUserMsg = msgs.find(m => m.role === 'user');
            const preview = firstUserMsg ? firstUserMsg.content.slice(0, 40) : 'Empty conversation';
            const isActive = (id === currentSessionId);
            const activeClass = isActive ? 'active-session' : '';
            const label = preview + (preview.length >= 40 ? '…' : '');
            html += `<li class="${activeClass}" data-session-id="${id}">${label}</li>`;
        });
        historyList.innerHTML = html;

        document.querySelectorAll('.history-list li[data-session-id]').forEach(li => {
            li.addEventListener('click', (e) => {
                const id = li.dataset.sessionId;
                if (id && id !== currentSessionId) {
                    switchSession(id);
                }
                if (window.innerWidth <= 720) {
                    sidebar.classList.remove('open');
                }
            });
        });
    }

    // ----- RENDER: messages from the active session -----
    function renderMessages(sessionId) {
        const msgs = sessions[sessionId] || [];
        chatMessages.innerHTML = '';
        msgs.forEach(msg => {
            const div = document.createElement('div');
            div.className = `message ${msg.role}`;
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = msg.role === 'bot' ? '🤖' : '👤';
            const bubble = document.createElement('div');
            bubble.className = 'bubble';

            // Add sources if they exist (only for bot responses)
            if (msg.role === 'bot' && msg.sources && msg.sources.length > 0) {
                bubble.innerHTML = `
                    ${msg.content}
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e0e6f0; font-size: 0.8em; color: #6c7e99;">
                        📚 Sources: ${msg.sources.join(', ')}
                    </div>
                `;
            } else {
                bubble.textContent = msg.content;
            }

            div.appendChild(avatar);
            div.appendChild(bubble);
            chatMessages.appendChild(div);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ----- SWITCH SESSION -----
    function switchSession(sessionId) {
        if (!sessions[sessionId]) return;
        currentSessionId = sessionId;
        renderHistory();
        renderMessages(currentSessionId);
        if (speechSynth.speaking) speechSynth.cancel();
    }

    // ----- CREATE NEW SESSION -----
    function createNewSession() {
        const newId = Date.now().toString(36) + Math.random().toString(36).slice(2,6);
        sessions[newId] = [
            { role: 'bot', content: 'Hello! How can I help you today?' }
        ];
        sessionOrder.push(newId);
        currentSessionId = newId;
        renderHistory();
        renderMessages(currentSessionId);
        if (window.innerWidth <= 720) {
            sidebar.classList.remove('open');
        }
        if (speechSynth.speaking) speechSynth.cancel();
        userInput.value = '';
        typingIndicator.classList.remove('show');
        isProcessing = false;
    }

    // ----- ADD MESSAGE -----
    function addMessage(role, content, sources = null) {
        if (!sessions[currentSessionId]) {
            sessions[currentSessionId] = [];
        }
        const msg = { role, content };
        if (sources) {
            msg.sources = sources;
        }
        sessions[currentSessionId].push(msg);
        renderMessages(currentSessionId);
        renderHistory();
    }

    // ========================================================
    // TEXT-TO-SPEECH IMPLEMENTATION (FROM CANVAS FILE)
    // ========================================================

    /**
     * Initializes the audio context for voice output (TTS)
     * This creates an audio context that can capture the Web Speech API output
     */
    function initTTSAudioContext() {
        if (audioContextVermelho) return;

        try {
            audioContextVermelho = new (window.AudioContext || window.webkitAudioContext)();
            destinationNode = audioContextVermelho.createMediaStreamDestination();
            console.log("🔴 TTS Audio context initialized.");
        } catch (e) {
            console.warn("Could not initialize TTS audio context:", e);
        }
    }

    /**
     * Text-to-Speech function using Web Speech API
     * @param {string} text - The text to be spoken
     */
    function speakText(text) {
        if (!window.speechSynthesis) return;

        // Cancel any ongoing speech
        if (speechSynth.speaking) {
            speechSynth.cancel();
        }

        // Resume audio context if suspended
        if (audioContextVermelho && audioContextVermelho.state === 'suspended') {
            audioContextVermelho.resume();
        }

        // Create the utterance
        utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-EN';
        utterance.rate = 0.98;
        utterance.pitch = 1.1;
        utterance.volume = 1;

        // Try to find a Portuguese voice
        const voices = speechSynth.getVoices();
        let voice = voices.find(v =>
            v.lang.includes('pt-BR') ||
            v.lang.includes('pt_PT') ||
            v.lang.includes('portuguese')
        );

        // If no Portuguese voice, try to find a female voice
        if (!voice) {
            voice = voices.find(v =>
                v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('samantha') ||
                v.name.toLowerCase().includes('maria') ||
                v.name.toLowerCase().includes('zira')
            );
        }

        // Fallback to any available voice
        if (!voice) {
            voice = voices[0] || null;
        }

        if (voice) {
            utterance.voice = voice;
            console.log(`🗣️ Using voice: ${voice.name} (${voice.lang})`);
        }

        // If we have a destination node, route the audio through it
        if (destinationNode) {
            try {
                utterance.outputDevice = destinationNode;
            } catch (e) {
                // Some browsers may not support outputDevice
                // If it fails, speech will still work but won't be routed to our analyzer
            }
        }

        // Speak the text
        speechSynth.speak(utterance);
    }

    /**
     * Initializes voice system (called on first interaction)
     */
    function initializeVoiceSystem() {
        initTTSAudioContext();
        // Pre-load voices
        if (window.speechSynthesis) {
            speechSynth.getVoices();
        }
    }

    // ----- SEND MESSAGE (main flow with API) -----
    async function handleSend() {
        const text = userInput.value.trim();
        if (!text || isProcessing) return;

        // Initialize voice system on first interaction
        initializeVoiceSystem();

        if (!sessions[currentSessionId]) {
            sessions[currentSessionId] = [];
        }

        // Add user message
        addMessage('user', text);
        userInput.value = '';
        isProcessing = true;
        typingIndicator.classList.add('show');

        try {
            // Check if API is online
            if (!apiOnline) {
                const healthCheck = await checkApiHealth();
                if (!healthCheck) {
                    const errorMsg = "⚠️ Server offline. Please check if the API is running at " + API_URL;
                    addMessage('bot', errorMsg);
                    typingIndicator.classList.remove('show');
                    isProcessing = false;
                    return;
                }
            }

            // Make request to the API
            const result = await askQuestion(text);

            if (result.error) {
                // Error in API response
                const errorMsg = `❌ ${result.message}`;
                addMessage('bot', errorMsg);
            } else {
                // Success - add answer with sources
                addMessage('bot', result.answer, result.sources);

                // Text-to-speech (if enabled)
                if (ttsEnabled) {
                    speakText(result.answer);
                }
            }

        } catch (error) {
            console.error('❌ Unexpected error:', error);
            addMessage('bot', '❌ An unexpected error occurred. Please try again.');
        }

        typingIndicator.classList.remove('show');
        isProcessing = false;
    }

    // ----- EVENT LISTENERS -----
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    newSessionBtn.addEventListener('click', createNewSession);

    // Toggle TTS
    ttsToggle.addEventListener('click', () => {
        // Initialize voice system when user clicks TTS toggle
        initializeVoiceSystem();

        ttsEnabled = !ttsEnabled;
        ttsToggle.classList.toggle('active', ttsEnabled);
        if (ttsEnabled) {
            const msgs = sessions[currentSessionId] || [];
            const lastBotMsg = [...msgs].reverse().find(m => m.role === 'bot');
            if (lastBotMsg) {
                speakText(lastBotMsg.content);
            }
        } else {
            if (speechSynth.speaking) speechSynth.cancel();
        }
    });

    // Hamburger (mobile)
    hamburger.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 720) {
            const isSidebar = sidebar.contains(e.target);
            const isHamburger = hamburger.contains(e.target);
            if (!isSidebar && !isHamburger && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        }
    });

    // Initialize voices on page load
    if (window.speechSynthesis) {
        speechSynth.getVoices();
        speechSynth.onvoiceschanged = () => {
            speechSynth.getVoices();
        };
    }

    // Check API periodically (every 30 seconds)
    setInterval(checkApiHealth, 30000);

    // Initialize the first session
    initFirstSession();

    // Extra: error handling to prevent multiple sends
    window.addEventListener('beforeunload', () => {
        if (speechSynth.speaking) speechSynth.cancel();
    });
});
