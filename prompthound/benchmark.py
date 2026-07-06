import numpy as np
import yaml
import importlib
import warnings
from pathlib import Path
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, confusion_matrix

warnings.filterwarnings('ignore')

def load_class(class_path):
    module_name, class_name = class_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def compute_fpr(y_true, y_pred, safe_label='safe', suspicious_label='suspicious', malicious_label='malicious'):
    # FPR Severe: Safe files predicted as Malicious
    # FPR Mild: Safe files predicted as Suspicious
    
    safe_mask = (y_true == safe_label)
    total_safe = np.sum(safe_mask)
    
    if total_safe == 0:
        return 0.0, 0.0
        
    predicted_as_malicious = np.sum((y_pred == malicious_label) & safe_mask)
    predicted_as_suspicious = np.sum((y_pred == suspicious_label) & safe_mask)
    
    fpr_severe = predicted_as_malicious / total_safe
    fpr_mild = predicted_as_suspicious / total_safe
    
    return fpr_severe, fpr_mild

def main():
    base_dir = Path(__file__).parent
    features_path = base_dir / 'features.npz'
    models_yaml_path = base_dir / 'models.yaml'
    
    if not features_path.exists():
        print("features.npz not found. Run extract_data.py first.")
        return
        
    data = np.load(features_path)
    X = data['X']
    y = data['y']
    
    # 80/20 train/test split, stratified by y
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Train size: {len(y_train)}, Test size: {len(y_test)}")
    
    with open(models_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
        
    results = []
    
    for model_name, model_info in config['models'].items():
        print(f"\n--- Benchmarking {model_name} ---")
        
        cls = load_class(model_info['class'])
        param_grid = model_info.get('params', {})
        
        # GridSearchCV
        clf = GridSearchCV(
            estimator=cls(),
            param_grid=param_grid,
            cv=3,
            scoring='f1_macro',
            n_jobs=-1
        )
        
        print("Training with GridSearchCV...")
        clf.fit(X_train, y_train)
        print(f"Best parameters: {clf.best_params_}")
        
        best_model = clf.best_estimator_
        y_pred = best_model.predict(X_test)
        
        f1_mac = f1_score(y_test, y_pred, average='macro')
        prec_mac = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec_mac = recall_score(y_test, y_pred, average='macro', zero_division=0)
        
        fpr_severe, fpr_mild = compute_fpr(y_test, y_pred)
        
        results.append({
            'Model': model_name,
            'Macro-F1': f1_mac,
            'Macro-Precision': prec_mac,
            'Macro-Recall': rec_mac,
            'FPR-Severe': fpr_severe,
            'FPR-Mild': fpr_mild
        })
        
        print(f"Macro-F1: {f1_mac:.4f}")
        print(f"FPR-Severe: {fpr_severe:.4f}")
        print(f"FPR-Mild: {fpr_mild:.4f}")

    # Generate Markdown Report
    report = ["# PromptHound Benchmark Results", ""]
    report.append("| Model | Macro-F1 | Macro-Precision | Macro-Recall | FPR-Severe | FPR-Mild |")
    report.append("|---|---|---|---|---|---|")
    
    # Sort by F1-Macro descending
    results.sort(key=lambda x: x['Macro-F1'], reverse=True)
    
    for r in results:
        row = f"| {r['Model']} | {r['Macro-F1']:.4f} | {r['Macro-Precision']:.4f} | {r['Macro-Recall']:.4f} | {r['FPR-Severe']:.4f} | {r['FPR-Mild']:.4f} |"
        report.append(row)
        
    report_path = base_dir / 'benchmark_report.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
        
    print(f"\nBenchmark completed. Report saved to {report_path}")

if __name__ == '__main__':
    main()
