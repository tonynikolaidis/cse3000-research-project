import os
import argparse
import shutil

def make_template():
    # Create new folder
    os.mkdir(path)

    # Create hearing.txt
    with open(f"{path}/hearing.txt", "w") as f:
        f.write("The cleaned hearing transcript goes here...")
    
    # Create topics.txt
    with open(f"{path}/topics.txt", "w") as f:
        f.write("Topic 1\nTopic 2\n...")

    # Create link.txt
    with open(f"{path}/link.txt", "w") as f:
        f.write("https://www.congress.gov/...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Create folder template for a new hearing")
    
    parser.add_argument('title')

    args = parser.parse_args()

    hearing = args.title
    path = f"hearings/{hearing}"
    
    try:
        make_template()
        print(f"✓ Template for '{hearing}' created successfully.")
    except FileExistsError:
        print(f"⨉ Warning: '{hearing}' already exists!", end=" ")
        user_input = input("Would you like to overwrite it? (Y/n) ")

        if (user_input.lower() == "y"):
            shutil.rmtree(f"{path}")
            make_template()
            print(f"✓ Template for '{hearing}' overwritten successfully.")

    except PermissionError:
        print(f"⨉ Permission denied: Unable to create '{hearing}'.")
    except Exception as e:
        print(f"⨉ An error occurred: {e}")