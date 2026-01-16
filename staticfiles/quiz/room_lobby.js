const protocol = window.location.protocol === "https:" ? "wss" : "ws";

const socket = new WebSocket(
    protocol + "://" + window.location.host + "/ws/room/" + ROOM_CODE + "/"
);

socket.onopen = () => {
    console.log("✅ WS connected");
};

socket.onerror = (e) => {
    console.error("❌ WS error", e);
};

socket.onclose = () => {
    console.warn("⚠ WS closed");
};

socket.onmessage = function (e) {
    console.log("📩 WS RAW:", e.data);

    const data = JSON.parse(e.data);
    console.log("📦 PARSED:", data);

    // обновление списка игроков
    if (data.event === "players") {
        const list = document.getElementById("players");
        list.innerHTML = "";

        data.players.forEach(username => {
            list.innerHTML += `<li>${username}</li>`;
        });
    }

    // старт игры → редирект
    if (data.event === "start") {
        console.log("🚀 REDIRECT TO:", data.url);
        window.location.href = data.url;
    }
};

function startGame() {
    if (socket.readyState !== WebSocket.OPEN) {
        console.error("❌ WS not ready");
        return;
    }

    console.log("▶ start pressed");
    socket.send(JSON.stringify({ action: "start" }));
}