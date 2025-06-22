import argparse
import json
import pandas as pd
from sklearn.metrics import cohen_kappa_score


def compute_cohens_kappa_from_csvs(path1: str, path2: str) -> dict:
    """
    Computes Cohen's Kappa for each stance target between two annotator CSVs.
    
    Args:
        path1 (str): File path to annotator 1's CSV.
        path2 (str): File path to annotator 2's CSV.
        
    Returns:
        dict: Mapping from stance target to Cohen's Kappa score.
    """
    # Load both CSVs
    df1 = pd.read_csv(path1, index_col=0)
    df2 = pd.read_csv(path2, index_col=0)
    
    if not df1.columns.equals(df2.columns) or not df1.index.equals(df2.index):
        raise ValueError("Both CSVs must have identical columns and row indices.")
    
    kappas = {}
    for col in df1.columns:
        labels1 = df1[col].tolist()
        labels2 = df2[col].tolist()
        kappa = cohen_kappa_score(labels1, labels2)
        kappas[col] = kappa
    
    return kappas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Calculate Cohen's Kappa")
    
    parser.add_argument('folder')
    parser.add_argument('-a', '--alpha', default="ground_truth_1.csv")
    parser.add_argument('-b', '--beta', default="ground_truth_2.csv")
    parser.add_argument('-o', '--output', default="ground_truth.csv")

    args = parser.parse_args()

    hearing = args.folder
    path = f"hearings/{hearing}"

    gt_1 = args.alpha
    gt_2 = args.beta

    output = f"{args.output}"

    kappas = compute_cohens_kappa_from_csvs(f"{path}/{gt_1}", f"{path}/{gt_2}")
    average_kappa = sum(kappas.values()) / len(kappas) if kappas else 0.0

    for target, kappa in kappas.items():
        print(f"{target}: Cohen's kappa = {kappa:.3f}")

    print(f"Average Kappa: {average_kappa:.3f}")

    result = {
        "per_topic_kappa": kappas,
        "average_kappa": average_kappa
    }
    
    with open(f"{path}/iaa.json", mode="w") as f:
        json.dump(result, f, indent=2)
