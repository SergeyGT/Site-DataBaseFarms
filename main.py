from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from config import host, user, password, db_name
from datetime import datetime
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7891230456A&s@127.0.0.1/farm'
app.config['SECRET_KEY'] = '2411'
db = SQLAlchemy(app)

# Класс для таблицы персонала
class Personal(db.Model):
    __tablename__ = 'personal'
    idpersonal = db.Column(db.Integer, primary_key=True)
    idfarms = db.Column(db.Integer, db.ForeignKey('farms.idfarms'), nullable=False)
    fio = db.Column(db.String(100), nullable=False)
    work_time = db.Column(db.DateTime, default=datetime.utcnow())
    post = db.Column(db.String(40), nullable=False)

    farm = db.relationship('Farms', back_populates='personal_list')

    def __repr__(self):
        return f'<Personal {self.fio}>'


class Farms(db.Model):
    __tablename__ = 'farms'
    idfarms = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50), nullable=False)
    personal_list = db.relationship('Personal', back_populates='farm', lazy=True)

    def __repr__(self):
        return f'<Farms {self.location}>'




@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/personal')
def show_personal():
    personal_list = Personal.query.all()
    return render_template('personal.html', personal_list=personal_list)


@app.route('/personal/<int:idperson>')
def del_personal(idperson):
    person = Personal.query.get_or_404(idperson)
    try:
        db.session.delete(person)
        db.session.commit()
        flash("Работник успешно удален", "success")
        return redirect('/personal')
    except:
        flash(f"При добавлении города возникла ошибка:", "danger")
        return redirect('/home')


@app.route('/info_farms', methods=['POST', 'GET'])
def info_farms():
    if request.method == "POST":
        location = request.form['location']

        farms = Farms(location=location)

        try:
            db.session.add(farms)
            db.session.commit()
            flash("Город был добавлен успешно", "success")
            return redirect('/info_farms')
        except Exception as e:
            db.session.rollback()
            flash(f"При добавлении города возникла ошибка: {str(e)}", "danger")
            return redirect('/home')
    else:
        farms = Farms.query.all()
        return render_template("farms.html", farms=farms)


@app.route('/all_farms')
def show_all_farms():
    all_farms = Farms.query.all()
    return render_template("all_farms.html", all_farms=all_farms)


@app.route('/all_farms/<int:idfarm>', methods=['POST', 'GET'])
def del_farms(idfarm):
    del_farm = Farms.query.get(idfarm)
    if request.method == "POST":
        if(request.form['location'] == del_farm.location):
            flash("Город не изменился", "danger")
            return redirect("/all_farms")
        else:
            del_farm.location = request.form['location']

            try:
                db.session.commit()
                flash("Город был изменен успешно", "success")
                return redirect("/all_farms")
            except Exception as e:
                db.session.rollback()
                flash(f"Переход на главную старницк. При изменении города возникла ошибка: {str(e)}... ", "danger")
                return redirect('/home')
    else:

        return render_template("change_farm.html", del_farm=del_farm)


@app.route('/filter_personal', methods=['GET'])
def filter_personal():
    city = request.args.get('city')
    if city:
        personal_list = Personal.query.join(Farms).filter(Farms.location == city).all()
    else:
        personal_list = Personal.query.all()
    return render_template('personal.html', personal_list=personal_list)


@app.route('/farms_worker_count')
def farms_worker_count():
    farms = Farms.query.all()
    farm_worker_counts = {farm.location: len(farm.personal_list) for farm in farms}
    return render_template('farms_worker_count.html', farm_worker_counts=farm_worker_counts)

if __name__ == "__main__":
    app.run()
