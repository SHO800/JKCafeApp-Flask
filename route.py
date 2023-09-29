import json

from flask import Flask, render_template, redirect, request, make_response, jsonify
from register import app, db, socketio
from register.common.models.menues import MENUES
from register.common.models.session_menues import SESSION_MENUES
from register.common.models.orders import OrderItem
from register.common.models.orders import Order
from register.csv_to_DB import menues_csv_db
from werkzeug.security import generate_password_hash
import os
import datetime
import pytz
from register.controllers.line_notification import SEND


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")

@app.route('/register')
def register():
    socketio.emit('regi_display_reload')
    return render_template(
        "register.html",
        menues=MENUES.query.all(),
        session_menues=SESSION_MENUES.query.all()
        )

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
            value = MENUES.query.get(menue_id).value,
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


@app.route("/display/regi", methods=['GET']) # SHO800
def regi_display():
    if request.method == 'GET':
        return render_template("regi_display.html", session_menues=SESSION_MENUES.query.all())


@app.route("/display/kitchen", methods=['GET']) # SHO800
def kitchen_display():
    if request.method == 'GET':
        active_orders = Order.query.filter(Order.provided != 1).all()

        return render_template("kitchen_display.html", orders=active_orders)


@socketio.on("connect")
def handle_connect():
    socketio.emit('client_echo', {'msg': 'server connected!'})


@socketio.on('server_echo')
def handle_server_echo(msg):
    print('echo: ' + str(msg))

@app.route('/menus', methods=['GET'])
def menus():
    # params = request.args

    response = []
    menus = MENUES.query.all()
    for menu in menus:
        response.append({
            "id": menu.id,
            "menu_name": menu.menue_name,
            "value": menu.value,
            "short_name": menu.short_name,
            "text": menu.text,
        })
    response = json.dumps(response)
    print(response)

    # return make_response(jsonify(response))
    return make_response(response)


    # socketio.emit('regi_display_reload')
    # return render_template(
    #     menues=MENUES.query.all(),
    #     session_menues=SESSION_MENUES.query.all()
    # )
