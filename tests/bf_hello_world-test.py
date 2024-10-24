import sys

from io import BytesIO

from esolangs_py.lib.brainfuck import interpret

with open("hello_world.bf", "r") as f:
    output_buffer = BytesIO()
    sys.stdout = output_buffer
    interpret(f.read())
    print(output_buffer)
