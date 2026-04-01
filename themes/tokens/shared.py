from rich.style import Style


def build_shared_tokens(palette):
    # Cor principal que você quer para TODAS as palavras reservadas
    kw = Style(color=palette["keyword"])

    return {
        # ==================== FORÇANDO KEYWORDS ====================
        "keyword": kw,

        # Todas as variações conhecidas de control flow
        "keyword.control": kw,
        "keyword.control.conditional": kw,   # if, else, elif
        "keyword.control.repeat": kw,        # for, while
        "keyword.control.return": kw,
        "keyword.control.exception": kw,     # try, except, finally, raise
        "keyword.control.flow": kw,          # break, continue, pass

        # Capturas específicas que aparecem muito
        "keyword.return": kw,
        "keyword.yield": kw,
        "keyword.async": kw,
        "keyword.lambda": kw,

        # if, else, for, while, try, except (muitas vezes caem aqui)
        "keyword.conditional": kw,
        "keyword.repeat": kw,
        "keyword.exception": kw,

        # Operadores palavra (is, not, and, or, in)
        "keyword.operator": kw,
        "operator.word": kw,
        "keyword.operator.logical": kw,
        "keyword.operator.word": kw,

        # Constantes built-in (None, True, False)
        "constant.builtin": Style(color=palette["constant"]),
        "boolean": Style(color=palette.get("boolean", palette["constant"])),

        # ==================== OUTROS (mantidos) ====================
        "function": Style(color=palette["function"]),
        "function.call": Style(color=palette["function"]),

        "class": Style(color=palette["type"]),
        "type": Style(color=palette["type"]),

        "variable": Style(color=palette["variable"]),
        "parameter": Style(color=palette.get("parameter", palette["variable"])),

        "string": Style(color=palette["string"]),
        "comment": Style(color=palette["comment"]),
        "number": Style(color=palette["number"]),

        "constant": Style(color=palette["constant"]),
        "decorator": Style(color=palette.get("decorator", palette["function"])),

        # Símbolos
        "operator": Style(color=palette.get("operator", "#D4D4D4")),
        "punctuation": Style(color=palette.get("operator", "#D4D4D4")),

        # Fallbacks finais
        "identifier": Style(color=palette["variable"]),
        "builtin": Style(color=palette["function"]),
    }