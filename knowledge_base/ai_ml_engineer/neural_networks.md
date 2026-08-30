# Neural Network Architectures & Optimization

## Deep Learning Foundations
Artificial Neural Networks learn hierarchical feature representations through non-linear activation functions (ReLU, LeakyReLU, GELU, Softmax). Forward propagation computes model activations, while Backpropagation applies the Multivariable Chain Rule to compute loss gradients with respect to weights.

## Optimization & Gradient Descent Variants
- **Stochastic Gradient Descent (SGD)**: Updates weights using single samples or mini-batches.
- **Adam (Adaptive Moment Estimation)**: Combines Momentum (first moment of gradients) and RMSProp (exponential moving average of squared gradients) with bias correction to dynamically adjust per-parameter learning rates.

## Transformers and Self-Attention Mechanism
The Transformer architecture replaces recurrent architectures with Scaled Dot-Product Attention:
`Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V`
Multi-Head Attention enables joint attention across representation subspaces at distinct positions.
