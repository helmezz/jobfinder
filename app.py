from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Подключение базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    birthtime = db.Column(db.Time, nullable=True)

# Функция для форматирования номера телефона
def format_phone_number(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits[0] == '8':
        digits = '7' + digits[1:]
    if len(digits) == 11:
        return f"+7({digits[1:4]}){digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    else:
        raise ValueError("Некорректный номер телефона")

# Главная страница
@app.route("/")
def home():
    return render_template("home.html")

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip()
        phone = request.form.get('phone', '').strip()
        birthdate = request.form.get('birthdate', '').strip()
        birthtime = request.form.get('birthtime', '').strip()

        if not email or not first_name or not last_name or not phone or not birthdate or not birthtime:
            flash('Все обязательные поля должны быть заполнены.')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует.')
            return redirect(url_for('register'))

        try:
            formatted_phone = format_phone_number(phone)
            birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d').date()
            birthtime_obj = datetime.strptime(birthtime, '%H:%M').time()

            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                phone=formatted_phone,
                birthdate=birthdate_obj,
                birthtime=birthtime_obj
            )
            db.session.add(new_user)
            db.session.commit()

            # Отображение благодарности
            return render_template('thanks.html')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}')
            return redirect(url_for('register'))

    return render_template('register.html')

# Обработчик ошибок
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Инициализация базы данных
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)