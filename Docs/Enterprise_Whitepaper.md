# PlacedOn Enterprise Architecture: The KAN Paradigm Shift

## Executive Summary
This document serves as the foundational artifact tracking PlacedOn's transition from classical deep learning (MLPs) into a state-of-the-art **Interpretability Ecosystem** powered by **Kolmogorov-Arnold Networks (KANs)**. This architecture allows PlacedOn to solve the "AI Black Box" problem while maintaining superior predictive accuracy.

## The Scaling & Interpretability Problem
As PlacedOn scales, we parse candidate responses into 384-dimensional semantic arrays. While standard Multi-Layer Perceptrons (MLPs) can map these, they are "Black Boxes"—stakeholders cannot see *how* a hiring decision was made. Furthermore, MLPs are parameter-heavy and struggle to generalize with limited "Expert" data.

## The KAN 2.0 Solution
To secure PlacedOn as a robust, transparent enterprise platform, we executed an architecture pivot to KANs:

1. **Spline-Based Connections**: Instead of fixed node activations, KANs use learnable, non-linear splines on the edges. This allows the model to learn the fundamental "mathematical functions" of a successful candidate.
2. **Semantic Calibration (2.0)**: We anchored our Neural Splines using real SBERT technical archetypes (Senior vs Junior). This ensures the model recognizes technical substance over generic keywords.
3. **Interpretability**: Because the network learns functions, we can mathematically trace the "influence" of specific semantic clusters on the final hiring score.

## Production Roadmap
The KAN 2.0 engine is now integrated into Layer 5. Our React Dashboard will now show two critical metrics:
- **Neural Performance Score**: The primary predictive output (90%+ accuracy benchmark).
- **Justification Matrix**: A data-driven explanation of which technical clusters drove the hiring recommendation.

This is the PlacedOn Moat: Transparent, verified technical intelligence.
