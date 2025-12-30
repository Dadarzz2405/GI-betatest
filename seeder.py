from app import app, db
from models import User
from flask_bcrypt import Bcrypt  # Import bcrypt here

bcrypt = Bcrypt(app)  # Initialize bcrypt

INITIAL_PASSWORD = "rohis2025"


members = [
    {"email": "muhammad.syathir@gdajogja.sch.id", "name": "Muhammad Syathir", "class": "X IPA 1", "role": "member"},
    {"email": "aiesha.makaila@gdajogja.sch.id", "name": "Aiesha Makaila", "class": "X IPA 2", "role": "member"},
    {"email": "aisyah.putri@gdajogja.sch.id", "name": "Aisyah Putri", "class": "X IPA 3", "role": "member"},
    {"email": "aqillah.hasanah@gdajogja.sch.id", "name": "Aqillah Hasanah", "class": "X IPA 1", "role": "member"},
    {"email": "arya.rahadian@gdajogja.sch.id", "name": "Arya Rahadian", "class": "X IPA 2", "role": "member"},
    {"email": "atthahirah.tsania@gdajogja.sch.id", "name": "Atthahirah Tsania", "class": "X IPA 3", "role": "member"},
    {"email": "aulia.meilinda@gdajogja.sch.id", "name": "Aulia Meilinda", "class": "X IPA 1", "role": "member"},
    {"email": "devone.nalandra@gdajogja.sch.id", "name": "Devone Nalandra", "class": "X IPA 2", "role": "member"},
    {"email": "dzakya.prasetya@gdajogja.sch.id", "name": "Dzakya Prasetya", "class": "X IPA 3", "role": "member"},
    {"email": "evan.farizqi@gdajogja.sch.id", "name": "Evan Farizqi", "class": "X IPA 1", "role": "member"},
    {"email": "faiq.asyam@gdajogja.sch.id", "name": "Faiq Asyam", "class": "X IPA 2", "role": "member"},
    {"email": "ghozy.suciawan@gdajogja.sch.id", "name": "Ghozy Suciawan", "class": "XI IPA 1", "role": "ketua"},
    {"email": "hadiqoh.aini@gdajogja.sch.id", "name": "Hadiqoh Aini", "class": "X IPA 3", "role": "member"},
    {"email": "haidar.nasirodin@gdajogja.sch.id", "name": "Haidar Nasirodin", "class": "XII IPA 1", "role": "admin"},  
    {"email": "hammam.prasetyo@gdajogja.sch.id", "name": "Hammam Prasetyo", "class": "X IPA 1", "role": "member"},
    {"email": "husein.syamil@gdajogja.sch.id", "name": "Husein Syamil", "class": "X IPA 2", "role": "member"},
    {"email": "intahani.sani@gdajogja.sch.id", "name": "Intahani Sani", "class": "X IPA 3", "role": "member"},
    {"email": "irfan.ansari@gdajogja.sch.id", "name": "Irfan Ansari", "class": "X IPA 1", "role": "member"},
    {"email": "jinan.muntaha@gdajogja.sch.id", "name": "Jinan Muntaha", "class": "X IPA 2", "role": "member"},
    {"email": "kemas.tamada@gdajogja.sch.id", "name": "Kemas Tamada", "class": "X IPA 3", "role": "member"},
    {"email": "khoirun.istiqomah@gdajogja.sch.id", "name": "Khoirun Istiqomah", "class": "X IPA 1", "role": "member"},
    {"email": "mufadilla.legisa@gdajogja.sch.id", "name": "Mufadilla Legisa", "class": "X IPA 2", "role": "member"},
    {"email": "muhammad.ismoyo@gdajogja.sch.id", "name": "Muhammad Ismoyo", "class": "X IPA 3", "role": "member"},
    {"email": "nabila.patricia@gdajogja.sch.id", "name": "Nabila Patricia", "class": "X IPA 1", "role": "member"},
    {"email": "nabilah.putri@gdajogja.sch.id", "name": "Nabilah Putri", "class": "X IPA 2", "role": "member"},
    {"email": "naufal.syuja@gdajogja.sch.id", "name": "Naufal Syuja", "class": "X IPA 3", "role": "member"},
    {"email": "rauf.akmal@gdajogja.sch.id", "name": "Rauf Akmal", "class": "X IPA 1", "role": "member"},
    {"email": "rifqy.daaris@gdajogja.sch.id", "name": "Rifqy Daaris", "class": "X IPA 2", "role": "member"},
    {"email": "tengku.harahap@gdajogja.sch.id", "name": "Tengku Harahap", "class": "X IPA 3", "role": "member"},
    {"email": "zahra.layla@gdajogja.sch.id", "name": "Zahra Layla", "class": "X IPA 1", "role": "member"},
    {"email": "zalfa.zahira@gdajogja.sch.id", "name": "Zalfa Zahira", "class": "X IPA 2", "role": "member"}
]

with app.app_context():
    for m in members:
        hashed_pw = bcrypt.generate_password_hash(INITIAL_PASSWORD).decode('utf-8')  # ✅ Correct way
        user = User(
            email=m["email"],
            password=hashed_pw,
            name=m["name"],
            class_name=m["class"],
            role=m["role"],
            must_change_password=True
        )
        db.session.add(user)
    db.session.commit()

print("✅ All members added with valid passwords!")