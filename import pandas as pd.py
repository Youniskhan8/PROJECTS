import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Load dataset
df = pd.read_csv('C:\Users\91979\Desktop\agriAPI/final_merged_dataset (1).csv')

# Drop rows with missing target
df = df.dropna(subset=['Modal Price (Rs./Quintal)'])

# Extract date features
df['Price Date'] = pd.to_datetime(df['Price Date'], errors='coerce')
df = df.dropna(subset=['Price Date'])
df['year'] = df['Price Date'].dt.year
df['month'] = df['Price Date'].dt.month

# Encode categorical variables
categorical_cols = ['District Name', 'Market Name', 'Commodity', 'Variety', 'Grade']
le_dict = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    le_dict[col] = le

# Prepare data
X = df[['District Name', 'Market Name', 'Commodity', 'Variety', 'Grade', 'year', 'month', 'Temperature']]
y = df['Modal Price (Rs./Quintal)']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning using RandomizedSearchCV
param_grid = {
    'n_estimators': [50, 100, 200],  
    'max_depth': [10, 20, 30, None],  
    'min_samples_split': [2, 5, 10],  
    'min_samples_leaf': [1, 2, 4]
}

rf_random = RandomizedSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_distributions=param_grid,
    n_iter=10,  # Faster tuning
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1  # Parallel processing
)

rf_random.fit(X_train, y_train)
best_params = rf_random.best_params_
print("Best Parameters:", best_params)

# Train model with best parameters
model = RandomForestRegressor(**best_params, random_state=42)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R2 Score:", r2_score(y_test, y_pred))

# Feature Importance
importances = model.feature_importances_
feature_names = X.columns
sorted_features = sorted(zip(importances, feature_names), reverse=True)
print("Feature Importances:", sorted_features)

# Create valid values dictionary
valid_values = {}
for col in categorical_cols:
    valid_values[col] = le_dict[col].classes_

def validate_sample_strict(sample):
    if sample['Market Name'] not in valid_values['Market Name']:
        print(f"❌ Market '{sample['Market Name']}' not found.")
        print(f"✅ Valid Markets: {valid_values['Market Name']}")
        return False

    combo_exists = df[
        (df['Commodity'] == le_dict['Commodity'].transform([sample['Commodity']])[0]) &
        (df['Variety'] == le_dict['Variety'].transform([sample['Variety']])[0]) &
        (df['Grade'] == le_dict['Grade'].transform([sample['Grade']])[0])
    ]
    if combo_exists.empty:
        print(f"❌ Combination of Commodity '{sample['Commodity']}', Variety '{sample['Variety']}', and Grade '{sample['Grade']}' does not exist.")
        return False

    print("✅ Sample is valid for prediction!")
    return True

def predict_price(sample):
    sample_encoded = sample.copy()
    for col in categorical_cols:
        sample_encoded[col] = le_dict[col].transform([sample[col]])[0]

    # Extract year and month separately
    sample_encoded['year'] = sample['Price Date'].year
    sample_encoded['month'] = sample['Price Date'].month

    # Only keep the columns used in training
    model_input = pd.DataFrame([{
        'District Name': sample_encoded['District Name'],
        'Market Name': sample_encoded['Market Name'],
        'Commodity': sample_encoded['Commodity'],
        'Variety': sample_encoded['Variety'],
        'Grade': sample_encoded['Grade'],
        'year': sample_encoded['year'],
        'month': sample_encoded['month'],
        'Temperature': sample['Temperature']
    }])

    prediction = model.predict(model_input)[0]
    return prediction

# Example
sample = {
    'Commodity': 'Apple',
    'Variety': 'American',
    'Grade': 'Medium',
    'District Name': 'Srinagar',
    'Market Name': 'Ganderbal',
    'Price Date': pd.to_datetime('2024-03-18'),
    'Temperature': 5.6
}

if validate_sample_strict(sample):
    predicted_price = predict_price(sample)
    print("Predicted Modal Price:", predicted_price)
else:
    print("⚠️ Invalid input, cannot predict.")
