# ============================================================
# TwinMind AI - Model Training
# ============================================================
#
# Trains:
#   1. MLP Regression Model
#      Target: impact_percentage
#
#   2. MLP Classification Model
#      Target: direction
#
# Saves:
#   - impact_regressor.pth
#   - direction_classifier.pth
#   - preprocessor.joblib
#   - direction_label_encoder.joblib
#   - feature_config.joblib
#   - training_results.joblib
#
# ============================================================

import os
import json
import random
import joblib

import numpy as np
import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. CONFIGURATION
# ============================================================

DATASET_PATH = "twinmind_training_dataset.csv"

MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

RANDOM_SEED = 42

TEST_SIZE = 0.20

BATCH_SIZE = 256

EPOCHS = 100

LEARNING_RATE = 0.001

PATIENCE = 10


# ============================================================
# 2. REPRODUCIBILITY
# ============================================================

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)

print("=" * 70)
print("TwinMind AI - Model Training")
print("=" * 70)


# ============================================================
# 3. LOAD DATASET
# ============================================================

print("\n[1/10] Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {df.shape}")

print("\nColumns:")
for column in df.columns:
    print("  -", column)


# ============================================================
# 4. BASIC CLEANING
# ============================================================

print("\n[2/10] Cleaning dataset...")

# Convert date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Remove rows with missing target values
df = df.dropna(
    subset=[
        "impact_percentage",
        "direction"
    ]
).copy()

# Remove duplicate records
df = df.drop_duplicates()

# Sort chronologically
df = df.sort_values("Date").reset_index(drop=True)

print(f"Dataset after cleaning: {df.shape}")

print("\nDate range:")
print("Start:", df["Date"].min())
print("End  :", df["Date"].max())


# ============================================================
# 5. CREATE DATE FEATURES
# ============================================================

print("\n[3/10] Creating date features...")

# We do not feed the raw date string into the neural network.
# Instead, derive useful calendar information.

df["month"] = df["Date"].dt.month
df["day_of_week"] = df["Date"].dt.dayofweek

# Drop raw date
df = df.drop(columns=["Date"])


# ============================================================
# 6. DEFINE FEATURES AND TARGETS
# ============================================================

print("\n[4/10] Preparing features and targets...")


# ------------------------------------------------------------
# Numeric features
# ------------------------------------------------------------

NUMERIC_FEATURES = [

    # Warehouse / inventory state
    "Units_Sold",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Promotion_Flag",
    "Stockout_Flag",
    "Demand_Forecast",

    # Historical change features
    "units_sold_baseline_7d",
    "demand_change_pct",
    "lead_time_baseline",
    "lead_time_change_pct",

    # Logistics
    "container_availability_index",
    "port_congestion_index",
    "shipping_delay_days",
    "fuel_cost_index",
    "route_commodity_price_index",
    "weather_disruption_score",
    "route_disrupted_share",
    "route_delayed_share",

    # Commodity
    "commodity_stress_index",

    # Geopolitical
    "geopolitical_risk_score",
    "geo_event_count",
    "geo_max_severity",
    "geo_risk_increase",
    "export_restriction_count",
    "trade_sanction_count",
    "port_strike_count",

    # Date-derived
    "month",
    "day_of_week"
]


# ------------------------------------------------------------
# Categorical features
# ------------------------------------------------------------

CATEGORICAL_FEATURES = [

    # Product identity
    "SKU_ID",

    # Warehouse identity
    "Warehouse_ID",

    # Supplier identity
    "Supplier_ID",

    # Region
    "Region",

    # User-selected scenario
    "scenario_type",

    # User-selected severity
    "severity"
]


# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------

REGRESSION_TARGET = "impact_percentage"

CLASSIFICATION_TARGET = "direction"


# ============================================================
# 7. CHECK FEATURES
# ============================================================

all_features = NUMERIC_FEATURES + CATEGORICAL_FEATURES

