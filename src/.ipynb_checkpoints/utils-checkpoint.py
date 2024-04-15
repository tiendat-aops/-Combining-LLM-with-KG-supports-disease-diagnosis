import os
import zipfile
import re
import csv


def write_to_txt(filename, content, output_path):
    """
    Write content to a text file.

    Args:
    - filename (str): The name of the PDF file.
    - content (str): The content to write to the text file.
    - output_path (str): The path where the text file will be saved.

    Returns:
    - None

    This function creates the output directory 'output' if it doesn't exist already.
    It then constructs the full output path based on the provided output_path.
    If the content is None, indicating an issue with retrieving the content, the function returns early without attempting to write to the file.
    Finally, it writes the content to a text file within the specified output directory, using the filename with the extension replaced with '.txt' as the filename.
    """
    if not os.path.exists("output"):
        os.makedirs("output")

    parent_path = os.path.join("", "output")

    if not os.path.exists(os.path.join(parent_path, output_path)):
        os.makedirs(os.path.join(parent_path, output_path))

    output_path = os.path.join(parent_path, output_path)

    if content is None:
        return

    with open(
        os.path.join(output_path, f"{filename.replace('.pdf', '')}.txt"), "w"
    ) as content_file:
        content_file.write(content)


def extract_zip(zip_file, extract_to):
    """
    Extracts a ZIP file into a directory.

    Args:
    - zip_file (str): The path to the ZIP file to extract.
    - extract_to (str): The path to the directory where the ZIP file will be extracted.
    """
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def replace_acronyms(input_str, abbr_list):
    """
    Replace acronyms in a string with their full meanings.

    Args:
    - input_str (str): The input string containing acronyms to be replaced.
    - abbr_list (dict): A dictionary where keys are acronyms and values are their full meanings.

    Returns:
    - str: The input string with acronyms replaced by their full meanings.
    """
    for acronym, full_meaning in abbr_list.items():
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(acronym) + r"(?![a-zA-Z0-9])"
        input_str = re.sub(pattern, full_meaning, input_str)
    return input_str


def write_to_csv(file_name, dict):
    with open(f"abbre_{file_name}.csv", "w", newline="") as csvfile:
        fieldnames = ["key", "value"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for key, value in dict.items():
            writer.writerow({"key": key, "value": value})


def replace_and_remove_newline(input_string):
    pattern = r"([^.])[ ]*\n"

    output_string = re.sub(pattern, r"\1 ", input_string)

    return output_string