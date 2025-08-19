// chatbot.js
document.addEventListener('DOMContentLoaded', () => {
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const closeChat = document.getElementById('close-chat');
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle chat window
    chatIcon.addEventListener('click', () => chatWindow.classList.toggle('hidden'));
    closeChat.addEventListener('click', () => chatWindow.classList.add('hidden'));

    // Function to add a message to the chat window
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('mb-3');
        
        const messageP = document.createElement('p');
        messageP.classList.add('rounded-lg', 'py-2', 'px-4', 'inline-block');

        if (sender === 'user') {
            messageP.classList.add('bg-orange-500', 'text-white');
            messageDiv.classList.add('text-right'); // Align user messages to the right
        } else {
            messageP.classList.add('bg-gray-200', 'text-gray-800');
        }

        messageP.innerText = message;
        messageDiv.appendChild(messageP);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to the latest message
    }

    // Function to handle sending a message
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;

        addMessage(message, 'user');
        chatInput.value = '';

        try {
            // Send message to your backend server
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            addMessage(data.reply, 'ai');

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again later.', 'ai');
        }
    }

    // Event listeners for sending message
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});