missing_features = [
    feature
    for feature in all_features
    if feature not in df.columns
]

if missing_features:

    raise ValueError(
        "The following required features are missing from the dataset:\n"
        + "\n".join(missing_features)
    )


print("\nNumber of numerical features:", len(NUMERIC_FEATURES))
print("Number of categorical features:", len(CATEGORICAL_FEATURES))
print("Total input features before encoding:", len(all_features))


# ============================================================
# 8. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

print("\n[5/10] Creating chronological train/test split...")

# IMPORTANT:
# We do NOT randomly shuffle the complete dataset before splitting.
# Older records -> training
# Newer records -> testing

split_index = int(len(df) * (1 - TEST_SIZE))

train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()

print(f"Training rows: {len(train_df)}")
print(f"Testing rows : {len(test_df)}")

print("\nTraining period:")
print(train_df.index.min(), "to", train_df.index.max())

print("\nTesting period:")
print(test_df.index.min(), "to", test_df.index.max())


# ============================================================
# 9. SEPARATE X AND Y
# ============================================================

X_train = train_df[all_features].copy()
X_test = test_df[all_features].copy()

y_reg_train = train_df[REGRESSION_TARGET].values.astype(np.float32)
y_reg_test = test_df[REGRESSION_TARGET].values.astype(np.float32)

y_cls_train = train_df[CLASSIFICATION_TARGET].values
y_cls_test = test_df[CLASSIFICATION_TARGET].values


# ============================================================
# 10. PREPROCESSING
# ============================================================

print("\n[6/10] Fitting preprocessing pipeline...")

numeric_transformer = StandardScaler()

# Handle different sklearn versions
try:
    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    )
except TypeError:
    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse=False
    )


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_transformer,
            NUMERIC_FEATURES
        ),
        (
            "categorical",
            categorical_transformer,
            CATEGORICAL_FEATURES
        )
    ]
)


# IMPORTANT:
# Fit ONLY on training data.
X_train_processed = preprocessor.fit_transform(X_train)

# Transform test data using the same fitted preprocessing.
X_test_processed = preprocessor.transform(X_test)


X_train_processed = np.asarray(
    X_train_processed,
    dtype=np.float32
)

X_test_processed = np.asarray(
    X_test_processed,
    dtype=np.float32
)


INPUT_SIZE = X_train_processed.shape[1]

print("Final neural-network input size:", INPUT_SIZE)


# ============================================================
# 11. ENCODE DIRECTION LABELS
# ============================================================

label_encoder = LabelEncoder()

y_cls_train_encoded = label_encoder.fit_transform(y_cls_train)
y_cls_test_encoded = label_encoder.transform(y_cls_test)

print("\nDirection classes:")

for index, label in enumerate(label_encoder.classes_):
    print(f"  {index} -> {label}")


# ============================================================
# 12. CREATE PYTORCH DATASETS
# ============================================================

X_train_tensor = torch.tensor(
    X_train_processed,
    dtype=torch.float32
)

X_test_tensor = torch.tensor(
    X_test_processed,
    dtype=torch.float32
)


# Regression tensors
y_reg_train_tensor = torch.tensor(
    y_reg_train,
    dtype=torch.float32
).reshape(-1, 1)

y_reg_test_tensor = torch.tensor(
    y_reg_test,
    dtype=torch.float32
).reshape(-1, 1)


# Classification tensors
y_cls_train_tensor = torch.tensor(
    y_cls_train_encoded,
    dtype=torch.long
)

y_cls_test_tensor = torch.tensor(
    y_cls_test_encoded,
    dtype=torch.long
)


regression_dataset = TensorDataset(
    X_train_tensor,
    y_reg_train_tensor
)

classification_dataset = TensorDataset(
    X_train_tensor,
    y_cls_train_tensor
)


