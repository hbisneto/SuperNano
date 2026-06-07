# cli/parser.py

import sys
from ..cli.models import CLIArgs

def parse_cli_args() -> CLIArgs:
    args   = sys.argv[1:]
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

        if arg in ("-C", "--backupdir"):
            if i + 1 < len(args):
                result.backup_dir = args[i + 1]
                i += 2
            else:
                print(
                    "supernanno: option '-C/--backupdir' requires an argument",
                    file=sys.stderr,
                )
                result.invalid_arg = arg
                return result
            continue

        if arg.startswith("--backupdir="):
            result.backup_dir = arg.split("=", 1)[1]
            i += 1
            continue

        if arg.startswith("+"):
            # +LINE ou +LINE,COLUMN ou +/SEARCH
            rest = arg[1:]

            if rest.startswith("/"):
                result.search = rest[1:]
                i += 1
                continue

            if "," in rest:
                line_str, col_str = rest.split(",", 1)
                try:
                    result.line = int(line_str)
                except ValueError:
                    print(
                        f"supernanno: invalid line number '{line_str}' in argument '{arg}'",
                        file=sys.stderr,
                    )
                    # Mantém line=None, não aborta a abertura do arquivo

                try:
                    result.column = int(col_str)
                except ValueError:
                    print(
                        f"supernanno: invalid column number '{col_str}' in argument '{arg}'",
                        file=sys.stderr,
                    )
                    result.column = 0  # Fallback seguro
            else:
                try:
                    result.line = int(rest)
                except ValueError:
                    print(
                        f"supernanno: invalid line number '{rest}' in argument '{arg}'",
                        file=sys.stderr,
                    )
                    # Mantém line=None

            i += 1
            continue

        if arg.startswith("-"):
            result.invalid_arg = arg
            return result

        # Arquivo posicional
        result.file = arg
        i += 1

    return result
