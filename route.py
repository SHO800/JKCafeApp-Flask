import datetime
import json
import os

import pytz
from flask import render_template, redirect, request, make_response, jsonify
from flask_socketio import join_room, emit

from register import app, db, socketio
from register.common.models.menues import MENUES, Toppings
from register.common.models.orders import Order
from register.common.models.orders import OrderItem
from register.common.models.session_menues import SESSION_MENUES
from register.csv_to_DB import menues_csv_db


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")


# @app.route('/register')
# def register():
#     socketio.emit('regi_display_reload')
#     return render_template(
#         "register.html",
#         menues=MENUES.query.all(),
#         session_menues=SESSION_MENUES.query.all()
#     )


@app.route('/add_menue', methods=['POST'])
def add_menue():
    if request.method == 'POST':
        menue_id = int(request.form.get("id")[5:])
        quantity = int(request.form.get("quantity"))
        session_menues = SESSION_MENUES(
            menue_name=MENUES.query.get(menue_id).menue_name,
            menue_id=menue_id,
            short_name=MENUES.query.get(menue_id).short_name,
            quantity=quantity,
            value=MENUES.query.get(menue_id).value,
            sum_value=MENUES.query.get(menue_id).value * quantity
        )
        db.session.add(session_menues)
        db.session.commit()

        return redirect("/register")


@app.route('/delete_menue', methods=['POST'])
def delete_menue():
    if request.method == 'POST':
        menue_id = int(request.form.get("id")[5:])
        menue = SESSION_MENUES.query.get(menue_id)
        db.session.delete(menue)
        db.session.commit()

        return redirect("/register")


@app.route('/checkout_submit', methods=['POST'])
def checkout_submit():
    if request.method == 'POST':
        session_menues = SESSION_MENUES.query.all()

        menues_list = [menue.menue_name for menue in SESSION_MENUES.query.all()]
        sum_values = [menue.sum_value for menue in SESSION_MENUES.query.all()]
        sum_value = sum(sum_values)

        now_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

        checkout_parent = Order(
            checkouted_at=now_time,
            total_value=sum_value,
            provided=0,
        )
        db.session.add(checkout_parent)
        db.session.commit()

        for session_menue in session_menues:
            checkout_child = OrderItem(
                parent=now_time,
                menue_name=session_menue.menue_name,
                short_name=session_menue.short_name,
                quantity=session_menue.quantity,
                sum_value=session_menue.sum_value
            )
            db.session.add(checkout_child)
            db.session.commit()

        # LINE送信 一時停止中
        # SEND(menues_list, sum_value)

        delete_session()
        socketio.emit('regi_display_reload')
        socketio.emit('kitchen_display_reload')
        return redirect("/")


@app.route('/admin')
def admin():
    return render_template("admin.html")


@app.route('/menues_csv', methods=['GET', 'POST'])
def menues_csv():
    if request.method == 'GET':
        return redirect("/admin")
    else:
        file = request.files['file']
        file.filename = "menues.csv"
        # file.save(os.path.join('register/static/csv/', file.filename))
        file.save(os.path.join(__file__, '..', 'register', 'static', 'csv', file.filename))
        menues_csv_db()
        return redirect("/admin")


def delete_session():
    session_menues = SESSION_MENUES.query.all()
    for session_menue in session_menues:
        db.session.delete(session_menue)
        db.session.commit()


@app.route("/clear")
def clear():
    delete_session()
    socketio.emit('regi_display_reload')
    socketio.emit('kitchen_display_reload')
    return redirect("/")


@app.route("/display/regi", methods=['GET'])  # SHO800
def regi_display():
    if request.method == 'GET':
        return render_template("regi_display.html", session_menues=SESSION_MENUES.query.all())


@app.route("/display/kitchen", methods=['GET'])  # SHO800
def kitchen_display():
    if request.method == 'GET':
        active_orders = Order.query.filter(Order.provided != 1).all()

        return render_template("kitchen_display.html", orders=active_orders)


room_id = 0
@app.route("/getClientId", methods=['GET'])
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
    menus = MENUES.query.all()
    toppings = Toppings.query.all()
    for menu in menus:
        toppings_of_menu = list(filter(lambda item: item.parent == menu.id, toppings))
        toppings_of_menu = {item.topping_name: {"value": item.value} for item in toppings_of_menu}
        response[menu.id] = {
            "menu_name": menu.menue_name,
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
    #     menues=MENUES.query.all(),
    #     session_menues=SESSION_MENUES.query.all()
    # )
