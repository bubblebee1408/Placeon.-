from typing import Dict, List
from pydantic import BaseModel, Field

from skill_taxonomy import DEFAULT_TRACKED_SKILLS


class Layer2Config(BaseModel):
    tracked_skills: List[str] = Field(default_factory=lambda: list(DEFAULT_TRACKED_SKILLS))
    base_score: float = 0.5
    base_uncertainty: float = 0.8
    uncertainty_floor: float = 0.01
    # Kalman Tracking Parameters (Optimized via 200-Candidate Marathon)
    process_noise_q: float = 0.02  # Higher drift allowed to catch rapid state changes
    measurement_noise_r_base: float = 0.03  # Very low noise baseline for high-precision sensors
    convergence_threshold: float = 0.05  # MAE target for high-precision convergence
    
    # Latent Skill Correlation Heuristics (Discovered via Simulation)
    latent_correlations: Dict[str, Dict[str, float]] = {
        "system_design": {"concurrency": -0.45}
    }
