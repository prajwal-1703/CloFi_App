import argparse
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort

from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from sqlalchemy.exc import IntegrityError
from models import db, User, Need, Donation
from config import Config
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(Config)

# Security layers
# from flask_wtf import CSRFProtect
# from flask_wtf.csrf import generate_csrf

# csrf = CSRFProtect(app)

# @app.context_processor
# def inject_csrf_token():
#     return dict(csrf_token=generate_csrf)

bcrypt = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[Config.RATE_LIMIT_DEFAULT])
talisman = Talisman(app, content_security_policy=Config.TALISMAN_CONTENT_SECURITY_POLICY, force_https=Config.TALISMAN_FORCE_HTTPS)

# DB init
db.init_app(app)

# ---------- Utility ----------
def is_logged_in():
    return 'user_id' in session

def validate_email(email):
    # basic email sanitization (email-validator library used by WTForms if forms added)
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

# ---------- CLI ----------
@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

# allow python app.py --init-db
def init_db_via_arg():
    with app.app_context():
        db.create_all()

# ---------- Routes (Pages) ----------
@app.route("/")
def index():
    needs = Need.query.order_by(Need.created_at.desc()).limit(5).all()
    donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()
    return render_template("index.html", needs=needs, donations=donations)

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not validate_email(email):
            flash("Invalid email format.", "error")
            return redirect(url_for("register"))
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("register"))
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(email=email, password_hash=pw_hash)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered.", "error")
            return redirect(url_for("register"))
        session["user_id"] = user.id
        flash("Registration successful!", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    needs = Need.query.order_by(Need.created_at.desc()).all()
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template("dashboard.html", needs=needs, donations=donations)

@app.route("/needs", methods=["GET", "POST"])
def needs_page():
    if request.method == "POST":
        title = request.form.get("title","").strip()
        description = request.form.get("description","").strip()
        category = request.form.get("category","").strip() or "general"
        if not title or not description:
            flash("Title and description are required.", "error")
            return redirect(url_for("needs_page"))
        need = Need(title=title[:120], description=description, category=category[:50], created_by=session.get("user_id"))
        db.session.add(need)
        db.session.commit()
        flash("Need posted.", "success")
        return redirect(url_for("needs_page"))
    needs = Need.query.order_by(Need.created_at.desc()).all()
    return render_template("needs.html", needs=needs)

@app.route("/donate", methods=["GET", "POST"])
def donate_page():
    if request.method == "POST":
        donor_name = request.form.get("donor_name","").strip() or "Anonymous"
        item = request.form.get("item","").strip()
        quantity = int(request.form.get("quantity","1") or 1)
        notes = request.form.get("notes","").strip() or None
        need_id = request.form.get("need_id")
        if not item:
            flash("Item is required.", "error")
            return redirect(url_for("donate_page"))
        donation = Donation(donor_name=donor_name[:120], item=item[:120], quantity=max(1, quantity), notes=notes, need_id=int(need_id) if need_id else None)
        db.session.add(donation)
        db.session.commit()
        flash("Thank you for donating!", "success")
        return redirect(url_for("donate_page"))
    needs = Need.query.order_by(Need.created_at.desc()).all()
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template("donate.html", needs=needs, donations=donations)

# ---------- JSON API (CSRF-protected for unsafe methods) ----------
@app.get("/api/needs")
def api_get_needs():
    needs = Need.query.order_by(Need.created_at.desc()).all()
    return jsonify([{"id": n.id, "title": n.title, "description": n.description, "category": n.category, "created_at": n.created_at.isoformat()} for n in needs])

@app.post("/api/needs")
@limiter.limit("50 per hour")
def api_post_need():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "general").strip()
    if not title or not description:
        return jsonify({"error": "title and description required"}), 400
    need = Need(title=title[:120], description=description, category=category[:50], created_by=session.get("user_id"))
    db.session.add(need)
    db.session.commit()
    return jsonify({"id": need.id}), 201

@app.get("/api/donations")
def api_get_donations():
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return jsonify([{"id": d.id, "donor_name": d.donor_name, "item": d.item, "quantity": d.quantity, "created_at": d.created_at.isoformat(), "need_id": d.need_id} for d in donations])

@app.post("/api/donations")
@limiter.limit("50 per hour")
def api_post_donation():
    data = request.get_json(silent=True) or {}
    donor_name = (data.get("donor_name") or "Anonymous").strip()
    item = (data.get("item") or "").strip()
    quantity = int(data.get("quantity") or 1)
    notes = (data.get("notes") or None)
    need_id = data.get("need_id")
    if not item:
        return jsonify({"error": "item required"}), 400
    donation = Donation(donor_name=donor_name[:120], item=item[:120], quantity=max(1, quantity), notes=notes, need_id=int(need_id) if need_id else None)
    db.session.add(donation)
    db.session.commit()
    return jsonify({"id": donation.id}), 201

# Error handlers (avoid leaking internals)
# @app.errorhandler(400)
# @app.errorhandler(401)
# @app.errorhandler(403)
# @app.errorhandler(404)
# @app.errorhandler(429)
# @app.errorhandler(500)
# def handle_errors(err):
#     code = getattr(err, "code", 500)
#     return render_template("error.html", code=code), code

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()
    if args.init_db:
        init_db_via_arg()
    else:
        app.run(host="0.0.0.0", port=5000)
