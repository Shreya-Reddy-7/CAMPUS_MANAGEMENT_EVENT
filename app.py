from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, desc
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret-demo-key"  # change in prod
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=8)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ==========================
# MODELS
# ==========================
class College(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

class User(db.Model):
    # For authentication (admins + students)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=True)
    # if role == 'student', link to Student row

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    college = db.relationship("College", backref="students")

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    type = db.Column(db.String(50))
    capacity = db.Column(db.Integer, default=50)
    is_cancelled = db.Column(db.Boolean, default=False)
    college_id = db.Column(db.Integer, db.ForeignKey("college.id"))
    college = db.relationship("College", backref="events")

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    student = db.relationship("Student", backref="registrations")
    event = db.relationship("Event", backref="registrations")

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    rating = db.Column(db.Integer)
    comments = db.Column(db.String(300))

# ==========================
# DB SETUP (seed)
# ==========================
def ensure_db():
    with app.app_context():
        db.create_all()
        if not College.query.first():
            c = College(name="Acharya Institute")
            db.session.add(c)
            db.session.commit()

            # students
            s1 = Student(name="Alice", college=c)
            s2 = Student(name="Bob", college=c)
            db.session.add_all([s1, s2])
            db.session.commit()

            # events
            e1 = Event(title="AI Workshop", type="Workshop", capacity=100, college=c)
            e2 = Event(title="HackWithInfy", type="Hackathon", capacity=200, college=c)
            db.session.add_all([e1, e2])
            db.session.commit()

            # create user accounts (admin + students)
            admin_user = User(email="admin@demo", role="admin")
            admin_user.set_password("adminpass")
            db.session.add(admin_user)

            user_a = User(email="alice@demo", role="student", student_id=s1.id)
            user_a.set_password("alicepass")
            user_b = User(email="bob@demo", role="student", student_id=s2.id)
            user_b.set_password("bobpass")
            db.session.add_all([user_a, user_b])
            db.session.commit()

# ==========================
# HELPERS
# ==========================
def json_success(data=None, message=None):
    resp = {"success": True}
    if data is not None:
        resp["data"] = data
    if message:
        resp["message"] = message
    return jsonify(resp)

def json_error(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

def role_required(role):
    # decorator-like helper inside function endpoints
    def inner_check():
        claims = get_jwt()
        return claims.get("role") == role
    return inner_check

# ==========================
# AUTH (register/login)
# ==========================
@app.route("/auth/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")
    name = data.get("name")

    if not email or not password:
        return json_error("email and password are required", 400)

    if User.query.filter_by(email=email).first():
        return json_error("email already registered", 400)

    user = User(email=email, role=role)
    user.set_password(password)

    if role == "student":
        # create student row
        college_id = data.get("college_id") or 1
        student = Student(name=name or email.split("@")[0], college_id=college_id)
        db.session.add(student)
        db.session.commit()
        user.student_id = student.id

    db.session.add(user)
    db.session.commit()
    return json_success(message="registered")

@app.route("/auth/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return json_error("email and password required", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return json_error("invalid credentials", 401)

    additional_claims = {"role": user.role, "user_id": user.id}
    if user.role == "student":
        additional_claims["student_id"] = user.student_id

    token = create_access_token(identity=user.email, additional_claims=additional_claims)
    return json_success(data={"access_token": token, "role": user.role, "student_id": user.student_id})

# ==========================
# ROUTES (public + protected)
# ==========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin_portal():
    return render_template("admin.html")

@app.route("/student")
def student_portal():
    return render_template("student.html")

@app.route("/events", methods=["GET"])
def list_events():
    events = Event.query.all()
    out = []
    for e in events:
        out.append({
            "id": e.id,
            "title": e.title,
            "type": e.type,
            "capacity": e.capacity,
            "is_cancelled": e.is_cancelled,
            "registrations": len(e.registrations),
            "attendance_count": Attendance.query.filter_by(event_id=e.id).count()
        })
    return json_success(data=out)

@app.route("/events", methods=["POST"])
@jwt_required()
def create_event():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return json_error("admin only", 403)
    data = request.get_json() or {}
    title = data.get("title")
    etype = data.get("type")
    cap = data.get("capacity", 50)
    college_id = data.get("college_id", 1)
    if not title or not etype:
        return json_error("title and type required", 400)
    ev = Event(title=title, type=etype, capacity=cap, college_id=college_id)
    db.session.add(ev)
    db.session.commit()
    return json_success(data={"event_id": ev.id}, message="event created")

@app.route("/events/<int:event_id>/register", methods=["POST"])
@jwt_required()
def register_event(event_id):
    claims = get_jwt()
    # allow student or admin to register (admin may register on behalf)
    data = request.get_json() or {}
    student_id = data.get("student_id")
    if claims.get("role") == "student" and not student_id:
        # logged in student registers self
        student_id = claims.get("student_id")
    if not student_id:
        return json_error("student_id required", 400)

    ev = Event.query.get_or_404(event_id)
    if ev.is_cancelled:
        return json_error("event cancelled", 400)
    if Registration.query.filter_by(student_id=student_id, event_id=event_id).first():
        return json_error("already registered", 400)
    if len(ev.registrations) >= ev.capacity:
        return json_error("event full", 400)

    reg = Registration(student_id=student_id, event_id=event_id)
    db.session.add(reg)
    db.session.commit()
    return json_success(data={"registration_id": reg.id}, message="registered")

@app.route("/events/<int:event_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_event(event_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return json_error("admin only", 403)
    ev = Event.query.get_or_404(event_id)
    if ev.is_cancelled:
        return json_error("already cancelled", 400)
    ev.is_cancelled = True
    db.session.commit()
    return json_success(message="cancelled")

@app.route("/attendance", methods=["POST"])
@jwt_required()
def mark_attendance():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    event_id = data.get("event_id")
    if not student_id or not event_id:
        return json_error("student_id and event_id required", 400)
    # ensure registration exists
    if not Registration.query.filter_by(student_id=student_id, event_id=event_id).first():
        return json_error("not registered", 400)
    if Attendance.query.filter_by(student_id=student_id, event_id=event_id).first():
        return json_error("attendance already marked", 400)
    att = Attendance(student_id=student_id, event_id=event_id)
    db.session.add(att)
    db.session.commit()
    return json_success(data={"attendance_id": att.id}, message="attendance marked")

@app.route("/feedback", methods=["POST"])
@jwt_required()
def give_feedback():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    event_id = data.get("event_id")
    rating = data.get("rating")
    comments = data.get("comments", "")
    if None in (student_id, event_id, rating):
        return json_error("student_id, event_id, rating required", 400)
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return json_error("rating must be 1-5", 400)
    fb = Feedback(student_id=student_id, event_id=event_id, rating=rating, comments=comments)
    db.session.add(fb)
    db.session.commit()
    return json_success(data={"feedback_id": fb.id}, message="feedback submitted")

# -----------------------
# REPORTS
# -----------------------
@app.route("/reports/event_popularity", methods=["GET"])
@jwt_required(optional=True)
def event_popularity():
    college_id = request.args.get("college_id", type=int)
    q = db.session.query(
        Event.id.label("event_id"),
        Event.title,
        Event.type,
        func.count(Registration.id).label("registrations")
    ).outerjoin(Registration).group_by(Event.id)
    if college_id:
        q = q.filter(Event.college_id == college_id)
    q = q.order_by(desc("registrations"))
    results = q.all()
    data = [{"event_id": r.event_id, "title": r.title, "type": r.type, "registrations": r.registrations} for r in results]
    return json_success(data=data)

@app.route("/reports/top_active_students", methods=["GET"])
@jwt_required(optional=True)
def top_active_students():
    college_id = request.args.get("college_id", type=int)
    limit = request.args.get("limit", type=int, default=5)
    q = db.session.query(
        Student.id.label("student_id"),
        Student.name,
        func.count(Registration.id).label("events_attended")
    ).join(Registration, Registration.student_id == Student.id
    ).join(Event, Registration.event_id == Event.id
    ).group_by(Student.id).order_by(desc("events_attended"))
    if college_id:
        q = q.filter(Student.college_id == college_id)
    results = q.limit(limit).all()
    data = [{"student_id": r.student_id, "name": r.name, "events_attended": r.events_attended} for r in results]
    return json_success(data=data)

@app.route("/reports/average_feedback", methods=["GET"])
@jwt_required(optional=True)
def average_feedback():
    college_id = request.args.get("college_id", type=int)
    q = db.session.query(
        Event.id.label("event_id"),
        Event.title,
        func.avg(Feedback.rating).label("average_rating"),
        func.count(Feedback.id).label("feedback_count")
    ).outerjoin(Feedback).group_by(Event.id)
    if college_id:
        q = q.filter(Event.college_id == college_id)
    results = q.all()
    data = []
    for r in results:
        avg = float(r.average_rating) if r.average_rating is not None else None
        data.append({"event_id": r.event_id, "title": r.title, "average_rating": avg, "feedback_count": r.feedback_count})
    return json_success(data=data)

@app.route("/reports/top_events_feedback", methods=["GET"])
@jwt_required(optional=True)
def top_events_feedback():
    college_id = request.args.get("college_id", type=int)
    limit = request.args.get("limit", type=int, default=3)
    q = db.session.query(
        Event.id.label("event_id"),
        Event.title,
        func.avg(Feedback.rating).label("average_rating"),
        func.count(Feedback.id).label("feedback_count")
    ).outerjoin(Feedback).group_by(Event.id).order_by(desc("average_rating"))
    if college_id:
        q = q.filter(Event.college_id == college_id)
    results = q.limit(limit).all()
    data = []
    for r in results:
        avg = float(r.average_rating) if r.average_rating is not None else None
        data.append({"event_id": r.event_id, "title": r.title, "average_rating": avg, "feedback_count": r.feedback_count})
    return json_success(data=data)

@app.route("/reports/inactive_students", methods=["GET"])
@jwt_required(optional=True)
def inactive_students():
    college_id = request.args.get("college_id", type=int)
    sub = db.session.query(Registration.student_id).distinct()
    q = Student.query.filter(~Student.id.in_(sub))
    if college_id:
        q = q.filter(Student.college_id == college_id)
    results = q.all()
    data = [{"student_id": s.id, "name": s.name} for s in results]
    return json_success(data=data)

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    ensure_db()
    app.run(debug=True)
