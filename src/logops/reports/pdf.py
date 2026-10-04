"""HTML → PDF with the headless print mode of Microsoft Edge or Google Chrome (no new dependency).

The browser runs the page's scripts first (virtual time budget), so Plotly charts are drawn before
printing.
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)
NAMES = ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")
RENDER_BUDGET_MS = 20_000  # time the page's scripts get before printing
TIMEOUT_S = 180
PRINT_WIDTH_PX = 640  # A4 width less 20 mm margins at 96 dpi, so charts are laid out at print size


class NoBrowserError(RuntimeError):
    """Neither Edge nor Chrome was found, so no PDF can be made."""


def find_browser() -> str | None:
    for path in CANDIDATES:
        if Path(path).is_file():
            return path
    for name in NAMES:
        if found := shutil.which(name):
            return found
    return None


PAGE_TOKEN = re.compile(r"\[\[page:([\w-]+)\]\]")  # "[[page:fig-2-1]]": that element's page


def to_pdf(html: str) -> bytes:
    """Print the HTML to PDF. Page tokens (contents and lists of figures and tables) are filled in
    from a first print: the browser records the page of every link target in the PDF."""
    if not PAGE_TOKEN.search(html):
        return _print(html)
    draft = _print(PAGE_TOKEN.sub("00", html))  # same width as the final numbers
    where = destinations(draft)
    return _print(PAGE_TOKEN.sub(lambda m: str(where.get(m.group(1), "")), html))


def destinations(pdf: bytes) -> dict[str, int]:
    """Page number (1-based) of each named destination in a PDF printed by Edge or Chrome."""
    objects = {int(n): body for n, body in re.findall(rb"(\d+) 0 obj\s*(.*?)\s*endobj", pdf, re.S)}
    catalog = next((b for b in objects.values() if b"/Type /Catalog" in b), b"")
    root, dests = (re.search(rb"/%s (\d+) 0 R" % k, catalog) for k in (b"Pages", b"Dests"))
    if not root or not dests:
        return {}
    order: list[int] = []

    def walk(n: int) -> None:
        body = objects.get(n, b"")
        kids = re.search(rb"/Kids \[([^\]]*)\]", body)
        if b"/Type /Pages" in body and kids:
            for kid in re.findall(rb"(\d+) 0 R", kids.group(1)):
                walk(int(kid))
        else:
            order.append(n)

    walk(int(root.group(1)))
    page = {n: i for i, n in enumerate(order, start=1)}
    names = re.findall(rb"/([\w-]+) \[(\d+) 0 R", objects.get(int(dests.group(1)), b""))
    return {name.decode(): page[int(ref)] for name, ref in names if int(ref) in page}


def _print(html: str) -> bytes:
    browser = find_browser()
    if browser is None:
        raise NoBrowserError("Microsoft Edge or Google Chrome is required for PDF output")
    with tempfile.TemporaryDirectory() as tmp:
        page, out = Path(tmp) / "report.html", Path(tmp) / "report.pdf"
        page.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                f"--window-size={PRINT_WIDTH_PX},1100",
                "--no-pdf-header-footer",
                "--print-to-pdf-no-header",
                f"--virtual-time-budget={RENDER_BUDGET_MS}",
                f"--user-data-dir={Path(tmp) / 'profile'}",
                f"--print-to-pdf={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=TIMEOUT_S,
        )
        return out.read_bytes()
