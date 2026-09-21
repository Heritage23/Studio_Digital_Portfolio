const BACKEND_URL = "https://studio-digital-portfolio.onrender.com";
// const BACKEND_URL = "http://127.0.0.1:8000";

/* ==================================================
HAMBURGER MENU
================================================== */

const hamburger =
document.getElementById("hamburger");

const mobileNav =
document.getElementById("mobileNav");

hamburger.addEventListener("click", function () {


mobileNav.classList.toggle("active");

const isOpen =
    mobileNav.classList.contains("active");

hamburger.setAttribute(
    "aria-expanded",
    isOpen
);

hamburger.setAttribute(
    "aria-label",
    isOpen ? "Close menu" : "Open menu"
);


});

const mobileLinks =
mobileNav.querySelectorAll("a");

mobileLinks.forEach(function (link) {


link.addEventListener("click", function () {

    mobileNav.classList.remove("active");

    hamburger.setAttribute(
        "aria-expanded",
        "false"
    );

    hamburger.setAttribute(
        "aria-label",
        "Open menu"
    );

});


});

/* ==================================================
CHATBOT
Connected to FastAPI + Gemini
================================================== */

const chatbotButton =
document.getElementById("chatbotButton");

const chatbotWindow =
document.getElementById("chatbotWindow");

const chatbotClose =
document.getElementById("chatbotClose");

const chatInput =
document.getElementById("chatInput");

const sendMessage =
document.getElementById("sendMessage");

const chatbotMessages =
document.getElementById("chatbotMessages");

/* ==================================================
OPEN CHATBOT
================================================== */

chatbotButton.addEventListener("click", function () {


chatbotWindow.classList.toggle("active");

if (
    chatbotWindow.classList.contains("active")
) {

    setTimeout(function () {

        chatInput.focus();

    }, 300);

}


});

/* ==================================================
CLOSE CHATBOT
================================================== */

chatbotClose.addEventListener("click", function () {


chatbotWindow.classList.remove("active");


});

/* ==================================================
ADD CHAT MESSAGE
================================================== */

function addChatMessage(text, sender) {


const message =
    document.createElement("div");

message.classList.add(
    "chat-message",
    sender
);

message.textContent = text;

chatbotMessages.appendChild(message);

chatbotMessages.scrollTop =
    chatbotMessages.scrollHeight;

return message;


}

/* ==================================================
ADD TYPING INDICATOR
================================================== */

function addTypingIndicator() {


const message =
    document.createElement("div");

message.classList.add(
    "chat-message",
    "bot",
    "typing-message"
);


message.innerHTML = `
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
`;


chatbotMessages.appendChild(message);

chatbotMessages.scrollTop =
    chatbotMessages.scrollHeight;


return message;


}

/* ==================================================
SEND MESSAGE TO AI BACKEND
================================================== */

async function sendChatMessage() {


const text =
    chatInput.value.trim();


if (!text) {
    return;
}


/* Add visitor message */

addChatMessage(
    text,
    "user"
);


/* Clear input */

chatInput.value = "";


/* Disable button while AI responds */

sendMessage.disabled = true;

chatInput.disabled = true;


/* Show typing indicator */

const loadingMessage =
    addTypingIndicator();


try {

    const response =
        await fetch(
            `${BACKEND_URL}/chat`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: text
                })
            }
        );


    /* Check if server responded successfully */

    if (!response.ok) {

        throw new Error(
            "Server returned an error"
        );

    }


    /* Convert response to JSON */

    const data =
        await response.json();


    /* Replace typing indicator with AI response */

    loadingMessage.classList.remove(
        "typing-message"
    );

    loadingMessage.innerHTML =
        data.reply ||
        "Sorry, I couldn't generate a response.";


} catch (error) {

    console.error(
        "Chatbot error:",
        error
    );


    /* Show friendly error */

    loadingMessage.classList.remove(
        "typing-message"
    );

    loadingMessage.innerHTML =
        "Sorry, I'm having trouble connecting right now. Please try again or contact Studio Digital on WhatsApp.";

}


/* Re-enable input */

sendMessage.disabled = false;

chatInput.disabled = false;


/* Scroll to newest message */

chatbotMessages.scrollTop =
    chatbotMessages.scrollHeight;


/* Put cursor back in input */

chatInput.focus();


}

/* ==================================================
SEND BUTTON
================================================== */

sendMessage.addEventListener(
"click",
sendChatMessage
);

/* ==================================================
ENTER KEY
================================================== */

chatInput.addEventListener(
"keydown",
function (event) {


    if (event.key === "Enter") {

        event.preventDefault();

        sendChatMessage();

    }

}


);
