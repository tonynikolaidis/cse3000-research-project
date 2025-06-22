import os
import json
import pandas as pd
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score

MODELS = ["chatgpt-4o-latest", "o3"]
PROMPT_FILES = ["zero_shot.csv", "few_shot.csv", "zero_shot_cot.csv", "few_shot_cot.csv"]

def compute_metrics(y_true, y_pred):
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='macro', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='macro', zero_division=0),
    }

def evaluate(gt_file, result_file, by_speakers=False):
    try:
        if by_speakers:
            df_gt = pd.read_csv(gt_file).set_index('Speaker').T
            df_rs = pd.read_csv(result_file).set_index('Speaker').T

            # Flatten all values into one list
            y_true = df_gt.values.flatten()
            y_pred = df_rs.values.flatten()
        else:
            df_gt = pd.read_csv(gt_file)
            df_rs = pd.read_csv(result_file)

            y_true = []
            y_pred = []
            for col in df_gt.columns:
                if col == "Speaker" or col not in df_rs.columns:
                    continue
                if len(df_gt[col]) != len(df_rs[col]):
                    continue
                y_true.extend(df_gt[col].tolist())
                y_pred.extend(df_rs[col].tolist())

        if len(y_true) != len(y_pred) or not y_true:
            return None

        return compute_metrics(y_true, y_pred)

    except Exception as e:
        print(f"⚠ Error comparing {result_file}: {e}")
        return None

def main(base_dir="hearings", by_speakers=False):
    all_scores = {}  # key: model/prompt, value: list of metrics per hearing

    for hearing in os.listdir(base_dir):
        hearing_path = os.path.join(base_dir, hearing)
        gt_file = os.path.join(hearing_path, "ground_truth.csv")
        if not os.path.isfile(gt_file):
            continue

        print(f"→ Evaluating {hearing}")
        for model in MODELS:
            model_dir = os.path.join(hearing_path, "output", model)
            if not os.path.isdir(model_dir):
                continue

            for prompt_file in PROMPT_FILES:
                result_path = os.path.join(model_dir, prompt_file)
                if not os.path.isfile(result_path):
                    continue

                key = f"{model}/{prompt_file}"
                metrics = evaluate(gt_file, result_path, by_speakers)
                if metrics:
                    all_scores.setdefault(key, []).append(metrics)

    # Compute average over all hearings
    averaged_results = {}
    for key, entries in all_scores.items():
        avg = {
            metric: round(sum(e[metric] for e in entries) / len(entries), 4)
            for metric in ['accuracy', 'precision', 'recall', 'f1']
        }
        averaged_results[key] = avg

    # Save final output
    suffix = "speakers" if by_speakers else "topics"
    out_file = os.path.join(base_dir, f"overall_eval_results_{suffix}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(averaged_results, f, indent=2)

    print(f"✓ Saved overall results to {out_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--speakers", action="store_true", help="Evaluate by speaker instead of topic")
    args = parser.parse_args()

    main(by_speakers=args.speakers)
