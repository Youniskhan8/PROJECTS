import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load trained model
if os.path.exists("model.pkl"):
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    print("✅ Model loaded successfully!")
else:
    print("❌ model.pkl not found!")

# Load Label Encoders
with open("label_encoders.pkl", "rb") as le_file:
    le_dict = pickle.load(le_file)

# Load dataset for dropdowns
df = pd.read_csv("final_merged_dataset (1).csv")

dropdown_values = {
    "commodities": sorted(df["Commodity"].dropna().unique()),
    "varieties": sorted(df["Variety"].dropna().unique()),
    "grades": sorted(df["Grade"].dropna().unique()),
    "districts": sorted(df["District Name"].dropna().unique()),
    "markets": sorted(df["Market Name"].dropna().unique())
}

@app.route("/")
def status():
    return "Commodity Price Prediction API is running!"

@app.route("/home", endpoint='home_page')
def home():
    return render_template("home.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html", dropdowns=dropdown_values)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # Required fields
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
