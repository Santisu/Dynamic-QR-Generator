import os
import shortuuid
import uuid
import qrcode
from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, and_, desc
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = "mN8sHrCqDwYfZ2P7Tt6WkKvJ9bXjLgA4"
# Cambia la URL de la base de datos si es necesario
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrcodes.db'
# Evita que SQLAlchemy emita advertencias
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.static_folder = 'static'


class QR(db.Model):
    __tablename__ = 'qr'
    qr_id = Column(Integer, primary_key=True)
    short_url = Column(String(45), unique=True, nullable=True)
    path = Column(String(45), unique=True, nullable=True)
    qr_image = Column(String(45), nullable=True)
    password = Column(String(45), nullable=True)
    info = relationship('Info', back_populates='qr')


class Info(db.Model):
    __tablename__ = 'info'
    info_id = Column(Integer, primary_key=True)
    qr_id = Column(Integer, ForeignKey('qr.qr_id'), nullable=False)
    original_url = Column(String(500), nullable=False)
    number_opened = Column(Integer, nullable=False)
    current_link = Column(Integer, nullable=False)
    qr = relationship('QR', back_populates='info')

# UTILS ########################################################


bcrypt = Bcrypt(app)


def short_path():
    short_path = shortuuid.encode(uuid.uuid4())
    short_path = short_path[:6]
    return short_path


def create_qr(enlace: str, unique_path):
    static_folder = 'static/qr_codes'
    folder_path = os.path.join(os.getcwd(), static_folder)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = f"qr_{unique_path}.png"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(enlace)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(static_folder, filename)
    qr_img.save(qr_path)

    return qr_path


##################################################################

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate', methods=["GET", "POST"])
def generate():
    if request.method == "POST":
        original_url = request.form.get("original_url")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if not original_url:
            message = {"m_url": "You must insert a valid text"}
            return render_template("generate.html", message=message)
        # Ensure password was submitted
        elif not password1:
            message = {"m_pass": "You must provide a valid password"}
            return render_template("generate.html", message=message)
        if password1 != password2:
            message = {"m_match": "Passwords don't match"}
            return render_template("generate.html", message=message)

        else:
            hashed_password = bcrypt.generate_password_hash(
                password1).decode('utf-8')
            base_domain = request.host
            unique = False
            while not unique:
                path = short_path()
                final_path = f'http://{base_domain}/{path}'
                existing_qr = QR.query.filter_by(short_url=final_path).first()
                if existing_qr is None:
                    unique = True
            qr_path = create_qr(final_path, path)
            qr = QR(short_url=final_path, path=path,
                    qr_image=qr_path, password=hashed_password)
            db.session.add(qr)
            db.session.flush()
            info = Info(qr_id=qr.qr_id, original_url=original_url,
                        number_opened=0, current_link=1)
            db.session.add(info)
            db.session.commit()
            session['qr_short_url'] = qr.path
            return redirect("/info")
    else:
        return render_template("generate.html")


@app.route('/get-info', methods=["GET", "POST"])
def get_info():
    if request.method == "POST":
        path = request.form.get("path")
        password = request.form.get("password")
        if not path:
            message = {"m_url": "You must insert a valid path"}
            return render_template("get_info.html", message=message)
        elif not password:
            message = {"m_pass": "You must provide a valid password"}
            return render_template("get_info.html", message=message)
        else:
            existing_qr = QR.query.filter_by(path=path).first()

            if existing_qr is not None:
                if bcrypt.check_password_hash(existing_qr.password, password):
                    session['qr_short_url'] = existing_qr.path
                    return redirect('/info')
            else:
                message = {"m_match": "Invalid path or password"}
            return render_template("get_info.html", message=message)

    else:
        return render_template("get_info.html")


@app.route('/info', methods=["GET", "POST"])
def info():
    if 'qr_short_url' in session:
        qr_short_url = session['qr_short_url']
        qr = QR.query.filter_by(path=qr_short_url).first()
        if qr:
            qr_info = Info.query.filter_by(qr_id=qr.qr_id).order_by(
                desc(Info.current_link)).all()
            if qr_info:
                if request.method == "POST":
                    path = request.form.get("path")
                    new_url = request.form.get("new_url")
                    password = request.form.get("password")
                    if not new_url:
                        message = {"m_url": "You must insert a valid url"}
                        return render_template("info.html", qr_info=qr_info, qr=qr, message=message)
                    qr = QR.query.filter_by(path=path).first()
                    if qr is not None:
                        if bcrypt.check_password_hash(qr.password, password):
                            Info.query.filter_by(qr_id=qr.qr_id).update(
                                {'current_link': 0})
                            existing_info = Info.query.filter(
                                and_(Info.qr_id == qr.qr_id, Info.original_url == new_url)).first()
                            if existing_info:
                                existing_info.current_link = 1
                            else:
                                info = Info(
                                    qr_id=qr.qr_id, original_url=new_url, number_opened=0, current_link=1)
                                db.session.add(info)
                            db.session.commit()
                        else:
                            message = {"m_pass": "Incorrect password"}
                            return render_template("info.html", qr_info=qr_info, qr=qr, message=message)
                    return redirect('/info')
                else:
                    return render_template("info.html", qr_info=qr_info, qr=qr)
    return redirect(url_for('index'))


@app.route('/<custom_url>')
def dynamic_redirect(custom_url):
    print(custom_url)
    qr = QR.query.filter(QR.path == custom_url).first()
    if qr:
        redirect_url = Info.query.filter(
            and_(Info.qr_id == qr.qr_id, Info.current_link == 1)).first()
        if redirect_url is not None:
            redirect_url.number_opened += 1
            db.session.commit()
            return redirect(redirect_url.original_url)
    abort(404)


@app.route('/clear-session')
def clear_session():
    if 'qr_short_url' in session:
        del session['qr_short_url']
    return redirect('/')


@app.route('/current-session')
def current_session():
    if 'qr_short_url' in session:
        return redirect('/info')
    else:
        return redirect('/get-info')


if __name__ == '__main__':
    app.run(debug=True)
