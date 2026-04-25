/* ===== CONFIG ===== */
const CACHE_VERSION = "v2";
const CACHE_TTL_MS  = 10 * 60 * 1000; // 10 min client-side cache per question
const DEBOUNCE_MS   = 300;

/* ===== ELEMENTS ===== */
const chatLog          = document.getElementById("chat-log");
const chatForm         = document.getElementById("chat-form");
const userInput        = document.getElementById("user-input");
const typingIndicator  = document.getElementById("typing-indicator");
const followupsContainer = document.getElementById("followups-container");
const themeToggle      = document.getElementById("theme-toggle");
const sidebarOpen      = document.getElementById("sidebar-open");
const sidebarClose     = document.getElementById("sidebar-close");
const sidebar          = document.getElementById("sidebar");
const stateSelect      = document.getElementById("state-select");
const ageinput         = document.getElementById("age-input");
const citizenCheck     = document.getElementById("citizen-check");
const checkBtn         = document.getElementById("check-eligibility-btn");
const eligibilityResult = document.getElementById("eligibility-result");
const stateBadge       = document.getElementById("state-badge");

/* ===== STATE ===== */
let conversationContext = {};
let sendDebounceTimer   = null;
let isSending           = false;

/* ===== THEME ===== */
const setTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
    localStorage.setItem("vw-theme", theme);
};
themeToggle.addEventListener("click", () => {
    setTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark");
});
setTheme(localStorage.getItem("vw-theme") || "dark");

/* ===== SIDEBAR ===== */
sidebarOpen?.addEventListener("click", () => sidebar.classList.add("open"));
sidebarClose?.addEventListener("click", () => sidebar.classList.remove("open"));

/* ===== STATE SELECTOR ===== */
stateSelect.addEventListener("change", () => {
    const state = stateSelect.value;
    if (state) {
        conversationContext.state = state;
        const stateName = STATE_NAMES[state] || state;
        stateBadge.textContent = `${stateName} — ECI Data`;
        appendBot(`📍 Got it! I'll use **${stateName}** for state-specific election schedules. What would you like to know?`, "local");
    } else {
        delete conversationContext.state;
        stateBadge.textContent = "Powered by ECI Data";
    }
});

/* ===== QUICK TOPIC CHIPS ===== */
document.querySelectorAll(".topic-chip").forEach(chip => {
    chip.addEventListener("click", () => sendMessage(chip.dataset.msg));
});

/* ===== ELIGIBILITY CHECKER ===== */
checkBtn.addEventListener("click", async () => {
    const age     = parseInt(ageinput.value, 10);
    const citizen = citizenCheck.checked;
    const state   = stateSelect.value || "CA";

    if (isNaN(age) || age < 0 || age > 120) {
        eligibilityResult.textContent = "⚠️ Enter a valid age (0–120).";
        eligibilityResult.className = "ineligible";
        eligibilityResult.classList.remove("hidden");
        return;
    }

    try {
        const res = await fetch(`/eligibility?age=${age}&citizen=${citizen}&state=${state}`);
        const data = await res.json();
        eligibilityResult.classList.remove("hidden");
        if (data.eligible) {
            eligibilityResult.textContent = "✅ You appear eligible to vote!";
            eligibilityResult.className = "eligible";
        } else {
            eligibilityResult.textContent = `❌ ${data.reasons[0]}`;
            eligibilityResult.className = "ineligible";
        }
    } catch {
        eligibilityResult.textContent = "⚠️ Could not check eligibility.";
        eligibilityResult.className = "ineligible";
        eligibilityResult.classList.remove("hidden");
    }
});

/* ===== RESPONSE CACHE ===== */
const cacheKey = (msg) => `${CACHE_VERSION}:${msg.trim().toLowerCase()}`;

const getCache = (msg) => {
    try {
        const raw = sessionStorage.getItem(cacheKey(msg));
        if (!raw) return null;
        const { data, ts } = JSON.parse(raw);
        if (Date.now() - ts > CACHE_TTL_MS) { sessionStorage.removeItem(cacheKey(msg)); return null; }
        return data;
    } catch { return null; }
};

const setCache = (msg, data) => {
    try {
        sessionStorage.setItem(cacheKey(msg), JSON.stringify({ data, ts: Date.now() }));
    } catch { /* quota exceeded, ignore */ }
};

/* ===== UI HELPERS ===== */
const scrollBottom = () => chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: "smooth" });

function appendUser(text) {
    const row = document.createElement("div");
    row.className = "msg-row user";
    row.innerHTML = `<div class="bubble user-bubble">${escapeHtml(text)}</div>`;
    chatLog.appendChild(row);
    scrollBottom();
}

