import numpy as np
import yaml
import importlib
from pathlib import Path
from sklearn.model_selection import train_test_split

def load_class(class_path):
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def main():
    base_dir = Path(__file__).parent
    features_path = base_dir.parent / 'data' / 'features.npz'
    
    data = np.load(features_path)
    X = data['X']
    y = data['y']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train LGBM with the best params
    cls = load_class('lightgbm.LGBMClassifier')
    clf = cls(n_estimators=100, learning_rate=0.1, num_leaves=31, class_weight='balanced', random_state=42, verbose=-1)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    
    # Find False Negatives: True = Malicious, Pred = Safe
    fn_indices = np.where((y_test == 'malicious') & (y_pred == 'safe'))[0]
    
    print(f"Total Malicious in Test: {np.sum(y_test == 'malicious')}")
    print(f"Total False Negatives (Malicious as Safe): {len(fn_indices)}")
    
    if len(fn_indices) > 0:
        print("\nAverage Feature Values for False Negatives vs True Positives (Malicious as Malicious):")
        tp_indices = np.where((y_test == 'malicious') & (y_pred == 'malicious'))[0]
        
        feature_names = [
            'b64_ratio', 'padding_ratio', 'code_to_prose_ratio', 'url_count', 
            'unicode_count', 'shell_command_presence', 'urgency_density', 
            'entropy', 'is_bundle', 'member_count', 'capability_mismatch_score'
        ]
        
        fn_means = np.mean(X_test[fn_indices], axis=0)
        tp_means = np.mean(X_test[tp_indices], axis=0) if len(tp_indices) > 0 else np.zeros(len(feature_names))
        
        for name, fn_val, tp_val in zip(feature_names, fn_means, tp_means):
            print(f"{name:25s} | FN mean: {fn_val:.4f} | TP mean: {tp_val:.4f}")

if __name__ == '__main__':
    main()
