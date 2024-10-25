import argparse
import pathlib

from sys import exit, stderr

from lang_list import IMPLEMENTED


def main(script: pathlib.Path, lang: str) -> int:
    """Receives a script file, opens it as binary and passes it to the
    relevant lang interpreter. Returns and exits with the errocode of the
    interpreter.
    """

    with open(script, "r") as f:
        script_contents = f.read()

    print(f"Interpreting program of type '{lang}'", file=stderr)

    match lang:
        case "brainfuck":
            from lib.brainfuck import interpret
            return interpret(script_contents)
        case _:
            return -1



if __name__ == "__main__":
    # TODO: implement subparsers for each language
    parser = argparse.ArgumentParser(description="All-in-one esolang interpreter")
    parser.add_argument("script", help="esolang script file")
    parser.add_argument(
        "-l", "--lang", "--language",
        help="name of the esolang (not required if the esolang has a distinct extension)",
        type=str.lower,
        choices=tuple(IMPLEMENTED.values()),
        required=False
    )
    args = parser.parse_args()

    script_path = pathlib.Path(args.script)

    # args.lang is already constrained by the parser
    language = args.lang
    if language is None:
        extension = script_path.suffix.lower()
        language  = IMPLEMENTED.get(extension)
        if language is None:
            raise NotImplementedError(f"'{extension}' language not recognized or supported.")

    exit(main(script_path, language))
