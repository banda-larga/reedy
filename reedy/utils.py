import re
import xml.etree.ElementTree as ET
from html import escape
from typing import Any, Callable, Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, NavigableString

PHOTO_RE = re.compile(r"Foto: ©")


def tei_to_html(xml_string: str) -> str:
    root = ET.fromstring(xml_string)

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="it">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{escape(root.get("title", ""))}</title>',
        f'<meta name="author" content="{escape(root.get("author", ""))}">',
        f'<meta name="description" content="{escape(root.get("description", ""))}">',
        "<style>",
        "body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }",
        "pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }",
        "code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }",
        "</style>",
        "</head>",
        "<body>",
    ]

    if main := root.find("main"):
        html_parts.extend(process_element(main))

    html_parts.extend(["</body>", "</html>"])

    return "\n".join(html_parts)


def process_element(element: ET.Element) -> List[str]:
    tag_processors: Dict[str, Callable] = {
        "head": lambda e: [
            f'<{e.get("rend", "h2").lower()}>{escape(e.text or "")}</{e.get("rend", "h2").lower()}>'
        ],
        "p": lambda e: ["<p>"] + process_mixed_content(e) + ["</p>"],
        "list": process_list,
        "code": lambda e: ["<pre><code>", escape(e.text or ""), "</code></pre>"],
    }

    return tag_processors.get(
        element.tag, lambda e: [part for child in e for part in process_element(child)]
    )(element)


def process_list(element: ET.Element) -> List[str]:
    list_type = "ul" if element.get("rend") == "ul" else "dl"
    html_parts = [f"<{list_type}>"]

    for item in element:
        if list_type == "ul":
            item_content = "".join(process_mixed_content(item))
            html_parts.append(f"<li>{item_content}</li>")
        else:
            tag = "dt" if item.get("rend", "").startswith("dt") else "dd"
            item_content = "".join(process_mixed_content(item))
            html_parts.append(f"<{tag}>{item_content}</{tag}>")

    html_parts.append(f"</{list_type}>")
    return html_parts


def process_mixed_content(element: ET.Element) -> List[str]:
    parts = []
    if element.text:
        parts.append(escape(element.text))

    for child in element:
        parts.extend(
            ["<code>", escape(child.text or ""), "</code>"]
            if child.tag == "code"
            else process_element(child)
        )
        if child.tail:
            parts.append(escape(child.tail))

    return parts


def get_ext(node_str: str) -> str:
    patterns = [r"(highlight-source-|language-)([a-z]+)", r'class="([a-z]+)']

    for pattern in patterns:
        if match := re.search(pattern, node_str):
            return match.group(2) if len(match.groups()) > 1 else match.group(1)

    return ""


def format_code(node: BeautifulSoup) -> str:
    return f"\n```\n{''.join(node.stripped_strings)}\n```" if node.name == "pre" else ""


def convert_to_standard_code_block(html_string: str) -> str:
    soup = BeautifulSoup(html_string, "html.parser")

    if not (code_element := soup.find("code")):
        return ""

    language = code_element.get("data-language", "")
    code = "\n".join(
        "".join(s.text for s in span.find_all("span"))
        for span in code_element.find_all("span", {"data-line": True})
    )

    return f"```{language}\n{code}\n```"


def code_standardization(html: str) -> str:
    """Standardize code blocks."""
    soup = BeautifulSoup(html, "html.parser")
    for fig in soup.find_all("figure"):
        fig.replace_with(convert_to_standard_code_block(str(fig)))

    for pre in soup.find_all("pre"):
        pre.replace_with(format_code(pre))

    content = re.sub(
        r"```(\w+)\n(.*?)\n```",
        lambda m: f'<pre><code class="language-{m.group(1)}">\n{m.group(2)}\n</code></pre>',
        str(soup),
        flags=re.DOTALL,
    )
    content = re.sub(
        r"```\n(.*?)\n```", r"<pre><code>\n\1\n</code></pre>", content, flags=re.DOTALL
    )

    return content


def to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    def process_element(element):
        if isinstance(element, NavigableString):
            return element.strip()

        def _process_dl(dl: BeautifulSoup) -> str:
            dt = dl.find("dt")
            dt = f"**{dt.get_text().strip()}**" if dt else ""
            return (
                f"{dt}\n\n"
                + "".join(
                    f"- {process_element(dd)}\n"
                    for dd in dl.find_all("dd", recursive=False)
                    if process_element(dd)
                )
                + "\n"
            )

        processors = {
            "h1": lambda e: f"# {e.get_text().strip()}\n\n",
            "h2": lambda e: f"\n## {e.get_text().strip()}\n\n",
            "h3": lambda e: f"\n### {e.get_text().strip()}\n\n",
            "h4": lambda e: f"\n#### {e.get_text().strip()}\n\n",
            "h5": lambda e: f"\n##### {e.get_text().strip()}\n\n",
            "p": lambda e: f"{' '.join(process_element(child) for child in e.children)}\n\n",
            "ul": lambda e: "".join(
                f"- {process_element(li)}\n"
                for li in e.find_all("li", recursive=False)
                if process_element(li)
            )
            + "\n",
            "dl": lambda e: _process_dl(e),
            "ol": lambda e: "".join(
                f"{i+1}. {process_element(li)}\n"
                for i, li in enumerate(e.find_all("li", recursive=False))
            )
            + "\n",
            "pre": lambda e: (
                f"```{e.find('code').get('class', [''])[0].replace('language-', '') if e.find('code') and e.find('code').get('class') else ''}\n"
                f"{e.get_text().strip()}\n"
                f"```\n\n"
            ),
            "code": lambda e: (
                f"`{e.get_text().strip()}`"
                if e.parent.name != "pre"
                else e.get_text().strip()
            ),
            "strong": lambda e: f"**{e.get_text().strip()}**",
            "b": lambda e: f"**{e.get_text().strip()}**",
            "em": lambda e: f"*{e.get_text().strip()}*",
            "i": lambda e: f"*{e.get_text().strip()}*",
            "a": lambda e: f"[{e.get_text().strip()}]({e.get('href', '')})",
            "img": lambda e: f"![{e.get('alt', '')}]({e.get('src', '')})\n\n",
        }

        return processors.get(
            element.name,
            lambda e: "".join(process_element(child) for child in e.children),
        )(element)

    markdown = "".join(process_element(element) for element in soup.body.children)

    markdown = "\n".join(
        line for line in markdown.split("\n") if not PHOTO_RE.search(line)
    )

    markdown = markdown.replace("` :", "`:")
    markdown = markdown.replace("` ,", "`,")
    markdown = markdown.replace("` .", "`.")
    return re.sub(r"\n{3,}", "\n\n", markdown).strip()


