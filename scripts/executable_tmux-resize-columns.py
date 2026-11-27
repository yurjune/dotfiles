#!/usr/bin/env python3
"""Resize two or three tmux columns while preserving stacked panes."""

import json
import re
import subprocess
import sys

# In a three-column layout, the outer columns split the remaining width evenly.
MIDDLE_COLUMN_PERCENT = 60

GEOMETRY = r"\d+x\d+,\d+,\d+"
PANE = rf"{GEOMETRY},\d+"
STACK = re.compile(rf"({GEOMETRY})\[{GEOMETRY},(\d+)(?:,{PANE})*\]")
COLUMN = re.compile(r"(\d+)x\d+,\d+,\d+,(\d+)")
HORIZONTAL_LAYOUT = re.compile(
    rf"[0-9a-f]{{4}},{GEOMETRY}\{{({COLUMN.pattern}(?:,{COLUMN.pattern}){{1,2}})\}}"
)


def read_columns(layout):
    if layout.startswith("{"):
        root = json.loads(layout)["L"]
        if root["t"] != "h" or len(root["c"]) not in (2, 3):
            return None
        columns = []
        for column in root["c"]:
            panes = column["c"] if column["t"] == "v" else [column]
            if not panes or any(pane["t"] != "p" for pane in panes):
                return None
            columns.append((column["w"], panes[0]["I"]))
        return columns

    # For width changes, any pane in a vertical stack represents the whole stack.
    while True:
        layout, count = STACK.subn(r"\1,\2", layout)
        if count == 0:
            break
    match = HORIZONTAL_LAYOUT.fullmatch(layout)
    if match is None:
        return None
    return [(int(width), f"%{pane}") for width, pane in COLUMN.findall(match[1])]


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

    columns = read_columns(layout)
    if columns is None:
        subprocess.run(
            [
                *tmux,
                "display-message",
                "-t",
                window,
                "Resizing requires two or three side-by-side columns",
            ],
            check=True,
        )
        return

    left, left_pane = columns[0]
    total = sum(width for width, _ in columns)
    if len(columns) == 2:
        left_target = min((3 * total + 2) // 4, total - 1)
        changes = [(left, left_target, left_pane)]
    else:
        right, right_pane = columns[-1]
        middle_target = max(1, min((MIDDLE_COLUMN_PERCENT * total + 50) // 100, total - 2))
        left_target = (total - middle_target) // 2
        right_target = total - middle_target - left_target
        changes = [(left, left_target, left_pane), (right, right_target, right_pane)]

    # Shrink outer columns first to make room in the middle for either to grow.
    commands = []
    for width, target, pane in sorted(
        changes, key=lambda change: change[1] - change[0]
    ):
        if width != target:
            commands.extend(["resize-pane", "-t", pane, "-x", str(target), ";"])
    if commands:
        subprocess.run([*tmux, *commands[:-1]], check=True)


if __name__ == "__main__":
    resize_columns(*sys.argv[1:])
