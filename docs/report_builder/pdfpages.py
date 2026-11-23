"""Measure the real page of every TOC entry in a PDF and write pages.json."""
import json
import re
import sys

import pymupdf

pdf, toc_json, out = sys.argv[1:4]
toc = json.load(open(toc_json))
doc = pymupdf.open(pdf)
norm = lambda s: re.sub(r"\s+", " ", s).strip()
page_lines = []
for pg in doc:
    lines = [norm(l) for l in pg.get_text().split("\n") if l.strip()]
    page_lines.append([l for l in lines if not re.match(r"^(CPU-SOCA|CAC771|Project Title:|Page \d+ of \d+)", l)])

# first body page: first page whose first lines start with the first chapter heading
start = next(i for i, ls in enumerate(page_lines) if i > 5 and norm(toc[0][2]) in ls[:3])
marks, cur = [], start
for level, number, text in toc:
    text_n = norm(text)
    found = None
    for i in range(cur, len(page_lines)):
        ls = page_lines[i]
        cand = {text_n, norm(f"{number} {text}")} if number else {text_n}
        window = ls[:3] if level == 1 else ls
        if any(x in cand for x in window):
            found = i
            break
    if found is None:
        print("NOT FOUND:", level, number, text)
        found = cur
    marks.append(found + 1)
    cur = found
json.dump(marks, open(out, "w"))
print("first body page", start + 1, "entries", len(marks), "last", marks[-1])
