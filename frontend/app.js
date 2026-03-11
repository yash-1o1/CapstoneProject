var socket = io();

// State
var currentUser = null;
var typingUsers = {};
var typingTimeout = null;
var isTyping = false;

// DOM
var nameModal = document.getElementById("name-modal");
var nameForm = document.getElementById("name-form");
var nameInput = document.getElementById("name-input");
var chatApp = document.getElementById("chat-app");
var messageArea = document.getElementById("message-area");
var messageForm = document.getElementById("message-form");
var messageInput = document.getElementById("message-input");
var userList = document.getElementById("user-list");
var onlineBadge = document.getElementById("online-badge");
var headerAvatars = document.getElementById("header-avatars");
var myAvatar = document.getElementById("my-avatar");
var typingIndicator = document.getElementById("typing-indicator");
var typingText = document.getElementById("typing-text");

// --- Helpers ---

function colorIndex(name) {
    var h = 0;
    for (var i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h);
    return Math.abs(h) % 8;
}

function initials(name) {
    var p = name.trim().split(/\s+/);
    return p.length >= 2 ? (p[0][0] + p[1][0]).toUpperCase() : name.substring(0, 2).toUpperCase();
}

function formatTime(ts) {
    var d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    messageArea.scrollTop = messageArea.scrollHeight;
}

// --- Name Entry ---

nameForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var name = nameInput.value.trim();
    if (!name || name.length > 30) return;
    currentUser = name;
    socket.emit("user:join", { name: name });
    nameModal.classList.add("hidden");
    chatApp.classList.remove("hidden");

    // Set my avatar in the input bar
    myAvatar.className = "input-avatar av-" + colorIndex(name);
    myAvatar.textContent = initials(name);

    messageInput.focus();
});

// --- Typing ---

messageInput.addEventListener("input", function () {
    if (!isTyping) {
        isTyping = true;
        socket.emit("typing:start");
    }
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(function () {
        isTyping = false;
        socket.emit("typing:stop");
    }, 2000);
});

// --- Send ---

messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = messageInput.value.trim();
    if (!text || text.length > 500) return;
    socket.emit("message:send", { text: text });
    messageInput.value = "";
    messageInput.focus();
    if (isTyping) {
        isTyping = false;
        clearTimeout(typingTimeout);
        socket.emit("typing:stop");
    }
});

// --- Socket Events ---

socket.on("chat:history", function (messages) {
    messageArea.innerHTML = "";
    messages.forEach(function (msg) { appendMessage(msg); });
    scrollToBottom();
});

socket.on("message:new", function (msg) {
    appendMessage(msg);
    scrollToBottom();
});

socket.on("users:list", function (users) {
    onlineBadge.textContent = users.length;

    // Sidebar user list
    userList.innerHTML = "";
    users.forEach(function (name) {
        var li = document.createElement("li");

        var av = document.createElement("div");
        av.className = "user-avatar av-" + colorIndex(name);
        av.textContent = initials(name);
        var dot = document.createElement("div");
        dot.className = "status-dot";
        av.appendChild(dot);

        var info = document.createElement("div");
        info.className = "user-info";
        var nm = document.createElement("div");
        nm.className = "user-name";
        nm.textContent = name;
        var st = document.createElement("div");
        st.className = "user-status";
        st.textContent = "Online";
        info.appendChild(nm);
        info.appendChild(st);

        li.appendChild(av);
        li.appendChild(info);
        userList.appendChild(li);
    });

    // Header mini avatars (show up to 5)
    headerAvatars.innerHTML = "";
    var shown = users.slice(0, 5);
    shown.forEach(function (name) {
        var av = document.createElement("div");
        av.className = "mini-avatar av-" + colorIndex(name);
        av.textContent = initials(name);
        headerAvatars.appendChild(av);
    });
    if (users.length > 5) {
        var more = document.createElement("div");
        more.className = "mini-avatar av-0";
        more.textContent = "+" + (users.length - 5);
        more.style.fontSize = "0.6rem";
        headerAvatars.appendChild(more);
    }
});

socket.on("user:joined", function (data) {
    appendSystemMessage(data.name + " joined the chat");
    scrollToBottom();
});

socket.on("user:left", function (data) {
    appendSystemMessage(data.name + " left the chat");
    delete typingUsers[data.name];
    updateTyping();
    scrollToBottom();
});

socket.on("typing:start", function (data) {
    typingUsers[data.name] = true;
    updateTyping();
});

socket.on("typing:stop", function (data) {
    delete typingUsers[data.name];
    updateTyping();
});

socket.on("error", function (data) {
    console.error("Server error:", data.message);
});

// --- Render ---

function appendMessage(msg) {
    var isOwn = msg.username === currentUser;

    var row = document.createElement("div");
    row.className = "msg-row " + (isOwn ? "own" : "other");

    // Avatar
    var av = document.createElement("div");
    av.className = "msg-avatar av-" + colorIndex(msg.username);
    av.textContent = initials(msg.username);
    row.appendChild(av);

    // Content
    var content = document.createElement("div");
    content.className = "msg-content";

    // Name (only for others)
    if (!isOwn) {
        var name = document.createElement("div");
        name.className = "msg-name";
        name.textContent = msg.username;
        content.appendChild(name);
    }

    // Bubble
    var bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.textContent = msg.text; // Safe: textContent
    content.appendChild(bubble);

    // Time
    var time = document.createElement("div");
    time.className = "msg-time";
    time.textContent = formatTime(msg.timestamp);
    content.appendChild(time);

    row.appendChild(content);
    messageArea.appendChild(row);
}

function appendSystemMessage(text) {
    var div = document.createElement("div");
    div.className = "msg-system";
    div.textContent = text;
    messageArea.appendChild(div);
}

function updateTyping() {
    var names = Object.keys(typingUsers);
    if (names.length === 0) {
        typingIndicator.classList.add("hidden");
        return;
    }
    typingIndicator.classList.remove("hidden");
    if (names.length === 1) {
        typingText.textContent = names[0] + " is typing...";
    } else if (names.length === 2) {
        typingText.textContent = names[0] + " and " + names[1] + " are typing...";
    } else {
        typingText.textContent = "Several people are typing...";
    }
}
