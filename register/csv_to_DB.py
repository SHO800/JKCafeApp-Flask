import csv
from register import app, db
from register.common.models.menues import MENUES


def menues_csv_db():
    menues = MENUES.query.all()
    for menue in menues:
        db.session.delete(menue)
        db.session.commit()

    with open(r'register\static\csv\menues.csv', encoding="utf_8") as f:
        reader = csv.reader(f)
        csv_datas = [row for row in reader]
        with app.app_context():
            for csv_data in csv_datas:
                menues = MENUES(
                    menue_name = csv_data[0],
                    value = int(csv_data[1]),
                    text = csv_data[2]
                )
                db.session.add(menues)
                db.session.commit()