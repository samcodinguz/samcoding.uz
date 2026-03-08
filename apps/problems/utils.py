import re

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