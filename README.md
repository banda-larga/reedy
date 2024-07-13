# Reedy 📚

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Reedy is a lightweight Python package that simplifies HTML to Markdown conversion for RAG, web scraping, and data extraction tasks.

## 🚀 Features

- 🔄 Effortless HTML to Markdown conversion
- 🔗 Customizable handling of links, images, formatting
- 🖋️ Preserves code blocks and text formatting
- 📊 Extracts and includes metadata

## 📦 Installation

Install Reedy using pip:

```bash
pip install -U git+https://github.com/banda-larga/reedy.git
```

## 🔧 Usage

### Converting URL content to Markdown

```python
from reedy import url2markdown

# here we use url2markdown
markdown = url2markdown("https://lilianweng.github.io/posts/2024-07-07-hallucination/", include_metadata=True)
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

### Converting HTML to Markdown

```python
from reedy import html2markdown

html_content = """
<h1>Hello, Reedy!</h1>
<p>This is a <strong>sample</strong> HTML content.</p>
"""

markdown = html2markdown(html_content)
print(markdown)
```

## ⚙️ Customization Options

Both `html2markdown` and `url2markdown` functions accept the following parameters:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `include_metadata` | bool | `False` | Include metadata in the output |
| `links` | bool | `False` | Preserve and convert HTML links |
| `images` | bool | `False` | Preserve and convert HTML images |
| `emphasis` | bool | `True` | Preserve and convert emphasis tags |
| `clean` | bool | `True` | Clean up the Markdown output |
| `separator` | str | `"---"` | Separator between metadata and content |

Example:

```python
markdown = html2markdown(
    html_content,
    include_metadata=True,
    links=True,
    images=True,
    emphasis=True,
    clean=True,
    separator="~~~~~~~"
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Reedy is open-source software licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgements

This package is heavily based on [Trafilatura](https://github.com/adbar/trafilatura). We extend our gratitude to its authors and contributors.
