from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from models import db, User, Session, Attendance

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0585ef7ad68d55b7fd83abf82d9e93cbd3af7bfb6702710f55c4b16e3fb0a74'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.role in ['admin', 'ketua', 'pembina']:
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('dashboard_member'))
        else:
            return "Invalid credentials"
        
    return render_template('login.html')


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if not current_user.role in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    return render_template('dashboard_admin.html')

@app.route('/dashboard_member')
@login_required
def dashboard_member():
    if current_user.role in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('dashboard_admin'))
    return render_template('dashboard_member.html')

@app.route('/add-member', methods=['GET', 'POST'])
@login_required
def add_member():
    if not current_user.role in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        class_name = request.form['class_name']
        role = request.form['role']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password, name=name, class_name=class_name, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('dashboard_admin'))
    return render_template('add_member.html')

@app.route('/member-list')
@login_required
def member_list():
    users = User.query.all()
    return render_template('member_list.html', users=users)

@app.route('/create-session', methods=['GET', 'POST'])
@login_required
def create_session():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']

        new_session = Session(name=name, date=date)
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('dashboard_admin'))
    return render_template('create_session.html')

@app.route('/attendance-mark', methods=['GET', 'POST'])
@login_required
def attendance_mark():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    
    sessions = Session.query.all()
    members = User.query.filter(User.role=='member').all()

    if request.method == 'POST':
        session_id = int(request.form['session_id'])

        from datetime import datetime
        for user in members:
            status = request.form.get(f'status_{user.id}')
            if status:
                new_attendance = Attendance(
                    session_id=session_id,
                    user_id=user.id,
                    status=status,
                    timestamp=datetime.now()  
                )
                db.session.add(new_attendance)
        db.session.commit()
        return "Attendance recorded successfully"

    return render_template('attendance_mark.html', sessions=sessions, users=members)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=True)
