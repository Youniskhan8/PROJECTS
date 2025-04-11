import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, make_response
from flask_cors import CORS
from functools import wraps

# Initialize Flask app with static/template folders
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key'
CORS(app)

# 🚫 Disable caching to prevent back-button access after logout
def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response
    return no_cache_view

# ✅ Load model
if os.path.exists("model.pkl"):
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    print("✅ Model loaded successfully!")
else:
    print("❌ model.pkl not found!")

# ✅ Load label encoders
if os.path.exists("label_encoders.pkl"):
    with open("label_encoders.pkl", "rb") as le_file:
        le_dict = pickle.load(le_file)
    print("✅ Label encoders loaded!")
else:
    le_dict = {}
    print("❌ label_encoders.pkl not found!")

# ✅ Load dropdown data
if os.path.exists("final_merged_dataset (1).csv"):
    df = pd.read_csv("final_merged_dataset (1).csv")
    dropdown_values = {
        "commodities": sorted(df["Commodity"].dropna().unique()),
        "varieties": sorted(df["Variety"].dropna().unique()),
        "grades": sorted(df["Grade"].dropna().unique()),
        "districts": sorted(df["District Name"].dropna().unique()),
        "markets": sorted(df["Market Name"].dropna().unique())
    }
else:
    dropdown_values = {"commodities": [], "varieties": [], "grades": [], "districts": [], "markets": []}
    print("❌ Dataset file not found!")

# 🏠 Root redirects to login
@app.route("/")
def root():
    return redirect(url_for('login'))

# 🔐 Home page
@app.route("/home")
@nocache
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("home.html")

# 🔑 Login route
@app.route("/login", methods=["GET", "POST"])
@nocache
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# 🚪 Logout and clear session
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# 📊 Analysis page
@app.route("/analysis")
@nocache
def analysis():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("analysis.html", dropdowns=dropdown_values)

# 🤖 Prediction API
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

# 🚀 Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
