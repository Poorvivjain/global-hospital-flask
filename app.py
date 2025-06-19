from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    timing = db.Column(db.String(100))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100))
    doctor_name = db.Column(db.String(100))
    appointment_date = db.Column(db.String(100))

@app.before_first_request
def init_db():
    db.create_all()
    if Doctor.query.count() == 0:
        db.session.add_all([
            Doctor(name="Dr. Aarti Sharma", specialization="Cardiology", timing="10:00 AM - 1:00 PM"),
            Doctor(name="Dr. Nikhil Verma", specialization="Neurology", timing="2:00 PM - 5:00 PM"),
            Doctor(name="Dr. Priya Mehta", specialization="Orthopedics", timing="11:00 AM - 2:00 PM")
        ])
        db.session.commit()

@app.route("/")
def home(): return render_template("index.html")

@app.route("/login")
def login(): return render_template("login.html")

@app.route("/register")
def register(): return render_template("register.html")

@app.route("/doctor")
def doctor(): return render_template("doctor.html")

@app.route("/appointment")
def appointment(): return render_template("appointment.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "User exists"}), 400
    db.session.add(User(username=data["username"], password=data["password"]))
    db.session.commit()
    return jsonify({"message": "Registered"})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    return jsonify({"message": "Success" if user else "Invalid"}), 200 if user else 401

@app.route("/api/doctors", methods=["GET", "POST"])
def api_doctors():
    if request.method == "POST":
        data = request.get_json()
        db.session.add(Doctor(**data))
        db.session.commit()
        return jsonify({"message": "Doctor added"})
    return jsonify([{ "name": d.name, "specialization": d.specialization, "timing": d.timing } for d in Doctor.query.all()])

@app.route("/api/appointments", methods=["GET", "POST"])
def api_appointments():
    if request.method == "POST":
        data = request.get_json()
        db.session.add(Appointment(**data))
        db.session.commit()
        return jsonify({"message": "Booked"})
    return jsonify([{ "patient_name": a.patient_name, "doctor_name": a.doctor_name, "appointment_date": a.appointment_date } for a in Appointment.query.all()])

if __name__ == "__main__":
    app.run(debug=True)
