import os
import pickle
import sqlite3
import pandas as pd
import numpy as np
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)  # Optional: Session expires after 30 mins
CORS(app)

# === LOGIN SETUP ===
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id_=user[0], username=user[1])
    return None

def init_user_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')

init_user_db()

# === MODEL SETUP ===
if os.path.exists("model.pkl"):
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    print("✅ Model loaded successfully!")
else:
    print("❌ model.pkl not found!")

with open("label_encoders.pkl", "rb") as le_file:
    le_dict = pickle.load(le_file)

df = pd.read_csv("final_merged_dataset (1).csv")
dropdown_values = {
    "commodities": sorted(df["Commodity"].dropna().unique()),
    "varieties": sorted(df["Variety"].dropna().unique()),
    "grades": sorted(df["Grade"].dropna().unique()),
    "districts": sorted(df["District Name"].dropna().unique()),
    "markets": sorted(df["Market Name"].dropna().unique())
}

# === ROUTES ===
@app.route("/")
def status():
    return "Commodity Price Prediction API is running!"

@app.route("/home", endpoint='home_page')
def home():
    return render_template("home.html")

@app.route("/analysis")
def analysis():
    return render_template("analysis.html", dropdowns=dropdown_values)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/sales")
@login_required
def sales():
    return render_template("sales.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                user_obj = User(id_=user[0], username=user[1])
                login_user(user_obj, remember=False)
                session.permanent = False  # Ensure session does not persist after browser closes
                return redirect(url_for('home_page'))
            else:
                flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            flash("Registration successful. Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()  # Clear session data
    flash("You have been logged out.")
    return redirect(url_for('home_page'))

@app.route("/get_options", methods=["POST"])
def get_options():
    data = request.get_json()
    option_type = data.get("type")
    value = data.get("value")

    if option_type == "commodity":
        filtered_df = df[df["Commodity"] == value]
        varieties = sorted(filtered_df["Variety"].dropna().unique().tolist())
        return jsonify({"options": varieties})

    elif option_type == "variety":
        filtered_df = df[df["Variety"] == value]
        grades = sorted(filtered_df["Grade"].dropna().unique().tolist())
        return jsonify({"options": grades})

    elif option_type == "district":
        filtered_df = df[df["District Name"] == value]
        markets = sorted(filtered_df["Market Name"].dropna().unique().tolist())
        return jsonify({"options": markets})

    return jsonify({"options": []})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    required_fields = ["Commodity", "Variety", "Grade", "District Name", "Market Name", "Price Date", "Temperature"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        data_encoded = data.copy()
        for col in ["Commodity", "Variety", "Grade", "District Name", "Market Name"]:
            data_encoded[col] = le_dict[col].transform([data[col]])[0]

        date = pd.to_datetime(data["Price Date"])
        data_encoded["year"] = date.year
        data_encoded["month"] = date.month

        model_input = np.array([[data_encoded[col] for col in [
            "District Name", "Market Name", "Commodity", "Variety", "Grade", "year", "month", "Temperature"]]])
        prediction = model.predict(model_input)[0]
        return jsonify({"Predicted Modal Price": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
