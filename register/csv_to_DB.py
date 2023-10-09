import csv
import os.path

from register import app, db
from register.common.models.menues import MENUES, Toppings


def menues_csv_db():
    menues = MENUES.query.all()
    toppings = Toppings.query.all()

    for menue in menues:
        db.session.delete(menue)
    for topping in toppings:
        db.session.delete(topping)

    db.session.commit()

    with open(os.path.join(__file__, r'../static/csv/menues.csv'), encoding="utf_8") as f:
        reader = csv.reader(f)
        csv_datas = [row for row in reader]
        with app.app_context():
            i = 0
            for csv_data in csv_datas:
                i += 1
                if len(csv_data) > 3:
                    if not str:
                        csv_data[2] = csv_data[0]

                    menues = MENUES(
                        id=i,
                        menue_name=csv_data.pop(0), # [0]
                        value=int(csv_data.pop(0)), # [1]
                        short_name=csv_data.pop(0), # [2]
                        text=csv_data.pop(0), # [3]
                    )

                    print(csv_data)
                    if len(csv_data) > 0: # トッピングがあるということ
                        while len(csv_data) > 1: # もし数が合わなければ最後の要素は無視される
                            toppings = Toppings(
                                parent=i,
                                topping_name=csv_data.pop(0),
                                value=int(csv_data.pop(0)),
                            )
                            db.session.add(toppings)
                    db.session.add(menues)
            db.session.commit()