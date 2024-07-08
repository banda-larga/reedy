from parsel import Selector
from trafilatura import extract, extract_metadata, fetch_url

from reedy.utils import (
    code_standardization,
    format_metadata,
    house_cleaning,
    meme,
    tei_to_html,
    to_markdown,
)


class ConversionError(Exception):
    pass


class URLFetchError(Exception):
    pass


def html2markdown(
    content_html: str,
    links: bool = False,
    images: bool = False,
    emphasis: bool = True,
    clean: bool = True,
    separator: str = "---",
) -> str:
    try:
        content = code_standardization(
            meme(content_html, links=links, images=images, emphasis=emphasis)
        )

        metadata = extract_metadata(content_html)
        metadata = metadata.as_dict() if metadata else {}
        metadata = format_metadata(metadata, separator=separator)

        xml = extract(content, output_format="xml")
        html = tei_to_html(xml) if xml else content

        body = Selector(text=html).css("body")
        body = body.get()

        md = to_markdown(body)
        if clean:
            md = house_cleaning(md)

        return f"{metadata}{md}".strip()
    except Exception as e:
        raise ConversionError(f"Error converting HTML to Markdown: {str(e)}") from e


def url2markdown(
    url: str,
    links: bool = False,
    images: bool = False,
    emphasis: bool = True,
    clean: bool = True,
    separator: str = "---",
) -> str:
    try:
        html = fetch_url(url)
        if html is None:
            raise URLFetchError(f"Failed to fetch content from URL: {url}")

        return html2markdown(
            html,
            links=links,
            images=images,
            emphasis=emphasis,
            clean=clean,
            separator=separator,
        )
    except URLFetchError as e:
        raise e
    except Exception as e:
        raise ConversionError(
            f"Error converting URL content to Markdown: {str(e)}"
        ) from e
