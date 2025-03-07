const socketio = require("socket.io");

socketio.on("msg", (msg) => {
  const div = document.createElement("div");
  div.classList.add("user-msg");
  div.innerText = msg;
  const messageContainer = document.getElementById("messages");
  messageContainer.appendChild(div);
});

function sendMsg(roomId, roomName) {
  const inputMsg = document.getElementById("msgInput");
  if (inputMsg && inputMsg.value != "") {
    socketio.emit("room_msg", {
      room_id: roomId,
      room_name: roomName,
      message: inputMsg.value.trim(),
    });
    inputMsg.value = "";
  }
}

document.addEventListener("keypress", (ev) => {
  if (ev.key == "enter") {
    sendMsg();
  }
});
