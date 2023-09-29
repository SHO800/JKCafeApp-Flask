import csv
import os.path

from register import app, db
from register.common.models.menues import MENUES


def menues_csv_db():
    menues = MENUES.query.all()
    for menue in menues:
        db.session.delete(menue)
        db.session.commit()

    with open(os.path.join(__file__, r'../static/csv/menues.csv'), encoding="utf_8") as f:
        reader = csv.reader(f)
        csv_datas = [row for row in reader]
        with app.app_context():
            for csv_data in csv_datas:
                if not str:
                    csv_data[2] = csv_data[0]

                menues = MENUES(
                    menue_name=csv_data[0],
                    value=int(csv_data[1]),
                    short_name=csv_data[2],
                    text=csv_data[3],
                )
                db.session.add(menues)
                db.session.commit()