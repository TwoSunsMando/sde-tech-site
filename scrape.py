#!/usr/bin/env python3
"""Convert SDE-Tech raw HTML pages to clean markdown.

Strategy:
  - Pull the page <h1> from the page-title section (or entry-title).
  - Extract HTML between <div class="entry-content"> and its closing comment.
  - For the homepage (empty entry-content), use the #frontpage-boxes block instead.
  - Walk the parsed HTML with html.parser and emit markdown for the tags we
    actually see on this site (Beaver Builder rich-text modules: p, ul, ol, li,
    h1-h6, strong, em, b, i, a, img, br, hr, span). Drop wrapper divs and
    presentational style attrs.
"""
import os
import re
import sys
from html.parser import HTMLParser
from html import unescape

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(RAW, "pages")

PAGES = [
    ("index", "html-index.html"),
    ("about-us", "html-about-us.html"),
    ("team-leaders", "html-team-leaders.html"),
    ("contact-us", "html-contact-us.html"),
    ("it-services", "html-it-services.html"),
    ("voip-phones", "html-voip-phones.html"),
    ("website-services", "html-website-services.html"),
    ("content-marketing", "html-content-marketing.html"),
    ("programming", "html-programming.html"),
]

INLINE = {"a", "strong", "b", "em", "i", "span", "img", "br", "code"}
BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
         "hr", "table", "tr", "td", "th", "blockquote", "section", "article"}


def slice_between(html: str, start_re: str, end_marker: str) -> str:
    m = re.search(start_re, html)
    if not m:
        return ""
    end = html.find(end_marker, m.end())
    if end < 0:
        return html[m.end():]
    return html[m.end():end]


def extract_h1(html: str) -> str:
    # Prefer the page-title section H1 (the breadcrumb header).
    m = re.search(r'<section[^>]*id="page-title"[^>]*>(.*?)</section>', html, re.S)
    block = m.group(1) if m else html
    m2 = re.search(r"<h1[^>]*>(.*?)</h1>", block, re.S)
    if not m2:
        return ""
    inner = re.sub(r"<[^>]+>", "", m2.group(1))
    return unescape(inner).strip()


def extract_entry_content(html: str) -> str:
    # Match the entry-content div and slice up to its end-marker comment.
    return slice_between(
        html,
        r'<div class="entry-content">',
        "<!-- .entry-content -->",
    ).strip()


def extract_frontpage_boxes(html: str) -> str:
    m = re.search(
        r'<div id="frontpage-boxes"[^>]*>(.*?)</div>\s*</div>\s*</div><!-- #main',
        html, re.S,
    )
    if m:
        return m.group(1)
    # Fallback: just grab from frontpage-boxes to entry-content.
    return slice_between(
        html, r'<div id="frontpage-boxes"[^>]*>', '<div id="primary"',
    )


