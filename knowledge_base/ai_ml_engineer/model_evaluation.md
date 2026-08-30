# Model Evaluation Metrics & Validation

## Confusion Matrix & Metrics
Classification performance relies on four outcomes: True Positive (TP), False Positive (FP), True Negative (TN), and False Negative (FN).
- **Precision**: `TP / (TP + FP)` - Ratio of correctly predicted positive observations to total predicted positives. Critical when False Positives carry high cost (e.g. Spam detection).
- **Recall (Sensitivity)**: `TP / (TP + FN)` - Ratio of correctly predicted positive observations to total actual positives. Critical when False Negatives carry high cost (e.g. Cancer detection).
- **F1 Score**: Harmonic mean of Precision and Recall (`2 * (Precision * Recall) / (Precision + Recall)`).
- **ROC-AUC**: Area Under the Receiver Operating Characteristic Curve plotting True Positive Rate vs False Positive Rate across classification thresholds.

## Cross-Validation Techniques
K-Fold Cross-Validation partitions data into K equal subsets, training K iterations on K-1 folds while validating on the remaining fold. Stratified K-Fold preserves class label proportions in imbalanced datasets.
