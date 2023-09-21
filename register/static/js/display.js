document.addEventListener("DOMContentLoaded", (event) => {
    //表示領域を取得しておく
    const messageBox = document.getElementById("messages");

    //socketを作成して接続
    const socket = io.connect(`http${document.domain}:${location.port}`);

    //socketにメッセージが飛んできたら
    socket.on("receive_message", function (data){
        //中身をそれに更新
        messageBox.innerHTML = `<p>${data.message}</p>`
    })
})