import os
import numpy as np
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")


class PrompthoundClassifier:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)

    def predict_proba(self, X):
        if self.model:
            return self.model.predict_proba(X)
        return np.random.dirichlet((10, 5, 1), 1)

    def predict(self, X):
        if self.model:
            return self.model.predict(X)
        probs = self.predict_proba(X)
        classes = ["safe", "suspicious", "malicious"]
        return np.array([classes[np.argmax(probs[0])]])


_model = PrompthoundClassifier()


def score_features(feature_dict):
    feature_names = [
        "b64_ratio",
        "padding_ratio",
        "code_to_prose_ratio",
        "url_count",
        "unicode_count",
        "shell_command_presence",
        "urgency_density",
        "entropy",
        "is_bundle",
        "member_count",
        "capability_mismatch_score",
        "high_severity_hits",
        "medium_severity_hits",
        "eval_exec_density",
        "secret_keyword_density",
    ]

    X = np.array([[feature_dict[name] for name in feature_names]])

    if _model.model:
        classes = _model.model.classes_
        probs = _model.predict_proba(X)[0]
        classification = _model.predict(X)[0]

        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probs)}
    else:
        classification = _model.predict(X)[0]
        probs = _model.predict_proba(X)[0]
        prob_dict = {
            "safe": float(probs[0]),
            "suspicious": float(probs[1]),
            "malicious": float(probs[2]),
        }

    return {
        "class": classification,
        "probabilities": {
            "safe": prob_dict.get("safe", 0.0),
            "suspicious": prob_dict.get("suspicious", 0.0),
            "malicious": prob_dict.get("malicious", 0.0),
        },
    }
