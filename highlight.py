from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import TextLexer
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

# server-side syntax highlighting

# reference: https://git.kernel.org/pub/scm/infra/cgit.git/tree/filters/syntax-highlighting.py?id=dbaee2672be14374acb17266477c19294c6155f3
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

def get_highlight_blame_style():
    formatter = HtmlFormatter(style='sas', nobackground=True, cssclass='blame-code')
    return formatter.get_style_defs('.blame-code')

# highlight a single line (for blame)
def highlight_line(line, filename):
    formatter = HtmlFormatter(style='sas', nobackground=True, cssclass='blame-code')
    try:
        lexer = guess_lexer_for_filename(filename, line)
    except ClassNotFound:
        if line.startswith('#!'):
            lexer = guess_lexer(line)
        else:
            lexer = TextLexer()
    except TypeError:
        lexer = TextLexer()
    highlighted = highlight(line, lexer, formatter)
    # remove the outer div and pre
    # highlighted is <div class="blame-code"><pre>mirri</pre></div>
    # extract inner
    start = highlighted.find('<pre>') + 5 # length of <pre>, very hacky i know
    end = highlighted.find('</pre>')
    return highlighted[start:end]

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