//ソケット通信を行うやつ
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

// 合計金額を表示するやつ
window.onload = function () {
    var tableElem = document.getElementById('session-menues');
    var rowElems = tableElem.rows;
    var price = 0;
    for (i = 1, len = rowElems.length; i < len; i++) {
        price += parseInt(rowElems[i].cells[3].innerText);
    }
    document.getElementById('sum-value').innerText = `${price}円`;
}