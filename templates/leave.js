const socket = require("socket.io");

document.getElementById("btn_leave").onclick = () => {
  const roomId = document.getElementById("room_id").value;
  socket.emit("leave", roomId);
};
