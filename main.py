from flask import Flask, render_template
from data import db_session
from data.estate_items import Item

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask_secret_key'


@app.route('/index')
@app.route('/')
def index():
    return render_template('base.html', title='Главная')


@app.route('/catalog')
def catalog():
    db_sess = db_session.create_session()
    estates = db_sess.query(Item)
    return render_template('catalog.html', title='Каталог', estates=estates)


def main():
    db_session.global_init("db/estate.db")
    # db_sess = db_session.create_session()
    # estate = Item()
    # estate.name = "Kv1"
    # estate.about = "Новостройка. Площадь 50 м2, 2 комнаты, 1 спальня. Без мебели"
    # estate.image_link = 'https://i.ibb.co/P13DDGv/image.jpg'
    # estate.price = 1523000
    # db_sess.add(estate)
    # db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()
