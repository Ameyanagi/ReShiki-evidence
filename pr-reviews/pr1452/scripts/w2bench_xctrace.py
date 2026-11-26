"""Fold an `xctrace export` time-profile table into flamegraph stacks for one process name.

Usage: python3 w2bench_xctrace.py EXPORT.xml PROCESS_SUBSTRING OUT.folded
Rows reference earlier elements by id (`ref="N"`); this resolves them while streaming.
Stacks are written root-first (inferno/flamegraph folded format), one line per unique stack.
"""

import collections
import sys
import xml.etree.ElementTree as ET


def main():
    path, want, out = sys.argv[1:4]
    by_id = {}  # id -> (tag, text-or-name)
    frames_of = {}  # backtrace id -> tuple of frame names (leaf first)
    stacks = collections.Counter()
    rows = kept = 0
    for event, elem in ET.iterparse(path, events=("end",)):
        tag = elem.tag
        if tag == "frame":
            if "id" in elem.attrib:
                by_id[elem.attrib["id"]] = elem.attrib.get("name") or elem.attrib.get("addr", "?")
        elif tag in ("process", "thread-state"):
            if "id" in elem.attrib:
                by_id[elem.attrib["id"]] = elem.attrib.get("fmt") or elem.text or ""
        elif tag == "backtrace":
            if "id" in elem.attrib:
                names = []
                for frame in elem.findall("frame"):
                    key = frame.attrib.get("id") or frame.attrib.get("ref")
                    names.append(by_id.get(key, "?"))
                frames_of[elem.attrib["id"]] = tuple(names)
        elif tag == "row":
            rows += 1
            process = elem.find("process")
            name = ""
            if process is not None:
                key = process.attrib.get("id") or process.attrib.get("ref")
                name = by_id.get(key, "")
            state = elem.find("thread-state")
            running = state is None or by_id.get(state.attrib.get("id") or state.attrib.get("ref"), "Running") == "Running"
            bt = elem.find("backtrace")
            if want in name and bt is not None and running:
                key = bt.attrib.get("id") or bt.attrib.get("ref")
                stack = frames_of.get(key)
                if stack:
                    stacks[";".join(reversed([s.replace(";", ":") for s in stack]))] += 1
                    kept += 1
            elem.clear()
    with open(out, "w") as f:
        for stack, n in stacks.most_common():
            f.write(f"{stack} {n}\n")
    print(f"rows={rows} kept={kept} unique={len(stacks)}", file=sys.stderr)


if __name__ == "__main__":
    main()
