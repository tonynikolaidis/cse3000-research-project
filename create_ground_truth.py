import argparse
import json, csv


def parse_stance(st):
    if st == "Positive":
        return 1
    elif st == "Negative":
        return -1
    else:
        return 0


def parse_annotations(ann):
    segment = ann["data"]["text"]

    speaker = " ".join(segment.split()[:2]).rstrip("., ")

    stances = []

    for res in ann["annotations"][0]["result"]:
        if "choices" in res["value"]:
            stance = res["value"]["choices"][0]     # Positive, Negative, or Neutral
            stance_num = parse_stance(stance)       # 1, -1, or 0
            stances.append(stance_num)              # append to array

    return {
        "id": ann["id"],
        "speaker": speaker,
        "stances": stances,
        "segment": segment
    }


def parse_txt_to_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
    return lines


def create_ground_truth_table(list_of_topics, ground_truth):
    speaker_labels = {}
    individual_stances = {}

    for ann in ground_truth:
        id      = ann["id"]
        speaker = ann["speaker"]
        stances = ann["stances"]

        non_zero_stances = all(s == 0 for s in stances)
        if not non_zero_stances:
            # print("------------------")
            # print(f"> ID: {id}")
            # print(f"> SPEAKER: {speaker}")
            # print(f"> STANCES: {stances}")

            if speaker not in individual_stances:
                individual_stances[speaker] = []

            individual_stances[speaker].append({
                "id": id,
                "stances": stances
            })

        if speaker not in speaker_labels:
            speaker_labels[speaker] = []

            for _ in stances:
                speaker_labels[speaker].append(0)

        for i in range(0, len(stances)):
            speaker_labels[speaker][i] += stances[i]

    # print(individual_stances)
    columns = ','.join(["SPEAKER", "ID"]) + ',' + ','.join(list_of_topics)
    rows = [columns]

    for sp in individual_stances.keys():
        # rows.append(sp)

        for a in individual_stances[sp]:
            seg_id = a["id"]
            st     = ",".join(['+' if s == 1 else '-' if s == -1 else '.' for s in a["stances"]])

            rows.append(f"{sp},{seg_id},{st}")

    # final_rows = "\n".join(rows)
    # with open("./individual_stances.csv", mode="w") as f:
    #     f.write(final_rows)

    # Make CSV file
    header = ["Speaker"]

    for topic in list_of_topics:
        header.append(topic)

    speaker_labels_array = []

    for speaker in speaker_labels:
        arr = [speaker]

        for i in range(0, len(speaker_labels[speaker])):
            label = speaker_labels[speaker][i]
            clamped_label = max(-1, min(1, label))
            arr.append(clamped_label)

        speaker_labels_array.append(arr)

    return header, speaker_labels_array


def write_ground_truth(header, speaker_labels_array, folder=".", filename="ground_truth_table"):
    with open(f'{folder}/{filename}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(speaker_labels_array)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Hearing Ground Truth Creator")
    
    parser.add_argument('folder')
    parser.add_argument('-a', '--annotations', default="annotations_2.json")
    parser.add_argument('-t', '--topics', default="topics.txt")
    parser.add_argument('-o', '--output', default="ground_truth_2")

    args = parser.parse_args()

    hearing = args.folder
    path = f"hearings/{hearing}"
    label_studio_annotations = args.annotations
    topics = args.topics
    output = args.output

    # Opening JSON file
    f = open(f"{path}/{label_studio_annotations}")

    # returns JSON object as a dictionary
    data = json.load(f)

    ground_truth = []

    for ann in data:
        annotation = parse_annotations(ann)
        ground_truth.append(annotation)

    f.close()

    list_of_topics = parse_txt_to_list(f"{path}/{topics}")

    header, speaker_labels_array = create_ground_truth_table(list_of_topics, ground_truth)
    write_ground_truth(header, speaker_labels_array, folder=path, filename=output)

    print(f"✓ Created ground truth table ({path}/{output}.csv)")
