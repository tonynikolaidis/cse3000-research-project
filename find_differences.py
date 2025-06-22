import argparse
import pandas as pd


def create_ground_truth(file1: str, file2: str, output_file: str):
    df1 = pd.read_csv(file1, index_col=0)
    df2 = pd.read_csv(file2, index_col=0)

    if not df1.columns.equals(df2.columns) or not df1.index.equals(df2.index):
        raise ValueError("CSV files must have matching rows and columns")

    ground_truth = df1.copy()

    for col in df1.columns:
        for idx in df1.index:
            val1 = df1.at[idx, col]
            val2 = df2.at[idx, col]
            ground_truth.at[idx, col] = val1 if val1 == val2 else "x"

    ground_truth.to_csv(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Create ground truth")
    
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

    create_ground_truth(f"{path}/{gt_1}", f"{path}/{gt_2}", f"{path}/{output}")
