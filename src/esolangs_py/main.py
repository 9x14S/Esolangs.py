import argparse
import pathlib

from sys import exit, stderr

from esolangs_py.lang_list import IMPLEMENTED


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
            from esolangs_py.lib.brainfuck import interpret
        case _:
            return -1

    return interpret(script_contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="All-in-one esolang interpreter")
    parser.add_argument("script", nargs=1, help="esolang script file")
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
            raise NotImplemented(f"'{extension}' language not recognized or supported.")

    exit(main(script_path, language))
