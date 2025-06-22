import argparse
import pandas as pd
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Compare ground truth to results",
        description="Compute metrics per speaker by transposing",
    )
    parser.add_argument('folder')
    parser.add_argument('-g', '--ground', default="ground_truth.csv")
    parser.add_argument('-r', '--results', default="zero_shot_prompt_output.csv")
    parser.add_argument('-s', '--speakers', action='store_true')
    parser.add_argument('-o', '--output', default="results")
    args = parser.parse_args()

    hearing = args.folder
    measure_speakers = args.speakers
    base_path = f"hearings/{hearing}"
    gt_file  = f"{base_path}/{args.ground}"
    rs_file  = f"{base_path}/{args.results}"
    out_csv  = f"{base_path}/{args.output}_{'speakers' if measure_speakers else 'topics'}.csv"

    # Now each column is a speaker; loop over speakers exactly as you did per-topic before
    results = {
        'Metric': ['Accuracy', 'Precision (macro)', 'Recall (macro)', 'F1-score (macro)']
    }

    print('Measuring speakers: ', measure_speakers)

    if measure_speakers:
        # Load and transpose so that speakers are columns
        df_gt   = pd.read_csv(gt_file).set_index('Speaker').T
        df_test = pd.read_csv(rs_file).set_index('Speaker').T

        for speaker in df_gt.columns:
            y_true = df_gt[speaker]
            y_pred = df_test[speaker]

            acc    = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
            recall    = recall_score(y_true, y_pred, average='macro', zero_division=0)
            f1        = f1_score(y_true, y_pred, average='macro', zero_division=0)

            results[speaker] = [
                f"{acc:.4f}",
                f"{precision:.4f}",
                f"{recall:.4f}",
                f"{f1:.4f}"
            ]
    else:
        df_gt   = pd.read_csv(gt_file)
        df_test = pd.read_csv(rs_file)

        # All columns except 'Speaker' are label columns
        label_cols = [col for col in df_gt.columns if col != 'Speaker']

        print("label_cols: ", label_cols)

        for col in label_cols:
            y_true = df_gt[col]
            y_pred = df_test[col]

            acc    = accuracy_score(y_true, y_pred)
            recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
            precis = precision_score(y_true, y_pred, average='macro', zero_division=0)
            f1     = f1_score(y_true, y_pred, average='macro', zero_division=0)

            # Format to four decimal places
            results[col] = [f"{acc:.4f}", f"{precis:.4f}", f"{recall:.4f}", f"{f1:.4f}"]

    # Build DataFrame and save
    df_out = pd.DataFrame(results)
    df_out.to_csv(out_csv, index=False)
    print(f"✓ Saved results to {out_csv}")
