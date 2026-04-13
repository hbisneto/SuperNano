# cli/parser.py
import sys
from cli.models import CLIArgs

def parse_cli_args() -> CLIArgs:
    args = sys.argv[1:]

    result = CLIArgs()

    if not args:
        return result

    first = args[0]

    # nano +25,8 file.txt
    if first.startswith("+"):
        position = first[1:]

        # +/search
        if position.startswith("/"):
            result.search = position[1:]

        # +25 or +25,8
        else:
            if "," in position:
                line, col = position.split(",", 1)
                result.line = int(line)
                result.column = int(col)
            else:
                result.line = int(position)

        if len(args) > 1:
            result.file = args[1]

    else:
        result.file = first

    return result