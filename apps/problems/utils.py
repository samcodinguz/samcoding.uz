def validate_statement(statement):

    required_sections = [
        r"\InputFile",
        r"\OutputFile",
        r"\Example",
        r"\Note"
    ]

    for section in required_sections:
        if section not in statement:
            return section

    return None