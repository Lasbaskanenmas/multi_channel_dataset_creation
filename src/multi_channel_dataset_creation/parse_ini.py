import argparse
import configparser
import json
import sys


def parse(inifile_path):
    config = configparser.ConfigParser()
    config.read(inifile_path)

    result = {}
    for section in config.sections():
        for key, value in config.items(section):
            if key in result:
                sys.exit(f"Duplicate key '{key}' found in multiple sections.")
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError as e:
                #print("failed to json convert :"+str(value))
                #print("making it into a string instead")
                result[key] = str(value)
    return result


def main():
    parser = argparse.ArgumentParser(description="Parse INI file and output JSON-parsed dictionary.")
    parser.add_argument("--ini_file", required=True, help="Path to the .ini file to parse.")
    args = parser.parse_args()

    parsed_dict = parse(args.ini_file)
    print(parsed_dict)


if __name__ == "__main__":
    main()
