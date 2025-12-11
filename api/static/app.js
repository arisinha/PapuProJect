/**
 * AI Agent Chat Interface
 * Interactive chat application for the LangChain Calculator Agent
 */

// ==================================================
// DOM Elements
// ==================================================
const elements = {
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    chatForm: document.getElementById('chatForm'),
    sendBtn: document.getElementById('sendBtn'),
    typingIndicator: document.getElementById('typingIndicator'),
    toolsGrid: document.getElementById('toolsGrid'),
    sidebar: document.getElementById('sidebar'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    mobileMenuBtn: document.getElementById('mobileMenuBtn'),
    mobileOverlay: document.getElementById('mobileOverlay'),
    connectionStatus: document.getElementById('connectionStatus'),
    exampleButtons: document.querySelectorAll('.example-btn')
};

// ==================================================
// API Functions
// ==================================================
const api = {
    baseUrl: '/api',

    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch {
            return false;
        }
    },

    async getTools() {
        const response = await fetch(`${this.baseUrl}/tools`);
        if (!response.ok) throw new Error('Failed to fetch tools');
        return response.json();
    },

    async sendMessage(message) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send message');
        }

        return response.json();
    }
};

// ==================================================
// UI Functions
// ==================================================
const ui = {
    updateConnectionStatus(connected) {
        const statusDot = elements.connectionStatus.querySelector('.status-dot');
        const statusText = elements.connectionStatus.querySelector('.status-text');
        
        if (connected) {
            statusDot.classList.add('connected');
            statusDot.classList.remove('disconnected');
            statusText.textContent = 'Conectado';
        } else {
            statusDot.classList.remove('connected');
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Desconectado';
        }
    },

    showTyping() {
        elements.typingIndicator.classList.add('active');
        this.scrollToBottom();
    },

    hideTyping() {
        elements.typingIndicator.classList.remove('active');
    },

    scrollToBottom() {
        const container = document.querySelector('.chat-container');
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
    },

    formatMessage(text) {
        // Convert markdown-like syntax to HTML
        let formatted = text
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Line breaks
            .replace(/\n/g, '<br>');

        return formatted;
    },

    addMessage(content, type = 'assistant') {
        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';
        
        const message = document.createElement('div');
        message.className = 'message';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${this.formatMessage(content)}</p>`;
        
        message.appendChild(messageContent);
        wrapper.appendChild(avatar);
        wrapper.appendChild(message);
        
        elements.chatMessages.appendChild(wrapper);
        this.scrollToBottom();
    },

    addErrorMessage(error) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper assistant';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '⚠️';
        
        const message = document.createElement('div');
        message.className = 'message';
        message.style.borderColor = 'var(--error)';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p style="color: var(--error);">Error: ${error}</p>`;
        
        message.appendChild(messageContent);
        wrapper.appendChild(avatar);
        wrapper.appendChild(message);
        
        elements.chatMessages.appendChild(wrapper);
        this.scrollToBottom();
    },

    setInputEnabled(enabled) {
        elements.messageInput.disabled = !enabled;
        elements.sendBtn.disabled = !enabled;
    },

    clearInput() {
        elements.messageInput.value = '';
        elements.messageInput.style.height = 'auto';
    },

    renderTools(tools) {
        elements.toolsGrid.innerHTML = '';
        
        tools.forEach(tool => {
            const card = document.createElement('div');
            card.className = 'tool-card';
            
            card.innerHTML = `
                <div class="tool-icon">${tool.icon}</div>
                <div class="tool-info">
                    <div class="tool-name">${formatToolName(tool.name)}</div>
                    <div class="tool-description">${tool.description}</div>
                </div>
            `;
            
            elements.toolsGrid.appendChild(card);
        });
    },

    toggleSidebar(open) {
        if (open) {
            elements.sidebar.classList.add('open');
            elements.mobileOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            elements.sidebar.classList.remove('open');
            elements.mobileOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
};

// ==================================================
// Helper Functions
// ==================================================
function formatToolName(name) {
    return name
        .replace(/_tool$/, '')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// ==================================================
// Event Handlers
// ==================================================
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = elements.messageInput.value.trim();
    if (!message) return;
    
    // Add user message
    ui.addMessage(message, 'user');
    ui.clearInput();
    ui.setInputEnabled(false);
    ui.showTyping();
    
    try {
        const response = await api.sendMessage(message);
        ui.hideTyping();
        ui.addMessage(response.response, 'assistant');
    } catch (error) {
        ui.hideTyping();
        ui.addErrorMessage(error.message);
        console.error('Chat error:', error);
    } finally {
        ui.setInputEnabled(true);
        elements.messageInput.focus();
    }
}

function handleExampleClick(e) {
    const query = e.currentTarget.dataset.query;
    if (query) {
        elements.messageInput.value = query;
        autoResizeTextarea(elements.messageInput);
        elements.messageInput.focus();
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            ui.toggleSidebar(false);
        }
    }
}

function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        elements.chatForm.dispatchEvent(new Event('submit'));
    }
}

// ==================================================
// Initialization
// ==================================================
async function init() {
    // Check connection
    const isConnected = await api.checkHealth();
    ui.updateConnectionStatus(isConnected);
    
    // Load tools
    if (isConnected) {
        try {
            const tools = await api.getTools();
            ui.renderTools(tools);
        } catch (error) {
            console.error('Failed to load tools:', error);
        }
    }
    
    // Setup event listeners
    elements.chatForm.addEventListener('submit', handleSubmit);
    elements.messageInput.addEventListener('keydown', handleKeydown);
    elements.messageInput.addEventListener('input', () => autoResizeTextarea(elements.messageInput));
    
    // Example buttons
    elements.exampleButtons.forEach(btn => {
        btn.addEventListener('click', handleExampleClick);
    });
    
    // Sidebar toggles
    elements.mobileMenuBtn.addEventListener('click', () => ui.toggleSidebar(true));
    elements.sidebarToggle.addEventListener('click', () => ui.toggleSidebar(false));
    elements.mobileOverlay.addEventListener('click', () => ui.toggleSidebar(false));
    
    // Periodic connection check
    setInterval(async () => {
        const connected = await api.checkHealth();
        ui.updateConnectionStatus(connected);
    }, 30000);
    
    // Focus input
    elements.messageInput.focus();
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
