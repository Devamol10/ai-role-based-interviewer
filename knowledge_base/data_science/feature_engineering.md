# Feature Engineering & Preprocessing

## Categorical Encoding Strategies
1. **One-Hot Encoding**: Converts categorical variables into binary indicator vectors for nominal categories without inherent order.
2. **Ordinal Encoding**: Maps ordered categories to integer ranks.
3. **Target (Mean) Encoding**: Replaces categories with the mean target value of the training subset. Requires smoothing and out-of-fold calculation to prevent target leakage.

## Numerical Transformation & Scaling
- **Standard Scaling (Z-score Normalization)**: Rescales features to zero mean and unit variance (`(x - mu) / sigma`).
- **Min-Max Scaling**: Bounds features into range `[0, 1]`.
- **Log and Power Transformations**: Reduces right-skewness and stabilizes variance across dynamic feature distributions.
