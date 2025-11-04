const socket = io();
const msgInput = document.getElementById("msg_input");
const messages = document.getElementById("messages");

socket.on("message", (msg) => {
  const li = document.createElement("li");
  li.textContent = msg;
  messages.appendChild(li);
  messages.scrollTop = messages.scrollHeight; // Auto-scroll
});

function sendMessage() {
  const msg = msgInput.value.trim();
  if (msg) {
    socket.send(msg);
    msgInput.value = "";
  }
}