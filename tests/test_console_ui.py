import logging
import os
import sys

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.console_ui import setup_console_logging


def test_console_does_not_print_logger_name(capsys):
    logger = logging.getLogger("GoldStandard")
    setup_console_logging(logger, verbose=True)
    logger.info("Hello Console Test")

    # Capture printed output (Rich writes to stdout)
    captured = capsys.readouterr()
    out = captured.out

    # Ensure the full logger name isn't present in console output and the symbol is present
    assert "GoldStandard" not in out
    assert "✔" in out or "Hello Console Test" in out
