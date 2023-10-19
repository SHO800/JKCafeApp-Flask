import datetime
import json
import os

import pytz
from flask import render_template, redirect, request, make_response, jsonify
from flask_socketio import join_room, emit
import uuid

from register import app, db, socketio
from register.common.models.menus import Menus, Toppings
from register.common.models.orders import Order, OrderItem, Options
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
                        coupon_amount=int(order_topping["couponAmount"])
                    )
                    db.session.add(order_option)


        db.session.commit()
        return order_datas
        # LINE送信 一時停止中
        # SEND(menus_list, sum_value)


        db.session.commit()
        socketio.emit('regi_display_reload')
        socketio.emit('kitchen_display_reload')
        return redirect("/")


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
        # file.save(os.path.join('register/static/csv/', file.filename))
        file.save(os.path.join(__file__, '..', 'register', 'static', 'csv', file.filename))
        menus_csv_db()
        return redirect("/admin")


# def delete_session():
#     session_menus = SESSION_MENUES.query.all()
#     for session_menu in session_menus:
#         db.session.delete(session_menu)
#         db.session.commit()


room_id = 0


@app.route("/client-id", methods=['GET'])
def give_client_id():
    global room_id
    room_id += 1
    print("told_register_clientId", room_id)
    return jsonify({'clientId': room_id})


@socketio.on("connect", namespace='/register')
def handle_connect():
    # socketio.emit('notice_join', {'id': room_id}, namespace='/register')
    pass


@socketio.on("connect", namespace='/display/register')
def handle_connect():
    pass


@socketio.on("join", namespace='/display/register')
def join_register_display(msg):
    join_room(msg["clientId"])
    print("join", msg["clientId"])


@socketio.on('server_echo')
def handle_server_echo(msg):
    print('echo: ' + str(msg), )


@socketio.on('temp_order_data', namespace='/register')
def display_bridge(msg):
    data_json = json.loads(msg["data"])
    print("to", msg["clientId"])

    emit("temp_order_data", data_json, to=str(msg["clientId"]), namespace='/display/register')
    pass


@app.route('/menus', methods=['GET'])
def menus():
    # params = request.args

    response = {}
    menus = Menus.query.all()
    toppings = Toppings.query.all()
    for menu in menus:
        toppings_of_menu = list(filter(lambda item: item.parent == menu.id, toppings))
        toppings_of_menu = {item.topping_name: {"value": item.value} for item in toppings_of_menu}
        response[menu.id] = {
            "menu_name": menu.menu_name,
            "value": menu.value,
            "short_name": menu.short_name,
            "text": menu.text,
            "topping": toppings_of_menu
        }
    response = json.dumps(response)
    # return make_response(jsonify(response))
    return make_response(response)

    # socketio.emit('regi_display_reload')
    # return render_template(
    #     menus=Menus.query.all(),
    #     session_menus=SESSION_MENUES.query.all()
    # )

# @app.route('/register')
# def register():
#     socketio.emit('regi_display_reload')
#     return render_template(
#         "register.html",
#         menus=Menus.query.all(),
#         session_menus=SESSION_MENUES.query.all()
#     )


# @app.route('/add_menu', methods=['POST'])
# def add_menu():
#     if request.method == 'POST':
#         menu_id = int(request.form.get("id")[5:])
#         quantity = int(request.form.get("quantity"))
#         session_menus = SESSION_MENUES(
#             menu_name=Menus.query.get(menu_id).menu_name,
#             menu_id=menu_id,
#             short_name=Menus.query.get(menu_id).short_name,
#             quantity=quantity,
#             value=Menus.query.get(menu_id).value,
#             sum_value=Menus.query.get(menu_id).value * quantity
#         )
#         db.session.add(session_menus)
#         db.session.commit()
#
#         return redirect("/register")

# @app.route('/delete_menu', methods=['POST'])
# def delete_menu():
#     if request.method == 'POST':
#         menu_id = int(request.form.get("id")[5:])
#         menu = SESSION_MENUES.query.get(menu_id)
#         db.session.delete(menu)
#         db.session.commit()
#
#         return redirect("/register")

# @app.route("/clear")
# def clear():
#     delete_session()
#     socketio.emit('regi_display_reload')
#     socketio.emit('kitchen_display_reload')
#     return redirect("/")


# @app.route("/display/regi", methods=['GET'])  # SHO800
# def regi_display():
#     if request.method == 'GET':
#         return render_template("regi_display.html", session_menus=SESSION_MENUES.query.all())


# @app.route("/display/kitchen", methods=['GET'])  # SHO800
# def kitchen_display():
#     if request.method == 'GET':
#         active_orders = Order.query.filter(Order.provided != 1).all()
#
#         return render_template("kitchen_display.html", orders=active_orders)
