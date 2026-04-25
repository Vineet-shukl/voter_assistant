document.addEventListener("DOMContentLoaded", () => {
    const chatLog = document.getElementById("chat-log");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const typingIndicator = document.getElementById("typing-indicator");
    const followupsContainer = document.getElementById("followups-container");
    const themeToggle = document.getElementById("theme-toggle");

    // Context object to store user state across messages
    let conversationContext = {
        state: null, // e.g., 'CA'
    };

    // Attempt to extract state code from user input simply
    function extractState(msg) {
        const stateMatch = msg.match(/\b(CA|NY|TX|FL|IL)\b/i);
        if (stateMatch) {
            conversationContext.state = stateMatch[1].toUpperCase();
        }
    }

    // Theme logic
    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        themeToggle.textContent = newTheme === "dark" ? "☀️" : "🌙";
        localStorage.setItem("theme", newTheme);
    };

    themeToggle.addEventListener("click", toggleTheme);
    if (localStorage.getItem("theme") === "dark") {
        toggleTheme(); // It defaults to light in HTML, so toggle if dark is saved
    }

    // Scroll to bottom
    const scrollToBottom = () => {
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    // Add message to UI
    const appendMessage = (text, sender, isMarkdown = false) => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", `${sender}-message`);
        
        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        
        if (isMarkdown && sender === 'bot') {
            bubble.innerHTML = marked.parse(text);
        } else {
            const p = document.createElement("p");
            p.textContent = text;
            bubble.appendChild(p);
        }
        
        msgDiv.appendChild(bubble);
        chatLog.appendChild(msgDiv);
        scrollToBottom();
    };

    // Add followup chips
    const renderFollowups = (chips) => {
        followupsContainer.innerHTML = "";
        chips.forEach(chipText => {
            const btn = document.createElement("button");
            btn.classList.add("chip");
            btn.textContent = chipText;
            btn.addEventListener("click", () => {
                userInput.value = chipText;
                chatForm.dispatchEvent(new Event("submit"));
            });
            followupsContainer.appendChild(btn);
        });
        scrollToBottom();
    };

    // Handle form submit
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // UI Updates for user message
        appendMessage(text, "user");
        userInput.value = "";
        followupsContainer.innerHTML = "";
        typingIndicator.classList.remove("hidden");
        scrollToBottom();

        extractState(text);

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, context: conversationContext })
            });

            if (!response.ok) {
                throw new Error("API responded with error");
            }

            const data = await response.json();
            typingIndicator.classList.add("hidden");
            appendMessage(data.reply, "bot", true);
            if (data.suggested_followups) {
                renderFollowups(data.suggested_followups);
            }
        } catch (error) {
            typingIndicator.classList.add("hidden");
            appendMessage("Sorry, I encountered an error connecting to the server.", "bot");
            console.error(error);
        }
    });
});
