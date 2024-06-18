pip install pandas
pip install -U matplotlib
pip install seaborn
pip install scikit-learn



import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
import logging


from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler, MinMaxScaler


# Load the dataset
file_path = 'enriched_playlist_v2.csv'  # Update with the correct path
data = pd.read_csv(file_path)

# Convert to more memory-efficient data types
for col in data.select_dtypes(include=['float64']).columns:
    data[col] = data[col].astype('float32')
for col in data.select_dtypes(include=['int64']).columns:
    data[col] = data[col].astype('int32')


# Identify and remove sparse classes
min_samples_per_class = 20
value_counts = data['playlist_id'].value_counts()
to_remove = value_counts[value_counts < min_samples_per_class].index
data = data[~data['playlist_id'].isin(to_remove)]

# Verify removal
remaining_counts = data['playlist_id'].value_counts()
print("Class distribution after removal:")
print(remaining_counts)

# Ensure no class has fewer than min_samples_per_class
assert remaining_counts.min() >= min_samples_per_class, "There are still classes with fewer than the minimum required samples."


print(data.info())

print(value_counts[value_counts >= min_samples_per_class])

# Separate features for normalization and standardization
features_to_normalize = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
features_to_standardize = ['loudness', 'tempo']

# Prepare features and labels
X = data[['danceability', 'energy', 'loudness', 'speechiness',
          'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
y = data['playlist_id']

# Apply MinMaxScaler for normalization
scaler_norm = MinMaxScaler()
X.loc[:, features_to_normalize] = scaler_norm.fit_transform(X[features_to_normalize])

# Apply StandardScaler for standardization
scaler_std = StandardScaler()
X.loc[:, features_to_standardize] = scaler_std.fit_transform(X[features_to_standardize])

# Create a smaller subset manually to ensure the minimum sample requirement is met
subset_fraction = 0.05
# Ensure subset meets the minimum requirement
subset = data.groupby('playlist_id').apply(lambda x: x.sample(n=min(len(x), min_samples_per_class), random_state=42))
subset = subset.reset_index(drop=True)

X_subset = subset[['danceability', 'energy', 'loudness', 'speechiness',
                   'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
y_subset = subset['playlist_id']

# Verify subset class distribution
subset_counts = y_subset.value_counts()
print("Subset class distribution:")
print(subset_counts)
assert subset_counts.min() >= min_samples_per_class, "Subset still has classes with fewer than the minimum required samples."



print(subset.info())


# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Fit the model
try:
    logger.info("Starting Grid Search")
    grid_search.fit(X_train, y_train)  # Replace X_train, y_train with your data
    logger.info("Grid Search completed successfully")
except Exception as e:
    logger.error(f"Error during Grid Search: {e}")

# Log the best parameters and score
logger.info(f"Best parameters found: {grid_search.best_params_}")
logger.info(f"Best cross-validation score: {grid_search.best_score_}")

# Split the subset into training and test sets for cross-validation
X_train, X_test, y_train, y_test = train_test_split(X_subset, y_subset, test_size=0.2, random_state=42)

# Define the parameter grid for Grid Search
param_grid = {
    'max_depth': [None, 10, 20, 30],
    'n_estimators': [10, 20, 50],
    'max_features': ['auto', 'sqrt']
}


# Initialize the Random Forest model

rf = RandomForestClassifier(random_state=42)

# Initialize Grid Search
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=127, scoring='accuracy')

# Fit the model
try:
    logger.info("Starting Grid Search")
    grid_search.fit(X_train, y_train)  # Replace X_train, y_train with your data
    logger.info("Grid Search completed successfully")
except Exception as e:
    logger.error(f"Error during Grid Search: {e}")

# Log the best parameters and score
logger.info(f"Best parameters found: {grid_search.best_params_}")
logger.info(f"Best cross-validation score: {grid_search.best_score_}")



# Get the best parameters and score
best_params = grid_search.best_params_
best_score = grid_search.best_score_

print(f"Best parameters: {best_params}")
print(f"Best cross-validation score: {best_score:.2f}")

# Evaluate the best model on the test set
best_rf = grid_search.best_estimator_
test_accuracy = best_rf.score(X_test, y_test)
print(f"Test set accuracy on subset: {test_accuracy:.2f}")

# Save the trained model from Grid Search
model_filename = 'best_random_forest_model.joblib'
joblib.dump(best_rf, model_filename)
print(f"Model saved to {model_filename}")

# Load the model and evaluate on the test set
rf_loaded = joblib.load(model_filename)
test_accuracy_loaded = rf_loaded.score(X_test, y_test)
print(f"Test set accuracy with loaded model on subset: {test_accuracy_loaded:.2f}")

# Apply the best parameters to the full dataset
X_train_full, X_test_full, y_train_full, y_test_full = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Random Forest model with the best parameters
rf_full = RandomForestClassifier(**best_params, random_state=42)

# Train on the full dataset
rf_full.fit(X_train_full, y_train_full)

# Save the trained model from the full dataset
full_model_filename = 'full_random_forest_model.joblib'
joblib.dump(rf_full, full_model_filename)
print(f"Full model saved to {full_model_filename}")

# Load the full model and evaluate on the test set
rf_full_loaded = joblib.load(full_model_filename)
test_accuracy_full_loaded = rf_full_loaded.score(X_test_full, y_test_full)
print(f"Test set accuracy with full loaded model: {test_accuracy_full_loaded:.2f}")