function appendBot(text, source = "ai") {
    const row = document.createElement("div");
    row.className = "msg-row bot";
    const badge = source === "local"
        ? `<span class="source-badge local">⚡ instant</span>`
        : `<span class="source-badge ai">🤖 AI</span>`;
    row.innerHTML = `
        <div class="avatar">🗳️</div>
        <div class="bubble bot-bubble">
            ${marked.parse(text)}
            <div class="msg-meta">${badge}</div>
        </div>`;
    chatLog.appendChild(row);
    scrollBottom();
}

function setFollowups(chips) {
    followupsContainer.innerHTML = "";
    chips.slice(0, 3).forEach(text => {
        const btn = document.createElement("button");
        btn.className = "followup-chip";
        btn.textContent = text;
        btn.addEventListener("click", () => sendMessage(text));
        followupsContainer.appendChild(btn);
    });
}

function escapeHtml(str) {
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

/* ===== STATE NAMES MAP ===== */
const STATE_NAMES = {
    DL: "Delhi", BR: "Bihar", WB: "West Bengal", TN: "Tamil Nadu",
    KL: "Kerala", AS: "Assam", UP: "Uttar Pradesh", MH: "Maharashtra",
    GJ: "Gujarat", RJ: "Rajasthan", KA: "Karnataka", MP: "Madhya Pradesh", PB: "Punjab"
};

/* ===== INDIA FOLLOW-UP CHIPS ===== */
function pick_followups(reply) {
    const r = reply.toLowerCase();
    if (r.includes("form 6") || r.includes("register")) {
        return ["What documents do I need for Form 6?", "Can I register online?", "Where do I find my BLO?"];
    }
    if (r.includes("epic") || r.includes("voter id")) {
        return ["How do I get a digital e-EPIC?", "How to correct my Voter ID details?", "What if I lost my Voter ID?"];
    }
    if (r.includes("evm") || r.includes("vvpat") || r.includes("voting machine")) {
        return ["Is EVM voting safe?", "What is VVPAT?", "How do I use EVM on election day?"];
    }
    if (r.includes("deadline") || r.includes("schedule") || r.includes("election date")) {
        return ["How do I register before the deadline?", "When will counting happen?", "When is the next Lok Sabha?"];
    }
    if (r.includes("alternative") || r.includes("aadhaar") || r.includes("pan")) {
        return ["Can I use Aadhaar to vote?", "What if my name is on the roll but I have no ID?", "How to get Voter ID fast?"];
    }
    if (r.includes("lok sabha") || r.includes("parliament")) {
        return ["What is a Vidhan Sabha election?", "How many seats in Lok Sabha?", "When is next general election?"];
    }
    return ["How do I register to vote?", "What is the EPIC Voter ID card?", "How do I find my polling booth?"];
}
async function sendMessage(text) {
    text = text.trim();
    if (!text || isSending) return;

    appendUser(text);
    followupsContainer.innerHTML = "";
    userInput.value = "";

    // 1. Check session cache first (saves API call entirely)
    const cached = getCache(text);
    if (cached) {
        appendBot(cached.reply, "local"); // treat cached as instant
        setFollowups(cached.suggested_followups || []);
        return;
    }

    // 2. Show typing and call API
    isSending = true;
    typingIndicator.classList.remove("hidden");
    scrollBottom();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, context: conversationContext })
        });

        typingIndicator.classList.add("hidden");

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        appendBot(data.reply, data.source || "ai");
        setFollowups(data.suggested_followups || []);
        setCache(text, data); // store in session cache

    } catch (err) {
        typingIndicator.classList.add("hidden");
        appendBot("⚠️ Something went wrong. Please try again or visit [eci.gov.in](https://eci.gov.in) or call the National Voter Helpline at **1950** (toll-free).", "local");
        console.error(err);
    } finally {
        isSending = false;
    }
}

/* ===== FORM SUBMIT with debounce ===== */
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    clearTimeout(sendDebounceTimer);
    sendDebounceTimer = setTimeout(() => sendMessage(userInput.value), DEBOUNCE_MS);
});

/* ===== ENTER key passthrough ===== */
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit"));
    }
});

/* ===== RESTORE STATE from sessionStorage ===== */
const savedState = sessionStorage.getItem("vw-india-state");
if (savedState) {
    stateSelect.value = savedState;
    conversationContext.state = savedState;
    const stateName = STATE_NAMES[savedState] || savedState;
    stateBadge.textContent = `${stateName} — ECI Data`;
}
stateSelect.addEventListener("change", () => {
    sessionStorage.setItem("vw-india-state", stateSelect.value);
});
