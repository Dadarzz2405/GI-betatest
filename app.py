from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from models import db, User, Session, Attendance
from datetime import datetime, date
from ummalqura.hijri_date import HijriDate
import json
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
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.must_change_password:
                return redirect(url_for('profile'))
            else:
                if user.role in ['admin', 'ketua', 'pembina']:
                    return redirect(url_for('dashboard_admin'))
                else:
                    return redirect(url_for('dashboard_member'))
        else:
            flash('Invalid email or password', 'error')
        
    return render_template('login.html')


@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role in ['admin', 'ketua', 'pembina']:
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_member'))
    else:
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

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken', 'error')
            return redirect(url_for('profile')) 

        current_user.username = username
        
        if password: 
            current_user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

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
        return redirect(url_for('invalid_credential'))
    
    sessions = Session.query.all()
    members = User.query.filter_by(role='member').all()  

    if request.method == 'POST':
        try:
            session_id = int(request.form['session_id'])
            
            from datetime import datetime
            for user in members:
                status = request.form.get(f'status_{user.id}')
                if status in ['present', 'absent', 'excused']: 
                    existing_attendance = Attendance.query.filter_by(
                        session_id=session_id, 
                        user_id=user.id
                    ).first()
                    
                    if existing_attendance:
                        existing_attendance.status = status
                    else:
                        new_attendance = Attendance(
                            session_id=session_id,
                            user_id=user.id,
                            status=status,
                            timestamp=datetime.now()
                        )
                        db.session.add(new_attendance)
            
            db.session.commit()
            flash("Attendance recorded successfully", "success")
            return redirect(url_for('attendance_mark'))
        except (ValueError, TypeError):
            flash("Invalid session selected", "error")
    
    return render_template('attendance_mark.html', sessions=sessions, users=members)

@app.route('/attendance-history')
@login_required
def attendance_history():

    records = db.session.query(
        Attendance,
        Session.name.label('session_name'),
        Session.date.label('session_date')
    ).join(Session, Attendance.session_id == Session.id)\
     .filter(Attendance.user_id == current_user.id).all()

    summary = {
        'present': sum(1 for r, _, _ in records if r.status=='present'),
        'absent': sum(1 for r, _, _ in records if r.status=='absent'),
        'excused': sum(1 for r, _, _ in records if r.status=='excused')
    }

    return render_template('attendance_history.html', records=records, summary=summary)

@app.route('/attendance-history-admin')
@login_required
def attendance_history_admin():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('invalid_credential')) 
    users = User.query.filter(User.role=='member').all()
    return render_template('attendance_history_admin.html', users=users)

@app.route('/attendance-history-admin/<int:user_id>')
@login_required
def attendance_history_admin_view(user_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('invalid_credential'))
    
    selected_user = User.query.get_or_404(user_id)

    records = db.session.query(
        Attendance,
        Session.name.label('session_name'),
        Session.date.label('session_date')
    ).join(Session, Attendance.session_id == Session.id)\
     .filter(Attendance.user_id == user_id).all()
    
    summary = {
        'present': sum(1 for r, _, _ in records if r.status=='present'),
        'absent': sum(1 for r, _, _ in records if r.status=='absent'),
        'excused': sum(1 for r, _, _ in records if r.status=='excused')
    }
    return render_template('attendance_history_admin_view.html', user=selected_user, records=records, summary=summary)

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash("Incorrect current password.", "danger")
        elif new_password != confirm_password:
            flash("New passwords don't match.", "danger")
        else:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.must_change_password = False
            db.session.commit()
            flash("Password updated successfully!", "success")
            if current_user.role in ['admin', 'ketua', 'pembina']:
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('dashboard_member'))
    return render_template('change_password.html')

ISLAMIC_HOLIDAYS = {
    # Muharram
    "01-01": "Islamic New Year (1 Muharram)",
    "01-09": "Day of Tasua",
    "01-10": "Day of Ashura",

    # Rabi' al-Awwal
    "03-12": "Mawlid al-Nabi (Prophet Muhammad's Birthday)",

    # Rajab
    "07-01": "Start of Rajab",
    "07-27": "Isra and Mi'raj",

    # Sha'ban
    "08-15": "Mid-Sha'ban (Laylat al-Bara'ah)",

    # Ramadan
    "09-01": "Start of Ramadan",
    "09-17": "Nuzul al-Qur'an",
    "09-21": "Laylat al-Qadr (possible)",
    "09-23": "Laylat al-Qadr (possible)",
    "09-25": "Laylat al-Qadr (possible)",
    "09-27": "Laylat al-Qadr (most observed)",
    "09-29": "Laylat al-Qadr (possible)",

    # Shawwal
    "10-01": "Eid al-Fitr",
    "10-02": "Eid al-Fitr (2nd day – some regions)",

    # Dhu al-Qi'dah
    "11-01": "Start of Dhu al-Qi'dah",

    # Dhu al-Hijjah
    "12-01": "Start of Dhu al-Hijjah",
    "12-08": "Day of Tarwiyah",
    "12-09": "Day of Arafah",
    "12-10": "Eid al-Adha",
    "12-11": "Days of Tashreeq",
    "12-12": "Days of Tashreeq",
    "12-13": "Days of Tashreeq",
}

def get_hijri_date(gregorian_date):
    try:
        g_date = datetime.strptime(gregorian_date, "%Y-%m-%d")
        h_date = HijriDate.from_gregorian(g_date.year, g_date.month, g_date.day, gr=True)
        return f"{h_date.day} {h_date.month_name()} {h_date.year} H"
    except ValueError:
        return "Invalid date"
    
@app.route('/api/dashboard_calendar')
@login_required
def api_dashboard_calendar():
    sessions = Session.query.all()
    calendar_events = []

    for session in sessions:
        hijri_date = get_hijri_date(session.date)
        title = f"{session.name} ({hijri_date})"
        calendar_events.append({
            'title': title,
            'start': session.date,
            'extendedProps': {
                'description' : getattr(session, 'description', ''),
                'type': 'rohis_session'
            }
        })

    today = date.today()
    year = today.year
    for date_str, holiday_name in ISLAMIC_HOLIDAYS.items():
        full_date = f"{year}-{date_str}"
        try:
            hijri_date = get_hijri_date(full_date)
            title = f"{holiday_name} ({hijri_date})"
            calendar_events.append({
                'title': title,
                'start': full_date,
                'backgroundColor': '#4CAF50',
                'borderColor': '#4CAF50',
                'textColor': 'white',
                'extendedProps': {
                    'description': holiday_name,
                    'type': 'islamic_holiday'
                }
            })    
        except ValueError:
            continue

        next_year = year + 1
        next_full_date = f"{next_year}-{date_str}"
        try:
            next_hijri_date = get_hijri_date(next_full_date)
            title = f"{holiday_name} ({next_full_date}/{next_hijri_date})"
            calendar_events.append({
                'title': title,
                'start': next_full_date,
                'backgroundColor': '#4CAF50',
                'borderColor': '#4CAF50',
                'textColor': 'white',
                'extendedProps': {
                    'description': holiday_name,
                    'type': 'islamic_holiday'
                }
            })
        except ValueError:
            continue

    return {'events': calendar_events}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=True)