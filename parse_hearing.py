import argparse
import re, json, textwrap
from pathlib import Path

# ----------------------------------------------------------------------
# tune this list if your corpus contains other titles
TITLES = (
    r"Dr\.|Mr\.|Ms\.|Mrs\.|Miss|Senator|Representative|Rep\.|Chair|Chairman|Chairwoman|Secretary|Gov\.|Adm\.|Gen\."
)

#   Dr. Smith. (optionally some text…)
SPEAKER_LINE = re.compile(
    rf"""
    ^\s*                                           # (possible indent)
    (?P<who>                                       # --- speaker name ---
        (?:{TITLES})\s+                            #   title
        [A-Z][A-Za-z.\-']+                         #   surname
        (?:\s+[A-Z][A-Za-z.\-']+)*                 #   optional extra names
    )
    \.\s*                                          # full stop after name
    (?P<rest>.*)                                   # any text that follows
    $""",
    re.VERBOSE,
)


def parse_hearing(raw: str) -> list[str]:
    """
    Turn a congressional-hearing transcript into
    ['<Speaker> <utterance>'], preserving paragraph breaks:
    - Lines within the same paragraph are joined with spaces.
    - Paragraphs start on lines indented by 4 spaces; those get separated by '\n'.
    """
    lines = textwrap.dedent(raw).splitlines()
    data: list[str] = []
    buf: list[str] = []
    speaker = None

    def flush():
        nonlocal buf, speaker, data
        if speaker and buf:
            paragraphs: list[str] = []
            current_para = None

            for line in buf:
                # If a line begins with 4 spaces, treat it as a new paragraph
                if line.startswith("    "):
                    # Save the previous paragraph (if any)
                    if current_para is not None:
                        paragraphs.append(current_para)
                    # Start a new paragraph, stripping that indent
                    current_para = line.lstrip()
                else:
                    # Continuation of the current paragraph (or first paragraph)
                    if current_para is None:
                        current_para = line
                    else:
                        # Join with a space, collapsing internal newlines
                        current_para += " " + line.strip()

            # Append the very last paragraph
            if current_para is not None:
                paragraphs.append(current_para)

            # Join paragraphs with a newline between them
            combined = "\n\n".join(p for p in paragraphs if p.strip())
            data.append(f"{speaker} {combined}")
            buf.clear()

    for ln in lines:
        m = SPEAKER_LINE.match(ln)
        if m:
            # New speaker → flush old buffer
            flush()
            speaker = m["who"]
            first_chunk = m["rest"].strip()
            if first_chunk:
                buf.append(first_chunk)
        else:
            # Preserve leading spaces so we can detect paragraph indents
            buf.append(ln.rstrip())

    # Flush the final speaker block
    flush()
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Hearing Parser into Label Studio")
    
    parser.add_argument('folder')
    parser.add_argument('-hr', '--hearing', default="hearing.txt")
    parser.add_argument('-o', '--output', default="hearing")

    args = parser.parse_args()

    folder = args.folder
    path = f"hearings/{folder}"
    hearing = args.hearing
    output = f"{args.output}.json"

    text = Path(f"{path}/{hearing}").read_text(encoding="utf-8")
    list_of_segments = parse_hearing(text)

    tasks = [
        {"id": i + 1, "text": segment}
        for i, segment in enumerate(list_of_segments)
    ]

    # JSON array
    Path(f"{path}/{output}").write_text(json.dumps(tasks, indent=2), "utf-8")

    print(f"✓ Ready for Label Studio ({path}/{output})")