def format_metadata(metadata: Dict[str, Any], separator: str = "---") -> str:
    key_mapping = {"categories": "Categories", "tags": "Tags", "date": "Date"}

    formatted_parts = []

    if "title" in metadata:
        formatted_parts.append(f"Title: {metadata['title']}\n")

    if "description" in metadata and metadata["description"]:
        formatted_parts.append(f"Snippet: {metadata['description']}\n")

    for key, display_name in key_mapping.items():
        if key in metadata and metadata[key]:
            if key == "date":
                value = metadata[key]

            elif key == "categories":
                value = ", ".join(metadata[key])

            elif key == "tags":
                if len(metadata[key]) > 1:
                    value = ", ".join([t.strip() for t in metadata[key] if t])
                else:
                    value = ", ".join(
                        [t.strip() for t in metadata[key][0].split(",") if t]
                    )
            formatted_parts.append(f"{display_name}: {value}\n")

    return "\n".join(formatted_parts) + f"\n{separator}\n\n"


def is_safe_url(url: str, allowed_schemes: List[str] = ["http", "https"]) -> bool:
    """Check if safeeee."""
    try:
        result = urlparse(url)
        return result.scheme in allowed_schemes and all([result.netloc, result.scheme])
    except:
        return False


def meme(
    html: str,
    base_url: str = "",
    links: bool = False,
    images: bool = False,
    emphasis: bool = True,
) -> str:
    conversions = {
        "emphasis": [
            (r"<(strong|b)>(.*?)</\1>", r"**\2**"),
            (r"<(em|i)>(.*?)</\1>", r"*\2*"),
        ],
        "links": [
            (
                r'<a href="(.*?)">(.*?)</a>',
                lambda m: (
                    f"[{m.group(2)}]({handle_url(m.group(1), base_url)})"
                    if is_safe_url(handle_url(m.group(1), base_url))
                    else m.group(0)
                ),
            ),
        ],
        "images": [
            (
                r'<img src="(.*?)" alt="(.*?)">',
                lambda m: (
                    f"![{m.group(2)}]({handle_url(m.group(1), base_url)})"
                    if is_safe_url(handle_url(m.group(1), base_url))
                    else m.group(0)
                ),
            ),
        ],
    }

    def handle_url(url: str, base: str) -> str:
        if not url.startswith(("http://", "https://")):
            return urljoin(base, url)
        return url.split()[0]

    def is_safe_url(url: str) -> bool:
        return True  # ph

    def apply_conversions(text: str, conv_type: str) -> str:
        for pattern, replacement in conversions.get(conv_type, []):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    soup = BeautifulSoup(html, "html.parser")

    if emphasis:
        html = apply_conversions(html, "emphasis")
    if links:
        html = apply_conversions(html, "links")
    if images:
        html = apply_conversions(html, "images")

    if nav := soup.find("nav"):
        nav_list = [f"<li>{a.text}</li>" for a in nav.find_all("a")]
        nav_str = "<ul>" + "".join(nav_list) + "</ul>"
        html = re.sub(r"<nav>.*?</nav>", nav_str, html, flags=re.DOTALL)

    return html.strip()


def house_cleaning(text: str) -> str:
    text = re.sub(r"\n\n+", "\n\n", text)
    text = re.sub(r"\r\n", "\n", text)
    text = text.replace("’", "'")
    text = text.replace("‘", "'")

    text = text.replace("“", '"')
    text = text.replace("”", '"')

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = text.replace("…", "...")

    text = text.replace("E'", "È")

    text = re.sub(r" :", ":", text)
    text = re.sub(r" ;", ";", text)
    text = re.sub(r" ,", ",", text)
    text = re.sub(r" \.", ".", text)
    text = re.sub(r" !", "!", text)
    text = re.sub(r" \?", "?", text)

    text = text.replace("«", '"')
    text = text.replace("»", '"')

    text = re.sub(r"\.{2,}", "...", text)
    text = re.sub(r",{2,}", ",", text)
    text = re.sub(r"_{2,}", "_", text)
    text = re.sub(r"-{2,}", "-", text)

    text = re.sub(r"\n ", "\n", text)
    text = re.sub(r"\n ", "\n", text)

    text = re.sub(r" +", " ", text)

    return text.strip()
