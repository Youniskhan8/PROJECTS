import pandas as pd

# Load the dataset
file_path = "/mnt/data/final_merged_dataset (1).csv"
df = pd.read_csv(file_path)

# Show unique values in the 'Grade' column before the change
unique_grades_before = df['Grade'].unique()
unique_grades_before
