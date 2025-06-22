# Towards Automated Stance Detection in Congressional Hearings with Large Language Models

This repository contains the code and annotation framework used in the paper
**"Towards Automated Stance Detection in Congressional Hearings with Large Language Models"**
by Nikolaidis (2025).

## Overview

This project explores how large language models (LLMs) can be used to detect the stance of multiple speakers towards multiple topics within U.S. congressional hearing transcripts. The codebase includes:

* A novel framework for annotating speaker-topic stance
* Scripts for preprocessing hearing transcripts
* Prompt templates for zero-shot, few-shot, and chain-of-thought (CoT) prompting
* Evaluation scripts
* Statistical significance tests

## Directory Structure

```
.
├── hearings/           # Dataset of transcripts
├── prompts/            # Prompt components
└── results/            # Output from experiments
```

## Setup

Install the Python dependencies by running:

```bash
pip install -r requirements.txt
```

I used Label Studio to annotate the hearings in the dataset. Installation instructions can be found [here](https://labelstud.io/guide/quick_start).

## Usage

Before proceeding with the following steps, it's recommended to remove all non-dialogue elements from transcripts.

### Preprocessing

Segment a cleaned hearing transcript into speaker turns:

```bash
python parse_hearing.py <folder>
```

The output is in JSON format, which you can directly import into Label Studio.

### Create the Annotation Interface for Label Studio

First, create a TXT file with the topics that you want to annotate stance towards. The format of the file must be as follows:

```txt
Topic 1
Topic 2
.
.
.
```

Then, run the following script:

```bash
python create_xml.py <folder>
```

The script will create the XML code for the annotation interface of Label Studio. At this point, you can manually assign stances for each segment of the hearing.

### Create the Ground Truth

After labelling the transcript, export the annotations into the folder of the hearing. Then, run the following script to produce a CSV file with the ground truth:

```bash
python create_ground_truth.py <folder>
```

### Test with an LLM

After creating the ground truth for the hearing, you can test any LLM using OpenAI's API. Don't forget to add your API key to shell configuration file (e.g. `.bashrc`, `.zshrc`).

```bash
python call_chatgpt.py --model chatgpt-4o --prompt <0, 1, 2, 3, or 4>
```

- `0`: Test will all four prompts
- `1`: zero-shot
- `2`: few-shot
- `3`: cot-zero-shot
- `4`: cot-few-shot

### Evaluation

Evaluate model predictions against ground truth:

```bash
python evaluate.py <folder>
```

Or, if you want to evaluate all hearings in the corpus, run:

```bash
python evaluate_all_hearings.py
```

### Significance Tests
You can test for statistical significance of results by running:

```bash
python bootstrap.py
```

## Inter-annotator Agreement

If you have multiple sets of annotations, you can compare their corresponding ground truth CSV files by running:

```bash
python find_differences.py --alpha <ground_truth_1.csv> --beta <ground_truth_2.csv>
```

Any values that are different between the two ground truths will be set to `X` in the resulting ground truth CSV.

### Cohen's κ
You can calculate the inter-annotator agreement score (Cohen's κ) of the entire corpus by running the following script:

```bash
python calculate_iaa_avg.py
```

## Citation

If you use this codebase, please cite the corresponding paper:

```
Nikolaidis. "Towards Automated Stance Detection in Congressional Hearings with Large Language Models." 2025.
```

## License

MIT License
