#!/usr/bin/env python3
"""One-shot fixup for bibl.bib: publisher names, journal caps, title acronyms, DOIs."""

import re

with open("bibl.bib", "r") as f:
    content = f.read()

original = content

# ── 1. Publisher / organization capitalization ────────────────────────────────
# --drop-all-caps (now removed from bibtex-tidy.sh) was converting IEEE→Ieee
# and ACM→Acm.  Fix the mangled values that are already in the file.
for field in ("publisher", "organization", "institution"):
    content = re.sub(rf"({field}\s*=\s*\{{)Ieee(\}})", r"\1IEEE\2", content)
    content = re.sub(rf"({field}\s*=\s*\{{)Acm(\}})", r"\1ACM\2", content)

content = content.replace(
    "publisher = {Ieee Computer Soc}",
    "publisher = {IEEE Computer Society}",
)

# ── 2. Journal name capitalization ────────────────────────────────────────────
journal_fixes = [
    ("journal = {IEEE access}", "journal = {IEEE Access}"),
    (
        "journal = {IEEE transactions on evolutionary computation}",
        "journal = {IEEE Transactions on Evolutionary Computation}",
    ),
    (
        "journal = {IEEE transactions on neural networks}",
        "journal = {IEEE Transactions on Neural Networks}",
    ),
    ("journal = {science}", "journal = {Science}"),
    ("journal = {Artificial life II}", "journal = {Artificial Life II}"),
    ("journal = {Artificial life}", "journal = {Artificial Life}"),
]
for old, new in journal_fixes:
    content = content.replace(old, new)

# ── 3. Series field ───────────────────────────────────────────────────────────
content = content.replace("series = {Sc15}", "series = {SC15}")

# ── 4. Protect acronyms in title fields ──────────────────────────────────────
# Hyphenated / special-char forms — processed FIRST (more specific wins).
# No word-boundary anchors; match exactly.
ACRONYMS_EXACT = [
    "SARS-CoV-2",
    "COVID-19",
    "NSGA-II",
    "CIFAR-10",
    "CS-2",
]

# Simple all-caps word forms — processed after the exact forms above.
# NOTE: "SARS" is intentionally omitted; in this bib it only appears as
# part of SARS-CoV-2, and the EXACT pass above already handles that.
ACRONYMS_WORD = [
    # Biology
    "DNA", "RNA", "HIV", "CRISPR",
    # CS / HPC / hardware
    "MPI", "HPC", "GPU", "CPU", "CUDA", "LLVM", "JIT", "IPU", "HW", "SW",
    # AI / ML / EC
    "AI", "ML", "GP", "GI", "GA",
    # Named systems / methods / datasets
    "MABE", "MODES", "ALIFE", "ISAL", "MAIDS", "CIPRES",
    "NERD", "EDGE", "NK", "OEE", "NSF", "ACCESS", "FAST",
    "ISPD", "OSF", "POET",
]


def protect_title(title: str) -> str:
    """Add {} around unprotected acronyms in a single-line title string.

    Strategy: apply the substitution to ALL occurrences (including already-
    braced ones), which turns {ACR} into {{ACR}}, then immediately collapse
    any {{ACR}} back to {ACR}.  This avoids placeholder tricks that can leave
    binary garbage when placeholders are inadvertently modified by the regex.
    """
    # Exact (hyphenated) forms first
    for acr in ACRONYMS_EXACT:
        pat = re.escape(acr)
        title = re.sub(pat, "{" + acr + "}", title)
        title = re.sub(r"\{\{" + pat + r"\}\}", "{" + acr + "}", title)

    # Word-boundary forms second
    for acr in ACRONYMS_WORD:
        pat = re.escape(acr)
        title = re.sub(r"\b" + pat + r"\b", "{" + acr + "}", title)
        title = re.sub(r"\{\{" + pat + r"\}\}", "{" + acr + "}", title)

    return title


def fix_title_line(line: str) -> str:
    m = re.match(r"(\s+title\s*=\s*\{)(.*?)(\},?)$", line)
    if m:
        new_inner = protect_title(m.group(2))
        if new_inner != m.group(2):
            return m.group(1) + new_inner + m.group(3)
    return line


content = "\n".join(fix_title_line(l) for l in content.split("\n"))

# ── 5. Add DOIs to entries that lack them ────────────────────────────────────
DOI_MAP = {
    "felsenstein1981evolutionary": "10.1007/BF01734359",
    "domingos2012few": "10.1145/2347736.2347755",
    "adami2006digital": "10.1038/nrg1771",
    "buckling2002role": "10.1038/nature01164",
    "antonio2017coevolutionary": "10.1109/TEVC.2017.2767023",
    "delsuc2005phylogenomics": "10.1038/nrg1603",
    "apprill2020role": "10.1146/annurev-marine-010419-010641",
    "cobb2013directed": "10.1002/aic.13995",
    "davies1987hypothesis": "10.1093/biomet/74.1.33",
    "colijn2014phylogenetic": "10.1093/emph/eou018",
    "burnham1979robust": "10.2307/1936861",
    "furber2014spinnaker": "10.1109/JPROC.2014.2304638",
    "del2019bio": "10.1016/j.swevo.2019.04.008",
    "gagliardi2019international": "10.1007/s42514-019-00002-y",
}


def inject_doi(entry_text: str, doi: str) -> str:
    """Insert a doi field into a BibTeX entry (before the closing brace)."""
    if re.search(r"^\s*doi\s*=", entry_text, re.MULTILINE | re.IGNORECASE):
        return entry_text
    # Insert doi field line before the final lone closing brace
    return re.sub(r"(\n\})$", f"\n  doi = {{{doi}}},\n}}", entry_text)


for key, doi in DOI_MAP.items():
    pattern = re.compile(
        r"(@\w+\{" + re.escape(key) + r",.*?\n\})",
        re.DOTALL,
    )
    content = pattern.sub(lambda m, d=doi: inject_doi(m.group(1), d), content)

# ── 6. Sanity check and write ─────────────────────────────────────────────────
# Verify no null bytes crept in
assert b"\x00" not in content.encode(), "BUG: null bytes in output!"

with open("bibl.bib", "w") as f:
    f.write(content)

added = len(content.splitlines()) - len(original.splitlines())
print(f"Done. {added:+d} lines net. No null bytes.")
