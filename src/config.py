"""
Configuration module to read database connection parameters from an INI file.
"""

from configparser import ConfigParser

def config(filename="src/database.ini", section="postgresql"):
    """
    Reads configuration from an INI file and returns a dictionary of database connection parameters.

    :param filename: Path to the INI file containing database connection details.
    :param section: Section within the INI file to read.
    :return: Dictionary of database connection parameters.
    """
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file.')
    return db