from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DiffLexer
from pygments.lexers import TextLexer
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound

STYLE = "default"


# reference: https://git.kernel.org/pub/scm/infra/cgit.git/tree/filters/syntax-highlighting.py?id=dbaee2672be14374acb17266477c19294c6155f3
def _safe_lexer(content, filename):
    try:
        return guess_lexer_for_filename(filename, content)
    except ClassNotFound:
        if content.startswith("#!"):
            return guess_lexer(content)
        return TextLexer()
    except TypeError:
        return TextLexer()


def _formatter(*, linenos=False, cssclass=None, nowrap=False):
    formatter_kwargs = {
        "style": STYLE,
        "nobackground": True,
        "linenos": linenos,
        "nowrap": nowrap,
    }
    if cssclass:
        formatter_kwargs["cssclass"] = cssclass
    return HtmlFormatter(**formatter_kwargs)


# highlight code with filename-based lexer
def highlight_code(data, filename):
    formatter = _formatter(linenos=True)
    css = formatter.get_style_defs(".highlight")
    highlighted = highlight(data, _safe_lexer(data, filename), formatter)
    return f"<style>{css}</style>{highlighted}"


# get CSS styles for blame view
def get_highlight_blame_style():
    formatter = _formatter(cssclass="blame-code")
    return formatter.get_style_defs(".blame-code")


# highlight a single line of code with filename-based lexer
def highlight_line(line, filename):
    # Use nowrap to avoid wrapping in <div><pre>...</pre></div>
    formatter = _formatter(cssclass="blame-code", nowrap=True)
    return highlight(line, _safe_lexer(line, filename), formatter)


# highlight diff with DiffLexer
def highlight_diff(data):
    formatter = _formatter()
    highlighted = highlight(data, DiffLexer(), formatter)
    # gd = removed, gi = added, gh = hunk, gu = header
    highlighted = highlighted.replace('class="gd"', 'class="diff-removed"')
    highlighted = highlighted.replace('class="gi"', 'class="diff-added"')
    highlighted = highlighted.replace('class="gh"', 'class="diff-hunk"')
    highlighted = highlighted.replace('class="gu"', 'class="diff-header"')
    css = """
    .diff-added { color: green; }
    .diff-removed { color: red; }
    .diff-hunk { background-color: lightgray; }
    .diff-header { color: blue; font-weight: bold; }
    """
    return f"<style>{css}</style>{highlighted}"
