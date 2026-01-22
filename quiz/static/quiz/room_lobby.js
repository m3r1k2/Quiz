console.log("🧠 lobby js loaded");

const btn = document.getElementById("startBtn");
console.log("🔍 startBtn =", btn);

if (!btn) {
    console.error("❌ startBtn NOT FOUND");
} else {
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(
        protocol + "://" + location.host + "/ws/room/" + ROOM_CODE + "/"
    );

    socket.onopen = () => console.log("✅ WS connected");
    socket.onerror = e => console.error("❌ WS error", e);
    socket.onclose = () => console.warn("⚠ WS closed");

    socket.onmessage = e => {
        console.log("📩 WS RAW:", e.data);
        const data = JSON.parse(e.data);

        if (data.event === "players") {
            const list = document.getElementById("players");
            if (!list) return;
            list.innerHTML = "";
            data.players.forEach(u => list.innerHTML += `<li>${u}</li>`);
        }

        if (data.event === "start") {
            console.log("🚀 redirect to game");
            window.location.href = data.url;
        }
    };

    btn.addEventListener("click", () => {
        console.log("▶ start clicked");

        if (socket.readyState !== WebSocket.OPEN) {
            console.error("❌ WS not ready");
            return;
        }

        socket.send(JSON.stringify({ action: "start" }));
        console.log("📤 start sent");
    });
}