#!/usr/bin/env python3
"""Resize three tmux columns while preserving the panes stacked within them."""

import re
import subprocess
import sys

# The middle and right columns split the remaining width equally.
LEFT_COLUMN_PERCENT = 56

GEOMETRY = r"\d+x\d+,\d+,\d+"
PANE = rf"{GEOMETRY},\d+"
STACK = re.compile(rf"({GEOMETRY})\[{GEOMETRY},(\d+)(?:,{PANE})*\]")
COLUMN = r"(\d+)x\d+,\d+,\d+,(\d+)"
THREE_COLUMNS = re.compile(rf"[0-9a-f]{{4}},{GEOMETRY}\{{{COLUMN},{COLUMN},{COLUMN}\}}")


def resize_columns(socket, window):
    tmux = ["tmux", "-S", socket]
    state = subprocess.check_output(
        [
            *tmux,
            "display-message",
            "-p",
            "-t",
            window,
            "#{window_zoomed_flag} #{window_layout}",
        ],
        text=True,
    )
    zoomed, _, layout = state.rstrip("\n").partition(" ")
    if zoomed == "1":
        subprocess.run(
            [
                *tmux,
                "display-message",
                "-t",
                window,
                "Unzoom the pane before resizing columns",
            ],
            check=True,
        )
        return

    # For width changes, any pane in a vertical stack represents the whole stack.
    while True:
        layout, count = STACK.subn(r"\1,\2", layout)
        if count == 0:
            break

    columns = THREE_COLUMNS.fullmatch(layout)
    if columns is None:
        subprocess.run(
            [
                *tmux,
                "display-message",
                "-t",
                window,
                "Resizing requires three side-by-side columns",
            ],
            check=True,
        )
        return

    left, left_pane, middle, _, right, right_pane = map(int, columns.groups())
    total = left + middle + right
    left_target = max(1, min((LEFT_COLUMN_PERCENT * total + 50) // 100, total - 2))
    right_target = (total - left_target) // 2

    # Shrink outer columns first to make room in the middle for either to grow.
    changes = [(left, left_target, left_pane), (right, right_target, right_pane)]
    commands = []
    for width, target, pane in sorted(
        changes, key=lambda change: change[1] - change[0]
    ):
        if width != target:
            commands.extend(["resize-pane", "-t", f"%{pane}", "-x", str(target), ";"])
    if commands:
        subprocess.run([*tmux, *commands[:-1]], check=True)


if __name__ == "__main__":
    resize_columns(*sys.argv[1:])
