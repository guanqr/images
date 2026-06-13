# -*- coding: utf-8 -*-
"""photo.toml 读写与排序"""
import os
import re


def parse_toml_entries(toml_path):
    """解析 TOML，返回条目列表 [{src, alt, category, ...}]"""
    entries = []
    if not os.path.exists(toml_path):
        return entries

    with open(toml_path, "r", encoding="utf-8") as f:
        content = f.read()

    for block in content.split("[[photo]]"):
        block = block.strip()
        if not block:
            continue
        entry = {}
        for line in block.split("\n"):
            m = re.match(r'^(\w+)\s*=\s*"([^"]*)"', line)
            if m:
                entry[m.group(1)] = m.group(2)
        if entry:
            entries.append(entry)

    return entries


def write_toml(toml_path, entries):
    """按 time 升序写入所有条目，无时间排最后"""
    def sort_key(e):
        t = e.get("time", "")
        return t if t else "z"

    entries.sort(key=sort_key)

    FIELDS = [
        "src", "alt", "category", "focus", "iso",
        "aperture", "shutter", "time", "place", "location",
    ]

    lines = []
    for i, entry in enumerate(entries):
        if i > 0:
            lines.append("")
        lines.append("[[photo]]")
        for f in FIELDS:
            lines.append(f'{f} = "{entry.get(f, "")}"')
        if entry.get("description"):
            lines.append(f'description = "{entry["description"]}"')

    lines.append("")

    with open(toml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