class MarkdownConverter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.list_stack = []  # list of ("ul"|"ol", index)
        self.in_a = []  # stack of href strings
        self.skip_depth = 0  # >0 while inside <script>/<style>
        self.italic_skip_stack = []  # True if current <i> is an icon (skip emphasis)

    # --- buffer helpers ---
    def emit(self, s: str):
        if self.skip_depth:
            return
        self.out.append(s)

    def text_so_far(self) -> str:
        return "".join(self.out)

    def ensure_blank_line(self):
        text = self.text_so_far()
        if not text:
            return
        if text.endswith("\n\n"):
            return
        if text.endswith("\n"):
            self.out.append("\n")
        else:
            self.out.append("\n\n")

    def ensure_newline(self):
        text = self.text_so_far()
        if text and not text.endswith("\n"):
            self.out.append("\n")

    # --- HTMLParser hooks ---
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.skip_depth += 1
            return
        if tag == "br":
            self.emit("  \n")
            return
        if tag == "hr":
            self.ensure_blank_line()
            self.emit("---\n\n")
            return
        if tag == "img":
            src = attrs.get("src", "").strip()
            alt = attrs.get("alt", "").strip()
            if src:
                self.emit(f"![{alt}]({src})")
            return
        if tag == "a":
            self.in_a.append(attrs.get("href", "").strip())
            self.emit("[")
            return
        if tag in ("strong", "b"):
            self.emit("**")
            return
        if tag == "em":
            self.emit("*")
            return
        if tag == "i":
            cls = attrs.get("class", "")
            # Font Awesome / icon fonts: skip emphasis markers entirely.
            is_icon = any(c == "fa" or c.startswith("fa-") or c.startswith("icon-")
                          for c in cls.split())
            self.italic_skip_stack.append(is_icon)
            if not is_icon:
                self.emit("*")
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.ensure_blank_line()
            level = int(tag[1])
            self.emit("#" * level + " ")
            return
        if tag == "p":
            self.ensure_blank_line()
            return
        if tag == "ul":
            self.ensure_blank_line()
            self.list_stack.append(["ul", 0])
            return
        if tag == "ol":
            self.ensure_blank_line()
            self.list_stack.append(["ol", 0])
            return
        if tag == "li":
            self.ensure_newline()
            depth = max(0, len(self.list_stack) - 1)
            indent = "  " * depth
            if self.list_stack and self.list_stack[-1][0] == "ol":
                self.list_stack[-1][1] += 1
                self.emit(f"{indent}{self.list_stack[-1][1]}. ")
            else:
                self.emit(f"{indent}- ")
            return
        if tag == "blockquote":
            self.ensure_blank_line()
            self.emit("> ")
            return
        # Otherwise: drop wrapper tags (div, span, section, article, ...).
        # For known block-ish wrappers, ensure we don't run paragraphs together.
        if tag in BLOCK:
            self.ensure_newline()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            if self.skip_depth:
                self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "a":
            href = self.in_a.pop() if self.in_a else ""
            self.emit(f"]({href})")
            return
        if tag in ("strong", "b"):
            self.emit("**")
            return
        if tag == "em":
            self.emit("*")
            return
        if tag == "i":
            is_icon = self.italic_skip_stack.pop() if self.italic_skip_stack else False
            if not is_icon:
                self.emit("*")
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.emit("\n\n")
            return
        if tag == "p":
            self.emit("\n\n")
            return
        if tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            if not self.list_stack:
                self.emit("\n\n")
            else:
                self.ensure_newline()
            return
        if tag == "li":
            self.ensure_newline()
            return
        if tag == "blockquote":
            self.emit("\n\n")
            return
        if tag in BLOCK:
            self.ensure_newline()

    def handle_data(self, data):
        if self.skip_depth:
            return
        if not data:
            return
        # Inside a list, before the bullet is written, skip pure-whitespace text.
        text = data.replace(" ", " ")
        # Collapse internal whitespace runs but preserve a single space.
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        # Collapse newlines: any run becomes a single space within a block.
        text = re.sub(r"\s*\n+\s*", " ", text)
        if text.strip() == "":
            # Only emit a space if the previous char isn't already whitespace
            # and we're mid-line (avoid leading spaces).
            buf = self.text_so_far()
            if buf and not buf[-1].isspace():
                self.emit(" ")
            return
        self.emit(text)


def html_to_markdown(html: str) -> str:
    p = MarkdownConverter()
    p.feed(html)
    p.close()
    md = p.text_so_far()
    # Tidy: trim trailing spaces per line; collapse 3+ blank lines to 2.
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    # Squash stray spaces before punctuation introduced by joining.
    md = re.sub(r" +([,.;:!?])", r"\1", md)
    return md.strip() + "\n"


def convert_page(slug: str, src_html: str) -> tuple[str, dict]:
    title = extract_h1(src_html) or slug.replace("-", " ").title()
    body_html = extract_entry_content(src_html)
    notes = {"title": title, "body_empty": False, "used_frontpage_boxes": False,
             "image_srcs": []}

    def has_visible_text(h: str) -> bool:
        stripped = re.sub(r"<[^>]+>", "", h or "")
        return bool(unescape(stripped).strip())

    if not has_visible_text(body_html) and slug == "index":
        body_html = extract_frontpage_boxes(src_html)
        notes["used_frontpage_boxes"] = True
    if not has_visible_text(body_html):
        notes["body_empty"] = True
        body_md = ""
    else:
        body_md = html_to_markdown(body_html)
    # Collect image refs for diagnostics.
    notes["image_srcs"] = re.findall(r'<img[^>]+src="([^"]+)"', body_html)
    out = f"# {title}\n\n{body_md}".rstrip() + "\n"
    return out, notes


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = []
    for slug, fname in PAGES:
        path = os.path.join(RAW, fname)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        md, notes = convert_page(slug, html)
        out_path = os.path.join(OUT, f"{slug}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        summary.append((slug, len(md), notes))
    for slug, size, notes in summary:
        flags = []
        if notes["body_empty"]:
            flags.append("EMPTY-BODY")
        if notes["used_frontpage_boxes"]:
            flags.append("frontpage-boxes")
        imgs = notes["image_srcs"]
        print(f"{slug:<20} {size:>5}B  imgs={len(imgs):<2} {' '.join(flags)}")
        for s in imgs:
            print(f"    img: {s}")


if __name__ == "__main__":
    main()
