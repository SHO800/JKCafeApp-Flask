document.addEventListener("DOMContentLoaded", (event) => {
    //表示領域を取得しておく
    const messageBox = document.getElementById("content");

    // socketオブジェクト生成
    let socket = io();
    // サーバとのコネクション確立
    socket.on('connect', function() {
        socket.emit('server_echo', {data: 'client connected!'});
    });
    // サーバからのメッセージを出力する関数
    socket.on('client_echo', function(data) {
        console.log("echo" + ': ' + data.msg);
    });
    //socketに情報が飛んできたら
    socket.on('show', function (data){
        console.log("show: " + data.menu)
        //中身をそれに更新
        messageBox.innerHTML = `<p>${data.menu}</p>`
    })
    //reloadが飛んできたら
    socket.on('regi_display_reload', function(){
        location.reload()
    })
})