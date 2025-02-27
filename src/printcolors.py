import sys
import os

# Define color codes
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def has_colours(stream):
    """Check if the terminal supports colors."""
    if not (hasattr(stream, "isatty") and stream.isatty()):
        return False
    if os.name == "nt":  # Windows compatibility
        return True
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except Exception:
        return False


def printout(text, colour=WHITE):
    """Print colored text if the terminal supports it."""
    if has_colours(sys.stdout):
        seq = "\x1b[1;%dm%s\x1b[0m" % (30 + colour, text)
    else:
        seq = text
    sys.stdout.write(seq + "\n")
    sys.stdout.flush()  # Ensure immediate output
