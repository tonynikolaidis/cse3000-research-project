import argparse
import csv
from pathlib import Path
import os


def parse_txt_to_list(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="Create Labelling Template for Label Studio",
                    description="What the program does",
                    epilog="Text at the bottom of help")
    
    parser.add_argument('folder')
    parser.add_argument('-g', '--ground', default="ground_truth.csv")
    parser.add_argument('-a', '--transcript', default="hearing.txt")
    parser.add_argument('-t', '--topics', default="topics.txt")
    parser.add_argument('-p', '--prompt', default="0")

    args = parser.parse_args()

    hearing = args.folder
    path = f"hearings/{hearing}"
    ground_truth = args.ground
    topics = args.topics
    prompt_type = int(args.prompt)
    transcript = args.transcript

    prompts = ["every", "zero_shot", "few_shot", "zero_shot_cot", "few_shot_cot"]

    prompt = prompts[prompt_type]

    task = Path(f"prompts/base.txt").read_text(encoding="utf-8")

    output_format = Path(f"prompts/output.txt").read_text(encoding="utf-8")

    list_of_speakers = []

    with open(f"{path}/{ground_truth}", mode='r') as file:
        csv_file = csv.reader(file)
        next(csv_file, None)    # Skip header line
        for lines in csv_file:
            list_of_speakers.append(lines[0])

    list_of_topics = parse_txt_to_list(f"{path}/{topics}")

    hearing_transcript = Path(f"{path}/{transcript}").read_text(encoding="utf-8")

    if not os.path.exists(f"{path}/prompts"):
        os.makedirs(f"{path}/prompts")

    times_to_run = 1

    if prompt_type == 0:
        times_to_run = 4
        prompt_type = 1

    i = 0

    while i < times_to_run:
        with open(f"{path}/prompts/{prompts[prompt_type]}.txt", mode="w") as file:
            file.write(task + "\n\n")

            if prompt_type == 1:   # zero-shot
                pass
            
            elif prompt_type == 2: # few-shot
                file.write("EXAMPLES\n")
                examples = Path(f"prompts/examples.txt").read_text(encoding="utf-8")
                file.write(examples + "\n\n")

            elif prompt_type == 3: # zero-shot-cot
                file.write("REASONING\n")
                reasoning = Path(f"prompts/cot.txt").read_text(encoding="utf-8")
                file.write(reasoning + "\n\n")

            elif prompt_type == 4: # few-shot-cot
                file.write("EXAMPLES\n")
                examples = Path(f"prompts/examples.txt").read_text(encoding="utf-8")
                file.write(examples + "\n\n")

                file.write("REASONING\n")
                reasoning = Path(f"prompts/cot.txt").read_text(encoding="utf-8")
                file.write(reasoning + "\n\n")
                
            else:
                raise Exception("Incorrect prompt type")

            file.write("OUTPUT FORMAT\n")
            file.write(output_format + "\n\n")

            file.write("LIST OF SPEAKERS\n")
            speakers = ", ".join(list_of_speakers) + "\n\n"
            file.write(speakers + "\n")

            file.write("LIST OF TOPICS\n")
            topics = ", ".join(list_of_topics) + "\n\n"
            file.write(topics + "\n")

            file.write("HEARING TRANSCRIPT\n")
            file.write(hearing_transcript)
        
        print(f"✓ Created {prompts[prompt_type]} prompt ({path}/{prompts[prompt_type]}.txt)")

        i += 1
        prompt_type += 1
    