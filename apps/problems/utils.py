import os
import re
import shutil
import zipfile
from django.conf import settings

def delete_test(problem):

    zip_path = problem.test_file.path
    folder_path = os.path.join(settings.MEDIA_ROOT, f"problems/test/{problem.id:04d}")
    
    problem.test_file.delete(save=False)
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    
    problem.save()

def unzip_tests(zip_path, id):

    path = os.path.join(settings.MEDIA_ROOT, f"{zip_path}/{id:04d}")

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path)

    return path

def validate_statement(statement):

    required_sections = [
        r"\Statement",
        r"\InputFile",
        r"\OutputFile",
        r"\Note"
    ]

    for section in required_sections:
        if section not in statement:
            return section

    return None

def parse_sections(text):

    sections = {
        "statement": "",
        "input": "",
        "output": "",
        "note": ""
    }

    parts = re.split(r'\\(Statement|InputFile|OutputFile|Note)', text)

    sections["statement"] = parts[0]

    for i in range(1, len(parts), 2):

        key = parts[i]
        value = parts[i+1]

        if key == "Statement":
            sections["statement"] = value
        elif key == "InputFile":
            sections["input"] = value
        elif key == "OutputFile":
            sections["output"] = value
        elif key == "Note":
            sections["note"] = value

    return sections

def replace_center(text):

    text = text.replace(r'\begin{center}', '<div class="text-center">')
    text = text.replace(r'\end{center}', '</div>')

    return text

def replace_images(text, problem):

    def repl(match):

        width = match.group(1)
        height = match.group(2)
        filename = match.group(3)

        img = problem.images.filter(original_name=filename).first()

        if not img:
            return ""

        style = ""

        if width:
            style += f"width:{width};"

        if height:
            style += f"height:{height};"

        return f'<img src="{img.image.url}" style="{style}" class="img-fluid"/>'

    pattern = r'\\includegraphics(?:\[w:(.*?)\])?(?:\[h:(.*?)\])?\{(.*?)\}'

    return re.sub(pattern, repl, text)

def parse_statement(text, problem):

    sections = parse_sections(text)

    for key in sections:

        sections[key] = replace_center(sections[key])
        sections[key] = replace_images(sections[key], problem)

    return sections