"""BrainFuck interpreter module

Specification for the language: https://brainfuck.org/brainfuck.html

Since the specification is vague, this interpreter is making these
design choices:
    1. If the instruction pointer reaches (last_instruction_index+1), the program exits.
    2. If the instruction pointer goes to (first_isntruction_index-1), the program crashes.
    3. If the data pointer moves outside the array boundaries, it crashes.
    4. Cell arithmetic supports overflow. 255 + 1 == 0 and 0 - 1 == 255
    5. If the program encounters a ',' command (read one byte) and stdin has reached
        and EOF, the byte at ARRAY[DPTR] will NOT be changed.
    6. The interpreter optionally recognizes the '#' (output state) command and the '!'
    (strip all other characters) command.
      6.1. The '!' command should always be the first command, and it will NOT be counted
            as part of the program (the first command after it will have index 0).
            (this is sort of irrelevant since the interpreter already ignores unset commands)
"""

from sys import stdin, stdout, stderr
from collections import deque

BF_DEFAULT_MEMORY_SIZE = 30_000
# The memory the language operates on
ARRAY = bytearray(BF_DEFAULT_MEMORY_SIZE)
# Instruction Pointer
IPTR  = 0
# Data Pointer
DPTR  = 0
# Jumps to and from opening/closing square brackets
JUMP_TABLE = {}
# Instruction buffer
INSTRUCTIONS: str

def move_forwards():
    """Move the data pointer forwards."""
    global DPTR
    DPTR += 1
    if DPTR >= BF_DEFAULT_MEMORY_SIZE:
        raise IndexError(f"Memory access outside boundary <{DPTR = }>.")

def move_backwards():
    """Move the data pointer backwards."""
    global DPTR
    DPTR -= 1
    if DPTR < 0:
        raise IndexError(f"Memory access outside boundary <{DPTR = }>.")

def increase_cell():
    """Increases the cell currently pointed at by DPTR by one.
    Handles overflow.
    """
    global ARRAY
    ARRAY[DPTR] = (ARRAY[DPTR]+1) & 0xFF

def decrease_cell():
    """Decreases the cell currently pointed at by DPTR by one.
    Handles overflow.
    """
    global ARRAY
    ARRAY[DPTR] = (ARRAY[DPTR]-1) & 0xFF

def jump_closing():
    """Checks if the current data cell is zero, if it is, it jumps over to the 
    corresponding (closing) square bracket.
    """
    global IPTR
    if ARRAY[DPTR] == 0:
        IPTR = JUMP_TABLE[IPTR]

def jump_opening():
    """Checks if the current data cell is NOT zero, if it isn't, it jumps over to the 
    corresponding (opening) square bracket.
    """
    global IPTR
    if ARRAY[DPTR] != 0:
        IPTR = JUMP_TABLE[IPTR]

def output_byte():
    """Outputs the byte currently pointed at by DPTR. Outputs to stdout and immediately
    flushes.
    """
    stdout.buffer.write(ARRAY[DPTR].to_bytes(1, "little"))

def input_byte():
    """Receives a single byte into the cell currently pointed at by DPTR.
    If EOF, keeps cell as-is. (Check design choices at the top of the file).
    """
    global ARRAY
    byte = stdin.read(1).encode("ascii")
    if byte != b'':
        ARRAY[DPTR] = byte[0]

def output_debug():
    """Prints to stderr some useful data for debugging. This function should be run when
    the interpreter encounters a '#' command and has been set up to recognize it.
    """
    dptr_minus_5 = DPTR - 5
    dptr_plus_5  = DPTR + 5
    start = dptr_minus_5 if dptr_minus_5 > 0 else DPTR - (5 - dptr_minus_5)
    end   = dptr_plus_5  if dptr_plus_5 < BF_DEFAULT_MEMORY_SIZE else DPTR + 4 - (dptr_minus_5 % BF_DEFAULT_MEMORY_SIZE)
    near_cells = [f"{val:x}" if idx + start != DPTR else f"{val:X}" for idx, val in enumerate(ARRAY[start:end])]
    print(
        f"{IPTR = :5}, {DPTR = :5}",
        f"{near_cells}",
        sep='\n',
        file=stderr,
    )


def filter_instructions(instructions: str, keep: set[str] | None):
    """Generator function that filters the instruction buffer and populates the jump table.
    """
    global JUMP_TABLE

    stack = deque()
    for idx, char in enumerate(instructions):
        match char:
            case '[':
                stack.append(idx)
            case ']':
                if len(stack) == 0:
                    raise SyntaxError(f"Missing opening bracket for ']' at {idx}")
                opening = stack.pop()
                JUMP_TABLE[idx] = opening
                JUMP_TABLE[opening] = idx
            case _:
                pass

        if keep is None:
            yield char

        elif char in keep:
            yield char

    if len(stack) != 0:
        for opening in stack:
            print(f"Missing closing bracket for '[' at {opening}", file=stderr)
        raise SyntaxError


COMMANDS = {
    '+': increase_cell,
    '-': decrease_cell,
    '>': move_forwards,
    '<': move_backwards,

    '.': output_byte,
    ',': input_byte,
    '[': jump_closing,
    ']': jump_opening,
}


def parse_instructions(
    instructions: str,
    strip_instructions: bool = False,
    dump_state: bool = False,
):
    """Receives the instructions read from the file, then optionally strips them ('!' command)
    and handles dumping state.

    Also populates the jump table and checks that all square brackets have opposites.
    """
    global INSTRUCTIONS

    if dump_state:
        global COMMANDS
        COMMANDS['#'] = output_debug 

    if strip_instructions and ARRAY[0]:
        keep = {*COMMANDS.keys()}
    else:
        keep = None

    INSTRUCTIONS = ''.join(filter_instructions(instructions, keep))


def run():
    """Runs the given program by calling each instruction's command and ignoring the
    character if it doesn't have one.

    Moving the instruction pointer lower than 0 causes an error and moving it higher than
    len(instructions) results in a clean exit.
    """
    global IPTR
    while IPTR != len(INSTRUCTIONS):
        if IPTR < 0:
            raise IndexError(f"Instruction pointer moved outside left boundary. {IPTR = }")

        command = COMMANDS.get(INSTRUCTIONS[IPTR])
        if command is not None:
            command()
        IPTR += 1


def interpret(
    script: str,
    strip_instructions: bool = False,
    dump_state: bool = False
) -> int:
    """Main interpreter function. Sets up the script to be run, and runs it.
    """
    parse_instructions(script, strip_instructions, dump_state)
    run()
    return 0
