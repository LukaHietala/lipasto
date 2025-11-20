from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import TextLexer
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

# server-side syntax highlighting

# https://git.kernel.org/pub/scm/infra/cgit.git/tree/filters/syntax-highlighting.py?id=dbaee2672be14374acb17266477c19294c6155f3

def highlight_code(data, filename):
    formatter = HtmlFormatter(style='sas', nobackground=True, linenos=True)
    try:
        lexer = guess_lexer_for_filename(filename, data)
    except ClassNotFound:
        if data.startswith('#!'):
            lexer = guess_lexer(data)
        else:
            lexer = TextLexer()
    except TypeError:
        lexer = TextLexer()
    css = formatter.get_style_defs('.highlight')
    highlighted = highlight(data, lexer, formatter)
    return f'<style>{css}</style>{highlighted}'

# bare diff highlighting
def highlight_diff(data):
    formatter = HtmlFormatter(style='sas', nobackground=True)
    lexer = DiffLexer()
    highlighted = highlight(data, lexer, formatter)
    # replace default pygments classes with custom ones
    # classes are from pygments DiffLexer, generic tokens
    # gd = general deleted, gi = general inserted, gh = general hunk, gu = hunk header?
    # https://pygments.org/docs/tokens/
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
    return f'<style>{css}</style>{highlighted}'