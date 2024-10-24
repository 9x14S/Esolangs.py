import argparse
import pathlib

from esolangs_py.lang_list import IMPLEMENTED


def main(script: pathlib.Path, lang: str) -> None:
    if not script.exists():
        raise FileNotFoundError(f"File {script} could not be found.")

    # TO-DO: add lib functionality


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="All-in-one esolang interpreter")
    parser.add_argument("script", nargs=1, help="esolang script file")
    parser.add_argument(
        "-l", "--lang", "--language",
        help="name of the esolang (not required if the esolang has a distinct extension)",
        choices=tuple(IMPLEMENTED.values()),
        required=False
    )
    args = parser.parse_args()

    script_path = pathlib.Path(args.script)

    # args.lang is already constrained by the parser
    language = args.lang
    if language is None:
        extension = script_path.suffix
        language  = IMPLEMENTED.get(extension)
        if language is None:
            raise NotImplemented(f"'{extension}' language not recognized or supported.")

    main(script_path, language)
