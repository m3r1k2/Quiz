const socket = new WebSocket(
    "ws://" + window.location.host + "/ws/room/" + ROOM_CODE + "/"
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.event === "players") {
        updatePlayers(data.players);
    }

    if (data.event === "question") {
        window.location.href = "/quiz/play/" + data.quiz_id + "/?q=" + data.index;
    }
};

function updatePlayers(players) {
    const ul = document.getElementById("players");
    ul.innerHTML = "";
    players.forEach(p => {
        ul.innerHTML += `<li>${p.name}</li>`;
    });
}

document.getElementById("start-btn")?.addEventListener("click", function () {
    socket.send(JSON.stringify({ action: "start_quiz" }));
});