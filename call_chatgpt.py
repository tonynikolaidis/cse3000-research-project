import argparse
import os
import time
from pathlib import Path
from openai import OpenAI


def strip_backticks(csv_string: str) -> str:
    lines = csv_string.strip().splitlines()

    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Call ChatGPT")
    
    parser.add_argument('folder')
    parser.add_argument('-p', '--prompt', default="0")
    parser.add_argument('-m', '--model', default="chatgpt-4o-latest")

    args = parser.parse_args()

    hearing = args.folder
    path = f"hearings/{hearing}"
    prompt_type = int(args.prompt)
    model = f"{args.model}"

    client = OpenAI()

    prompts = ["every", "zero_shot", "few_shot", "zero_shot_cot", "few_shot_cot"]

    if not os.path.exists(f"{path}/output"):
        os.makedirs(f"{path}/output")

    if not os.path.exists(f"{path}/output/{model}"):
        os.makedirs(f"{path}/output/{model}")

    output_path = f"{path}/output/{model}"

    times_to_run = 1

    if prompt_type == 0:
        times_to_run = 4
        prompt_type = 1

    i = 0

    while i < times_to_run:
        prompt = Path(f"{path}/prompts/{prompts[prompt_type]}.txt").read_text(encoding="utf-8")

        print(f"✓ Calling {model} with {prompts[prompt_type]}")

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        output = response.output_text
        output_cleaned = strip_backticks(output)

        with open(f"{output_path}/{prompts[prompt_type]}.csv", mode="w") as file:
            file.write(output_cleaned)
        
        print(f"✓ Wrote response to {output_path}/{prompts[prompt_type]}.csv")

        i += 1
        prompt_type += 1

        if i < times_to_run:
            print("Pausing for 3 seconds...")
            time.sleep(3)
