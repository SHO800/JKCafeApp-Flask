document.addEventListener("DOMContentLoaded", (event) => {
    //表示領域を取得しておく
    const messageBox = document.getElementById("content");

    // socketオブジェクト生成
    let socket = io();
    // サーバとのコネクション確立
    socket.on('connect', function() {
        socket.emit('server_echo', {data: 'client connected!'});
    });
    //reloadが飛んできたら
    socket.on('kitchen_display_reload', function(){
        location.reload()
    })
})