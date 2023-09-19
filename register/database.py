from register import app, db

def is_exist_db():
  with app.app_context():
    connection = db.engine.connect()
    is_user_table_exist = db.engine.dialect.has_table(connection, 'user')

    if not (is_user_table_exist):
        db.create_all()