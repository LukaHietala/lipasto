from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import TextLexer
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
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