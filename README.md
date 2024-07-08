# Reedy

Reedy is a Python package that provides an easy and efficient way to convert HTML content to Markdown format for RAG/Scraping/Data Extraction purposes.

## Features

- HTML to Markdown
- Customizable options for handling links and images
- Preserves code and formatting
- Handles metadata extraction

## Installation

Clone the repository:

```
git clone https://github.com/banda-larga/reedy.git
cd reedy
```

You can install Reedy using pip:

```
pip install -e .
```

### Converting URL content to Markdown

```python
from reedy import url2markdown, html2markdown

# here we use url2markdown
markdown = url2markdown("https://lilianweng.github.io/posts/2024-07-07-hallucination/")
print(markdown)
```

Output:
```
Title: Extrinsic Hallucinations in LLMs

Snippet: Hallucination in large language models usually refers to the model generating unfaithful, fabricated, inconsistent, or nonsensical content. As a term, hallucination has been somewhat generalized to cases when the model makes mistakes. Here, I would like to narrow down the problem of hallucination to be when the model output is fabricated and not grounded by either the provided context or world knowledge. There are two types of hallucination: In-context hallucination: The model output should be consistent with the source content in context.

Categories: posts

Tags: nlp, language-model, safety, hallucination, factuality

Date: 2024-07-07

---

Hallucination in large language models usually refers to the model generating unfaithful, fabricated, inconsistent, or nonsensical content. As a term, hallucination has been somewhat generalized to cases when the model makes mistakes. Here, I would like to narrow down the problem of hallucination to be when the model output is fabricated and **not grounded** by either the provided context or world knowledge.

There are two types of hallucination:

- In-context hallucination: The model output should be consistent with the source content in context.
- Extrinsic hallucination: The model output should be grounded by the pre-training dataset. However, given the size of the pre-training dataset, it is too expensive to retrieve and identify conflicts per generation. If we consider the pre-training data corpus as a proxy for world knowledge, we essentially try to ensure the model output is factual and verifiable by external world knowledge. Equally importantly, when the model does not know about a fact, it should say so.

This post focuses on extrinsic hallucination. To avoid hallucination, LLMs need to be (1) factual and (2) acknowledge not knowing the answer when applicable.
...
```

This will fetch the content from the specified URL, convert it to Markdown, and include links and images in the output.

### Customization Options

The `html2markdown` and `url2markdown` functions accept the following options:

- `links` (bool): If True, preserve and convert HTML links to Markdown format.
- `images` (bool): If True, preserve and convert HTML images to Markdown format.
- `emphasis` (bool): If True, preserve and convert HTML emphasis tags to Markdown format.
- `clean` (bool): If True, clean up the Markdown output.
- `separator` (str): The separator to use between metadata and content. Default is `---`.

Example:
```python
markdown = html2markdown(
    html_content,
    links=True,
    images=False,
    emphasis=False,
    clean=True,
    separator="~~~~~~~"
)
```

## License

HTML2Markdown is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This package is heavily based on [Trafilatura](https://github.com/adbar/trafilatura). I would like to thank the author.