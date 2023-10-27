import datetime
import json
import os
import uuid
from typing import List

import pytz
from flask import render_template, redirect, request, make_response, jsonify
from flask_socketio import join_room, emit

from register.controllers.line_notification import send
from register import app, db, socketio
from register.common.models.menus import Menus, Toppings, MenuCoupons
from register.common.models.orders import Order, OrderItem, Options, OrderCoupons
from register.csv_to_DB import menus_csv_db


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")


@app.route('/checkout-submit', methods=['POST'])
def checkout_submit():
    if request.method == 'POST':
        order_datas = request.get_json()
        now_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

        sum_value = sum([data["sum"] for data in order_datas])

        order_uuid = str(uuid.uuid4())
        order_parent = Order(
            uuid=order_uuid,
            checked_out_at=now_time,
            total_value=sum_value,
            provided=0,
        )

        db.session.add(order_parent)

        for order_data in order_datas:
            order_child_uuid = str(uuid.uuid4())
            order_child = OrderItem(
                uuid=order_child_uuid,
                parent=order_uuid,
                menu_id=int(order_data['id']),
                menu_name=order_data['menu_name'],
                short_name=order_data['short_name'],
                value=int(order_data['value']),
                quantity=int(order_data['quantity']),
                sum=int(order_data['sum']),
            )
            db.session.add(order_child)

            if order_data['topping']:
                for order_topping_name in order_data['topping']:
                    order_topping = order_data['topping'][order_topping_name]
                    if order_topping["quantity"] <= 0:
                        continue

                    order_option_uuid = str(uuid.uuid4())
                    order_option = Options(
                        uuid=order_option_uuid,
                        parent=order_child_uuid,
                        option_name=order_topping_name,
                        value=int(order_topping["value"]),
                        quantity=int(order_topping["quantity"]),
                    )
                    db.session.add(order_option)

            if order_data['coupon']:
                for order_coupon_name in order_data['coupon']:
                    order_coupon = order_data['coupon'][order_coupon_name]
                    if order_coupon["quantity"] <= 0:
                        continue

                    order_coupon_uuid = str(uuid.uuid4())
                    order_coupon_add_data = OrderCoupons(
                        uuid=order_coupon_uuid,
                        parent=order_child_uuid,
                        coupon_name=order_coupon_name,
                        value=int(order_coupon["value"]),
                        quantity=int(order_coupon["quantity"]),
                    )
                    db.session.add(order_coupon_add_data)

        send("menu", order_parent.total_value)
        db.session.commit()

        print("order_added!")
        send_data = send_kitchen_orders()
        # LINE送信 一時停止中
        return order_datas


@app.route('/admin')
def admin():
    return render_template("admin.html")


@app.route('/menus-csv', methods=['GET', 'POST'])
def menus_csv():
    if request.method == 'GET':
        return redirect("/admin")
    else:
        file = request.files['file']
        file.filename = "menus.csv"

        file.save(os.path.join(__file__, '..', 'register', 'static', 'csv', file.filename))
        menus_csv_db()
        return redirect("/admin")


room_id = 0


@app.route("/client-id", methods=['GET'])
def give_client_id():
    global room_id
    # room_id += 1 # もしレジを複数台にするならこれ使う
    print("told_register_clientId", room_id)
    return jsonify({'clientId': room_id})


@app.route('/menus', methods=['GET'])
def menus():
    # params = request.args

    response = {}
    menus = Menus.query.all()
    toppings = Toppings.query.all()
    coupons = MenuCoupons.query.all()
    for menu in menus:
        toppings_of_menu = list(filter(lambda item: item.parent == menu.id, toppings))
        toppings_of_menu = {item.topping_name: {"value": item.value} for item in toppings_of_menu}
        coupons_of_menu = list(filter(lambda item: item.parent == menu.id, coupons))
        coupons_of_menu = {item.coupon_name: {"value": item.value} for item in coupons_of_menu}
        response[menu.id] = {
            "menu_name": menu.menu_name,
            "value": menu.value,
            "short_name": menu.short_name,
            "text": menu.text,
            "topping": toppings_of_menu,
            "coupon": coupons_of_menu
        }
    response = json.dumps(response)
    return make_response(response)


@socketio.on("connect", namespace='/register')
def handle_connect():
    send_register_history()
    pass


@socketio.on("connect", namespace='/display/register')
def handle_connect():
    print("レジのディスプレイが接続しました")
    pass


@socketio.on("connect", namespace="/display/kitchen")
def handle_connect():
    print("キッチンのディスプレイが接続しました")
    send_kitchen_orders()


@socketio.on("join", namespace='/display/register')
def join_register_display(msg):
    join_room(msg["clientId"])
    print("レジのディスプレイが次のルームに参加しました: ", msg["clientId"])


@socketio.on('temp_order_data', namespace='/register')
def display_bridge(msg):
    data_json = json.loads(msg["data"])
    print("error", msg)
    print(f"{msg['clientId']}番レジの情報が更新されました")
    emit("temp_order_data", data_json, to=str(msg["clientId"]), namespace='/display/register')


def send_kitchen_orders():
    send_data = []

    active_orders: List[Order] = Order.query.filter(Order.provided != 1).all()
    for order in active_orders:
        items = []
        for item in order.item:
            options = []
            for option in item.option:
                options.append({
                    "uuid": option.uuid,
                    "option_name": option.option_name,
                    "quantity": option.quantity,
                })

            items.append({
                "uuid": item.uuid,
                "menu_id": item.menu_id,
                "menu_name": item.menu_name,
                "quantity": item.quantity,
                "option": options,
            })

        checked_out_at = order.checked_out_at.strftime('%y/%m/%d %H:%M:%S')

        send_data.append({
            "uuid": order.uuid,
            "orderedAt": checked_out_at,
            "items": items,
        })

    socketio.emit("kitchen_order_data", send_data, namespace='/display/kitchen')
    print("キッチンに情報を送信しました")
    send_register_history()
    return send_data


@socketio.on('kitchen_order_provided', namespace='/display/kitchen')
def kitchen_order_provided(msg):
    order = Order.query.get(msg)
    order.provided = 1
    db.session.commit()
    send_kitchen_orders()
    print("注文の提供が完了したようです", msg)


def send_register_history():
    send_data = []

    # recently_orders: List[Order] = Order.query.filter(Order.provided != 1).all()
    last_ten = Order.query.order_by(Order.checked_out_at.desc()).limit(50).all()
    for order in last_ten:
        items = []
        for item in order.item:
            options = []
            for option in item.option:
                options.append({
                    "uuid": option.uuid,
                    "option_name": option.option_name,
                    "quantity": option.quantity,
                })

            items.append({
                "uuid": item.uuid,
                "menu_id": item.menu_id,
                "menu_name": item.menu_name,
                "quantity": item.quantity,
                "option": options,
            })

        checked_out_at = order.checked_out_at.strftime('%y/%m/%d %H:%M:%S')

        send_data.append({
            "uuid": order.uuid,
            "orderedAt": checked_out_at,
            "items": items,
        })



    socketio.emit("history", send_data, namespace='/register')
    print("レジに履歴を送信しました")
    return send_data