import sys
import re
import pandas as pd

# usage: python convert_v2.py <input_csv_or_xlsx> <template_html> <output_html>
input_file = sys.argv[1] if len(sys.argv) > 1 else "glossary_input.csv"
template_file = sys.argv[2] if len(sys.argv) > 2 else "template_working.html"
output_file = sys.argv[3] if len(sys.argv) > 3 else "glossary_output.html"

ITALIC_PHRASE = "երբեմն նաև՝"

if input_file.endswith(".csv"):
    df = pd.read_csv(input_file, header=None)
else:
    df = pd.read_excel(input_file, header=None)

def italicize(text: str) -> str:
    return text.replace(ITALIC_PHRASE, f"<i>{ITALIC_PHRASE}</i>")

# matches "1." or "1․" (Armenian full stop U+0589) followed by whitespace
NUM_MARKER = r"\d+[․.]\s"

def numbered_to_list(text: str) -> str:
    # only convert if text starts with "1. " (or "1․ ") and a "2. " marker exists later
    if not re.match(rf"^\s*1[․.]\s", text):
        return text
    if not re.search(rf"(?<!\d)2[․.]\s", text):
        return text
    # split before each "N. " marker, optionally consuming preceding comma+whitespace
    parts = re.split(rf"\s*,?\s*(?={NUM_MARKER})", text)
    items = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        p = re.sub(rf"^{NUM_MARKER}", "", p).rstrip(", ").strip()
        if p:
            items.append(p)
    if len(items) < 2:
        return text
    lis = "".join(f"<li>{it}</li>" for it in items)
    return f'<ol style="margin:0;padding-left:0;list-style-position:inside;">{lis}</ol>'

rows = []
for _, row in df.iterrows():
    term = str(row.iloc[0])
    translation = str(row.iloc[1])
    if term.strip().lower() == "nan" or translation.strip().lower() == "nan":
        continue
    term_html = italicize(numbered_to_list(term))
    translation_html = italicize(numbered_to_list(translation)).replace("\n", "<br>")
    rows.append(f"<tr><td><b>{term_html}</b></td><td>{translation_html}</td></tr>")
    print(f"Added term: {term}")

rows_html = "\n      ".join(rows)

with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

new_tbody = f"<tbody>\n      {rows_html}\n    </tbody>"
final_html, n = re.subn(
    r"<tbody>.*?</tbody>",
    lambda m: new_tbody,
    template,
    count=1,
    flags=re.DOTALL,
)

if n == 0:
    raise RuntimeError("Could not find <tbody>...</tbody> in template")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Saved {len(rows)} rows into {output_file}")

# տալիս ես ֆայլ, էրկու սյունակով՝ term դիմացը translation, ու կանչում
# python convert_v2.py glossary_input.csv template_working.html glossary_output.html
