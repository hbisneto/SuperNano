# cli/parser.py
import sys
from cli.models import CLIArgs

def parse_cli_args() -> CLIArgs:
    args = sys.argv[1:]
    result = CLIArgs()

    i = 0
    positional = []

    while i < len(args):
        arg = args[i]

        # Help / version
        if arg in ("-h", "--help"):
            result.help = True
            return result

        if arg in ("-V", "--version"):
            result.version = True
            return result

        # Read only
        if arg in ("-v", "--view"):
            result.view_mode = True
            i += 1
            continue

        # Backup enabled
        if arg in ("-B", "--backup"):
            result.backup = True
            i += 1
            continue

        # Backup dir
        if arg == "-C":
            if i + 1 < len(args):
                result.backup_dir = args[i + 1]
                i += 2
                continue

        if arg.startswith("--backupdir="):
            result.backup_dir = arg.split("=", 1)[1]
            i += 1
            continue

        positional.append(arg)
        i += 1

    if not positional:
        return result

    first = positional[0]

    # nano +25,8 file.txt
    if first.startswith("+"):
        position = first[1:]

        if position.startswith("/"):
            result.search = position[1:]
        else:
            if "," in position:
                line, col = position.split(",", 1)
                result.line = int(line)
                result.column = int(col)
            else:
                result.line = int(position)

        if len(positional) > 1:
            result.file = positional[1]
    else:
        result.file = first

    return result