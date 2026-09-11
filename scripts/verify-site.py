#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "site-public"
ALLOWLIST = PUBLIC / "publish-allowlist.txt"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.images = []
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.images.append((attrs["src"], attrs.get("alt")))
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


allowed = [line.strip() for line in ALLOWLIST.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
if len(allowed) != len(set(allowed)):
    fail("publish allowlist contains duplicate paths")

for rel in allowed:
    path = (PUBLIC / rel).resolve()
    if PUBLIC.resolve() not in path.parents or not path.is_file():
        fail(f"invalid or missing allowlist entry: {rel}")

for path in PUBLIC.rglob("*"):
    if not path.is_file() or path == ALLOWLIST:
        continue
    rel = path.relative_to(PUBLIC).as_posix()
    if rel not in allowed:
        fail(f"public file is not explicitly allowlisted: {rel}")

blocked_extensions = {".csv", ".doc", ".docx", ".eml", ".key", ".pdf", ".pem", ".pfx", ".xls", ".xlsx"}
for rel in allowed:
    if Path(rel).suffix.lower() in blocked_extensions:
        fail(f"confidential document type is not publishable: {rel}")

page = (PUBLIC / "index.html").read_text(encoding="utf-8")
parser = PageParser()
parser.feed(page)
parser.close()

if "Novara Data Centre Programme" not in "".join(parser.title):
    fail("page title is missing")
if 'name="robots" content="noindex,nofollow,noarchive"' not in page:
    fail("page-level noindex policy is missing")
for href in parser.links:
    if href.startswith("#") and href[1:] not in parser.ids:
        fail(f"internal link has no target: {href}")
for src, alt in parser.images:
    if not alt:
        fail(f"image is missing alt text: {src}")
    if src.startswith("/") and not (PUBLIC / src[1:]).is_file():
        fail(f"image asset is missing: {src}")

combined = "\n".join((PUBLIC / rel).read_text(encoding="utf-8", errors="ignore") for rel in allowed if Path(rel).suffix.lower() in {".html", ".css", ".js", ".txt"})
secret_patterns = [
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"\brnd_[A-Za-z0-9_-]{16,}\b",
    r"\bgh[oprsu]_[A-Za-z0-9]{20,}\b",
    r'"private_key"\s*:',
    r'"client_email"\s*:',
]
for pattern in secret_patterns:
    if re.search(pattern, combined):
        fail(f"possible credential in public build: {pattern}")

required_phrases = ["350 MW", "Phase 0", "PowerCo", "EquipmentCo", "governed data room"]
for phrase in required_phrases:
    if phrase not in page:
        fail(f"required programme statement is missing: {phrase}")

print(f"Verified public boundary and {len(parser.links)} page links")