regression_loader = DataLoader(
    regression_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

classification_loader = DataLoader(
    classification_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


# ============================================================
# 13. DEFINE MLP REGRESSION MODEL
# ============================================================

class ImpactRegressor(nn.Module):

    def __init__(self, input_size):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, 1)
        )

    def forward(self, x):

        return self.network(x)


# ============================================================
# 14. DEFINE MLP CLASSIFICATION MODEL
# ============================================================

class DirectionClassifier(nn.Module):

    def __init__(self, input_size, num_classes):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, num_classes)
        )

    def forward(self, x):

        return self.network(x)


# ============================================================
# 15. CREATE MODELS
# ============================================================

print("\n[7/10] Creating neural networks...")

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("Training device:", device)


impact_model = ImpactRegressor(
    INPUT_SIZE
).to(device)


direction_model = DirectionClassifier(
    INPUT_SIZE,
    len(label_encoder.classes_)
).to(device)


# ============================================================
# 16. REGRESSION TRAINING
# ============================================================

print("\n" + "=" * 70)
print("TRAINING IMPACT REGRESSION MODEL")
print("=" * 70)


regression_optimizer = torch.optim.Adam(
    impact_model.parameters(),
    lr=LEARNING_RATE
)

regression_loss_function = nn.MSELoss()


best_regression_loss = float("inf")
regression_patience_counter = 0

best_regression_state = None


for epoch in range(EPOCHS):

    impact_model.train()

    total_loss = 0.0

    for batch_X, batch_y in regression_loader:

        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        regression_optimizer.zero_grad()

        predictions = impact_model(batch_X)

        loss = regression_loss_function(
            predictions,
            batch_y
        )

        loss.backward()

        regression_optimizer.step()

        total_loss += loss.item() * len(batch_X)


    epoch_loss = total_loss / len(regression_dataset)


    # --------------------------------------------------------
    # Validation on test set
    # --------------------------------------------------------

    impact_model.eval()

    with torch.no_grad():

        test_predictions = impact_model(
            X_test_tensor.to(device)
        )

        validation_loss = regression_loss_function(
            test_predictions,
            y_reg_test_tensor.to(device)
        ).item()


    print(
        f"Epoch {epoch + 1:03d}/{EPOCHS} "
        f"| Train Loss: {epoch_loss:.4f} "
        f"| Test Loss: {validation_loss:.4f}"
    )


    # --------------------------------------------------------
    # Early stopping
    # --------------------------------------------------------

    if validation_loss < best_regression_loss:

        best_regression_loss = validation_loss

        regression_patience_counter = 0

        best_regression_state = {
            key: value.cpu().clone()
            for key, value in impact_model.state_dict().items()
        }

    else:

        regression_patience_counter += 1

        if regression_patience_counter >= PATIENCE:

            print("Early stopping regression training.")

            break


# Restore best model
impact_model.load_state_dict(
    best_regression_state
)


# ============================================================
# 17. REGRESSION EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("IMPACT REGRESSION EVALUATION")
print("=" * 70)


impact_model.eval()

with torch.no_grad():

    regression_predictions = impact_model(
        X_test_tensor.to(device)
    ).cpu().numpy().flatten()


# Keep predictions in realistic range
regression_predictions = np.clip(
    regression_predictions,
    0,
    100
)


mae = mean_absolute_error(
    y_reg_test,
    regression_predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_reg_test,
        regression_predictions
    )
)

r2 = r2_score(
    y_reg_test,
    regression_predictions
)


