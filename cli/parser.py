# cli/parser.py

import sys
from cli.models import CLIArgs

def parse_cli_args() -> CLIArgs:
    args = sys.argv[1:]
    result = CLIArgs()

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("-h", "--help"):
            result.help = True
            return result

        if arg in ("-V", "--version"):
            result.version = True
            return result

        if arg in ("-v", "--view"):
            result.view_mode = True
            i += 1
            continue

        if arg in ("-B", "--backup"):
            result.backup = True
            i += 1
            continue

        if arg == "-C" and i + 1 < len(args):
            result.backup_dir = args[i + 1]
            i += 2
            continue

        if arg.startswith("--backupdir="):
            result.backup_dir = arg.split("=", 1)[1]
            i += 1
            continue
        
        if arg.startswith("--") and arg not in ("--help", "--version"):
            result.invalid_arg = arg
            return result

        # supernanno +25,8 file.txt
        if arg.startswith("+"):
            position = arg[1:]
            if position.startswith("/"):
                result.search = position[1:]
            else:
                if "," in position:
                    try:
                        line_str, col_str = position.split(",", 1)
                        result.line = int(line_str)
                        result.column = int(col_str)
                    except ValueError:
                        pass
                else:
                    try:
                        result.line = int(position)
                    except ValueError:
                        pass
        else:
            # É o nome do arquivo
            result.file = arg

        i += 1

    return result