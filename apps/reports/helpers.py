from reportlab.lib.units import mm
from reportlab.lib import colors


def _wrap_text(text: str, max_chars: int):
    """Simple word-wrap helper."""
    words = text.split()
    line = []
    length = 0
    for w in words:
        if length + len(w) + 1 > max_chars:
            yield " ".join(line)
            line = [w]
            length = len(w)
        else:
            line.append(w)
            length += len(w) + 1
    if line:
        yield " ".join(line)


def _draw_row(c, x, y, cells, col_widths, header=False):
    """Draw a simple table row."""
    c.setFont("Helvetica-Bold" if header else "Helvetica", 10)
    for text, col_w in zip(cells, col_widths):
        c.drawString(x, y, text)
        x += col_w
    if header:
        c.setStrokeColor(colors.black)
        c.line(20 * mm, y - 2, 190 * mm, y - 2)
