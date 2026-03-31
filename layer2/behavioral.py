from layer2.embedding import cosine_distance
from layer2.models import AdapterOutput, BehavioralSignals


class BehavioralSignalTracker:
    async def track(self, history: list[AdapterOutput]) -> BehavioralSignals:
        if not history:
            return BehavioralSignals(consistency_score=0.0, drift_score=0.0, confidence_signal=0.0)

        drift = self._drift(history)
        consistency = self._consistency(history)
        confidence = sum(item.confidence for item in history) / len(history)

        return BehavioralSignals(
            consistency_score=round(max(0.0, min(consistency, 1.0)), 4),
            drift_score=round(max(0.0, min(drift, 1.0)), 4),
            confidence_signal=round(max(0.0, min(confidence, 1.0)), 4),
        )

    def _drift(self, history: list[AdapterOutput]) -> float:
        if len(history) < 2:
            return 0.0
        distances = [
            cosine_distance(history[idx - 1].embedding, history[idx].embedding)
            for idx in range(1, len(history))
        ]
        return sum(distances) / len(distances)

    def _consistency(self, history: list[AdapterOutput]) -> float:
        if len(history) < 2:
            return 1.0

        skills = history[0].skills.keys()
        deltas: list[float] = []
        for skill in skills:
            series = [item.skills[skill].score for item in history if skill in item.skills]
            deltas.extend(abs(series[idx] - series[idx - 1]) for idx in range(1, len(series)))

        if not deltas:
            return 1.0

        avg_delta = sum(deltas) / len(deltas)
        return 1.0 - min(avg_delta, 1.0)
