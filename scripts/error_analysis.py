import numpy as np
import importlib
import pandas as pd
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split

# Add src to sys.path to import prompthound
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from prompthound.features import FEATURE_NAMES


def load_class(class_path):
    module_name, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


def main():
    base_dir = Path(__file__).parent
    features_path = base_dir.parent / "data" / "features.npz"

    data = np.load(features_path)
    X = pd.DataFrame(data["X"], columns=FEATURE_NAMES)
    y = data["y"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train LGBM with the best params
    cls = load_class("lightgbm.LGBMClassifier")
    clf = cls(
        n_estimators=100,
        learning_rate=0.1,
        num_leaves=31,
        class_weight="balanced",
        random_state=42,
        verbose=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Find False Negatives: True = Malicious, Pred = Safe
    fn_indices = np.where((y_test == "malicious") & (y_pred == "safe"))[0]

    print(f"Total Malicious in Test: {np.sum(y_test == 'malicious')}")
    print(f"Total False Negatives (Malicious as Safe): {len(fn_indices)}")

    if len(fn_indices) > 0:
        print(
            "\nAverage Feature Values for False Negatives vs True Positives (Malicious as Malicious):"
        )
        tp_indices = np.where((y_test == "malicious") & (y_pred == "malicious"))[0]

        feature_names = FEATURE_NAMES

        fn_means = X_test.iloc[fn_indices].mean(axis=0)
        tp_means = (
            X_test.iloc[tp_indices].mean(axis=0)
            if len(tp_indices) > 0
            else pd.Series(0, index=feature_names)
        )

        for name in feature_names:
            fn_val = fn_means[name]
            tp_val = tp_means[name]
            print(f"{name:25s} | FN mean: {fn_val:.4f} | TP mean: {tp_val:.4f}")


if __name__ == "__main__":
    main()
