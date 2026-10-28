const socket = new WebSocket("ws://localhost:8000/ws");

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};

export default socket;