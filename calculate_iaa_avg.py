import os
import json

def compute_average_kappa_across_hearings(base_dir: str = "hearings") -> float:
    kappa_values = []

    for hearing in os.listdir(base_dir):
        hearing_path = os.path.join(base_dir, hearing)
        iaa_path = os.path.join(hearing_path, "iaa.json")

        if os.path.isdir(hearing_path) and os.path.isfile(iaa_path):
            with open(iaa_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                avg_kappa = data.get("average_kappa", None)
                if avg_kappa is not None:
                    kappa_values.append(avg_kappa)

    if not kappa_values:
        print("No valid average_kappa values found.")
        return 0.0

    overall_avg = sum(kappa_values) / len(kappa_values)
    print(f"Average kappa across {len(kappa_values)} hearings: {overall_avg:.4f}")
    return overall_avg

compute_average_kappa_across_hearings("hearings")
