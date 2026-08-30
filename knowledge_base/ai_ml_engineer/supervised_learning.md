# Supervised Learning Fundamentals

## Bias-Variance Tradeoff
The generalization error of machine learning models stems from three components:
- **Bias**: Error introduced by approximating a real-world problem with an oversimplified model (causes underfitting).
- **Variance**: Error introduced by sensitivity to small fluctuations in training data (causes overfitting).
- **Irreducible Error**: Inherent noise within data measurements.

## Linear Models & Regularization
Linear Regression minimizes Mean Squared Error (MSE), whereas Logistic Regression applies the Sigmoid (Logit) function to map predictions to probability ranges `[0, 1]` using Binary Cross-Entropy loss.
Regularization penalizes high weights:
- **L1 Regularization (Lasso)**: Adds `lambda * sum(|w|)` penalty, driving weights to exact zeros and yielding feature selection.
- **L2 Regularization (Ridge)**: Adds `lambda * sum(w^2)` penalty, shrinking weights uniformly to mitigate multicollinearity.
- **ElasticNet**: Combines L1 and L2 penalties.