print(f"\nMAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


# ============================================================
# 18. CLASSIFICATION TRAINING
# ============================================================

print("\n" + "=" * 70)
print("TRAINING DIRECTION CLASSIFICATION MODEL")
print("=" * 70)


classification_optimizer = torch.optim.Adam(
    direction_model.parameters(),
    lr=LEARNING_RATE
)


# ------------------------------------------------------------
# Class imbalance handling
# ------------------------------------------------------------

class_counts = np.bincount(
    y_cls_train_encoded
)

class_weights = (
    len(y_cls_train_encoded)
    /
    (
        len(class_counts)
        *
        class_counts
    )
)

class_weights_tensor = torch.tensor(
    class_weights,
    dtype=torch.float32
).to(device)


classification_loss_function = nn.CrossEntropyLoss(
    weight=class_weights_tensor
)


best_classification_loss = float("inf")

classification_patience_counter = 0

best_classification_state = None


for epoch in range(EPOCHS):

    direction_model.train()

    total_loss = 0.0

    for batch_X, batch_y in classification_loader:

        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        classification_optimizer.zero_grad()

        logits = direction_model(batch_X)

        loss = classification_loss_function(
            logits,
            batch_y
        )

        loss.backward()

        classification_optimizer.step()

        total_loss += loss.item() * len(batch_X)


    epoch_loss = (
        total_loss
        /
        len(classification_dataset)
    )


    # --------------------------------------------------------
    # Test loss
    # --------------------------------------------------------

    direction_model.eval()

    with torch.no_grad():

        test_logits = direction_model(
            X_test_tensor.to(device)
        )

        validation_loss = classification_loss_function(
            test_logits,
            y_cls_test_tensor.to(device)
        ).item()


    print(
        f"Epoch {epoch + 1:03d}/{EPOCHS} "
        f"| Train Loss: {epoch_loss:.4f} "
        f"| Test Loss: {validation_loss:.4f}"
    )


    # --------------------------------------------------------
    # Early stopping
    # --------------------------------------------------------

    if validation_loss < best_classification_loss:

        best_classification_loss = validation_loss

        classification_patience_counter = 0

        best_classification_state = {
            key: value.cpu().clone()
            for key, value in direction_model.state_dict().items()
        }

    else:

        classification_patience_counter += 1

        if classification_patience_counter >= PATIENCE:

            print("Early stopping classification training.")

            break


# Restore best model
direction_model.load_state_dict(
    best_classification_state
)


# ============================================================
# 19. CLASSIFICATION EVALUATION
# ============================================================

print("\n" + "=" * 70)
print("DIRECTION CLASSIFICATION EVALUATION")
print("=" * 70)


direction_model.eval()

with torch.no_grad():

    logits = direction_model(
        X_test_tensor.to(device)
    )

    probabilities = torch.softmax(
        logits,
        dim=1
    )

    classification_predictions = torch.argmax(
        probabilities,
        dim=1
    ).cpu().numpy()


accuracy = accuracy_score(
    y_cls_test_encoded,
    classification_predictions
)

precision = precision_score(
    y_cls_test_encoded,
    classification_predictions,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_cls_test_encoded,
    classification_predictions,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_cls_test_encoded,
    classification_predictions,
    average="weighted",
    zero_division=0
)


print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


print("\nClassification Report:")

print(
    classification_report(
        y_cls_test_encoded,
        classification_predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ============================================================
# 20. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_cls_test_encoded,
    classification_predictions
)


plt.figure(figsize=(7, 6))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
)

plt.xlabel("Predicted Direction")
plt.ylabel("Actual Direction")
plt.title("TwinMind Direction Classification - Confusion Matrix")

plt.tight_layout()

confusion_matrix_path = os.path.join(
    MODEL_DIR,
    "direction_confusion_matrix.png"
)

plt.savefig(
    confusion_matrix_path,
    dpi=300
)

plt.close()


print(
    "\nConfusion matrix saved:",
    confusion_matrix_path
)


# ============================================================
# 21. REGRESSION ACTUAL VS PREDICTED GRAPH
# ============================================================

plt.figure(figsize=(8, 6))

plt.scatter(
    y_reg_test,
    regression_predictions,
    alpha=0.4
)

plt.xlabel("Actual Impact Percentage")
plt.ylabel("Predicted Impact Percentage")

plt.title(
    "TwinMind Impact Model - Actual vs Predicted"
)

# Perfect prediction line
min_value = min(
    y_reg_test.min(),
    regression_predictions.min()
)

max_value = max(
    y_reg_test.max(),
    regression_predictions.max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--"
)

plt.tight_layout()

regression_plot_path = os.path.join(
    MODEL_DIR,
    "impact_actual_vs_predicted.png"
)

plt.savefig(
    regression_plot_path,
    dpi=300
)

plt.close()


print(
    "Regression plot saved:",
    regression_plot_path
)


# ============================================================
# 22. SAVE MODELS
# ============================================================

print("\n[8/10] Saving trained models...")


impact_model_path = os.path.join(
    MODEL_DIR,
    "impact_regressor.pth"
)

direction_model_path = os.path.join(
    MODEL_DIR,
    "direction_classifier.pth"
)


torch.save(
    {
        "model_state_dict": impact_model.state_dict(),
        "input_size": INPUT_SIZE,
        "model_type": "ImpactRegressor"
    },
    impact_model_path
)


torch.save(
    {
        "model_state_dict": direction_model.state_dict(),
        "input_size": INPUT_SIZE,
        "num_classes": len(label_encoder.classes_),
        "model_type": "DirectionClassifier"
    },
    direction_model_path
)


print(
    "Saved:",
    impact_model_path
)

print(
    "Saved:",
    direction_model_path
)


# ============================================================
# 23. SAVE PREPROCESSOR
# ============================================================

print("\n[9/10] Saving preprocessing objects...")


preprocessor_path = os.path.join(
    MODEL_DIR,
    "preprocessor.joblib"
)

label_encoder_path = os.path.join(
    MODEL_DIR,
    "direction_label_encoder.joblib"
)


joblib.dump(
    preprocessor,
    preprocessor_path
)

joblib.dump(
    label_encoder,
    label_encoder_path
)


print(
    "Saved:",
    preprocessor_path
)

print(
    "Saved:",
    label_encoder_path
)


# ============================================================
# 24. SAVE FEATURE CONFIGURATION
# ============================================================

feature_config = {

    "numeric_features": NUMERIC_FEATURES,

    "categorical_features": CATEGORICAL_FEATURES,

    "all_features": all_features,

    "regression_target": REGRESSION_TARGET,

    "classification_target": CLASSIFICATION_TARGET,

    "direction_classes": label_encoder.classes_.tolist(),

    "input_size": INPUT_SIZE
}


feature_config_path = os.path.join(
    MODEL_DIR,
    "feature_config.joblib"
)


joblib.dump(
    feature_config,
    feature_config_path
)


print(
    "Saved:",
    feature_config_path
)


# ============================================================
# 25. SAVE TRAINING RESULTS
# ============================================================

training_results = {

    "dataset_rows": len(df),

    "training_rows": len(train_df),

    "testing_rows": len(test_df),

    "input_size": INPUT_SIZE,

    "regression": {

        "MAE": float(mae),

        "RMSE": float(rmse),

        "R2": float(r2)

    },

    "classification": {

        "Accuracy": float(accuracy),

        "Precision": float(precision),

        "Recall": float(recall),

        "F1": float(f1)

    },

    "direction_classes": label_encoder.classes_.tolist()

}


training_results_path = os.path.join(
    MODEL_DIR,
    "training_results.joblib"
)


joblib.dump(
    training_results,
    training_results_path
)


# Also save human-readable JSON
training_results_json_path = os.path.join(
    MODEL_DIR,
    "training_results.json"
)


with open(
    training_results_json_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        training_results,
        file,
        indent=4
    )


# ============================================================
# 26. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print("\nRegression Model")
print("----------------")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")


print("\nClassification Model")
print("--------------------")
print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


print("\nGenerated files:")

for filename in sorted(os.listdir(MODEL_DIR)):

    print(
        "  -",
        os.path.join(MODEL_DIR, filename)
    )


print("\nTwinMind AI model training finished successfully.")