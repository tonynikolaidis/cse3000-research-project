import os
import json
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def compute_metrics(y_true, y_pred):
    return {
        'accuracy':  accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
        'recall':    recall_score(y_true, y_pred, average='macro', zero_division=0),
        'f1':        f1_score(y_true, y_pred, average='macro', zero_division=0),
    }

def evaluate(gt_path, res_path):
    df_gt = pd.read_csv(gt_path)
    df_rs = pd.read_csv(res_path)
    y_true, y_pred = [], []
    for col in df_gt.columns:
        if col != 'Speaker' and col in df_rs.columns:
            y_true.extend(df_gt[col].tolist())
            y_pred.extend(df_rs[col].tolist())
    if not y_true or len(y_true) != len(y_pred):
        return None
    return compute_metrics(y_true, y_pred)

def bootstrap_p(diffs, n_iter=5000, seed=0):
    rng = np.random.default_rng(seed)
    diffs = np.array(diffs)
    boot_means = []
    for _ in range(n_iter):
        sample = rng.choice(diffs, size=len(diffs), replace=True)
        boot_means.append(sample.mean())
    boot_means = np.array(boot_means)
    # one-tailed p-value: proportion of boot_means ≤ 0
    p = np.mean(boot_means <= 0)
    return diffs.mean(), p

def main(data_dir='hearings'):
    MODELS    = ['chatgpt-4o-latest', 'o3']
    CONTRASTS = [
        ('few_shot.csv',      'zero_shot.csv'),
        ('few_shot_cot.csv',  'few_shot.csv'),
        ('zero_shot_cot.csv', 'zero_shot.csv'),
        ('zero_shot_cot.csv', 'few_shot_cot.csv'),
    ]
    METRICS   = ['accuracy', 'precision', 'recall', 'f1']

    # 1) collect metrics per (model, prompt)
    scores = defaultdict(list)
    for hearing in os.listdir(data_dir):
        gt = os.path.join(data_dir, hearing, 'ground_truth.csv')
        if not os.path.isfile(gt):
            continue
        for model in MODELS:
            out = os.path.join(data_dir, hearing, 'output', model)
            if not os.path.isdir(out):
                continue
            for prompt in {c for pair in CONTRASTS for c in pair}:
                path = os.path.join(out, prompt)
                if os.path.isfile(path):
                    m = evaluate(gt, path)
                    if m:
                        scores[(model, prompt)].append(m)

    results = {}

    # 2) per-model bootstrap tests
    for model in MODELS:
        for cot, base in CONTRASTS:
            key = f'{model}: {cot} > {base}'
            results[key] = {}
            diffs_by_metric = {metric: [] for metric in METRICS}
            cot_list  = scores[(model, cot)]
            base_list = scores[(model, base)]
            for m_cot, m_base in zip(cot_list, base_list):
                for metric in METRICS:
                    diffs_by_metric[metric].append(m_cot[metric] - m_base[metric])
            for metric in METRICS:
                diffs = diffs_by_metric[metric]
                if len(diffs) < 1:
                    results[key][metric] = {'mean_diff': None, 'p': None}
                else:
                    mean_diff, p = bootstrap_p(diffs)
                    results[key][metric] = {
                        'mean_diff': round(mean_diff, 4),
                        'p':          round(p, 4)
                    }

    # 3) pooled bootstrap tests across both models
    for cot, base in CONTRASTS:
        key = f'pooled: {cot} > {base}'
        results[key] = {}
        for metric in METRICS:
            diffs = []
            for model in MODELS:
                cot_list  = scores[(model, cot)]
                base_list = scores[(model, base)]
                for m_cot, m_base in zip(cot_list, base_list):
                    diffs.append(m_cot[metric] - m_base[metric])
            if not diffs:
                results[key][metric] = {'mean_diff': None, 'p': None}
            else:
                mean_diff, p = bootstrap_p(diffs)
                results[key][metric] = {
                    'mean_diff': round(mean_diff, 4),
                    'p':          round(p, 4)
                }

    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
