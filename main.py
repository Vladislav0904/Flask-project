from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.estate_items import Item
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.buildings_edit import BuildingForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/index')
@app.route('/')
def index():
    return render_template('base.html', title='Главная')


@app.route('/catalog')
def catalog():
    db_sess = db_session.create_session()
    estates = db_sess.query(Item)
    return render_template('catalog.html', title='Каталог', estates=estates)


@app.route('/building/<int:id>')
def building(id):
    db_sess = db_session.create_session()
    building = db_sess.query(Item).get(id)
    return render_template('building.html', building=building, title=building.name)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.is_admin = False
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/post_edit')
def post_edit():
    db_sess = db_session.create_session()
    estates = db_sess.query(Item).filter(current_user.id == Item.user_id)
    return render_template('post_edit.html', title='Мои здания', estates=estates)


@app.route('/building_info_edit', methods=['GET', 'POST'])
@login_required
def add_building():
    form = BuildingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        item = Item(
            name=form.name.data,
            about=form.about.data,
            tags=form.tags.data,
            price=form.price.data,
            address=form.address.data,
            image_link=form.image_link.data)
        current_user.items.append(item)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/catalog')
    return render_template('building_info_edit.html', title='Добавление здания',
                           form=form)


@app.route('/building_info_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_building(id):
    form = BuildingForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        items = db_sess.query(Item).filter(Item.id == id,
                                           Item.user == current_user
                                           ).first()
        print(items)
        if items:
            form.name.data = items.name
            form.about.data = items.about
            form.tags.data = items.tags
            form.price.data = items.price
            form.address.data = items.address
            form.image_link.data = items.image_link
            print(items)
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        items = db_sess.query(Item).filter(Item.id == id,
                                           Item.user == current_user
                                           ).first()
        if items:
            items.name = form.name.data
            items.about = form.about.data
            items.tags = form.tags.data
            items.price = form.price.data
            items.address = form.address.data
            items.image_link = form.image_link.data
            db_sess.commit()
            return redirect('/post_edit')
        else:
            abort(404)

    return render_template('building_info_edit.html',
                           title='Редактирование информации о здании',
                           form=form
                           )


@app.route('/building_info_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def building_delete(id):
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.id == id,
                                      Item.user == current_user
                                      ).first()
    if items:
        db_sess.delete(items)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/post_edit') 







def main():
    db_session.global_init("db/estate.db")
    # db_sess = db_session.create_session()
    # estate = Item()
    # estate.name = "Сарай в центре Москвы"
    # estate.about = "Современная, удобная планировка 97 серии, комната 19 м., кухня-9м., кладовка, санузел раздельный. " \
    #                "Дом новый, сдача апрель-май. мкрн Парковый, новый микрорайон №45. Отделка полная строительная: " \
    #                "обои, линолеум, вся сантехника, натяжные потолки, межкомнатные двери ламинированные, " \
    #                "лоджия застеклена, современная детская и спортивная площадка, рядом лес. остановка, " \
    #                "магазины рядом. "
    # estate.image_link = 'https://i.ibb.co/hYGdRB3/saray.jpg'
    # estate.address = 'ул. Охотный Ряд, 2, Москва'
    # estate.tags = 'Площадь 36 м2, большой туалет, 1 спальня. Вторичная мебель.'
    # estate.price = 167000
    # db_sess.add(estate)
    # db_sess.commit()
    app.run()


if __name__ == '__main__':
    main()
