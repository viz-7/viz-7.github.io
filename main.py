#!/usr/bin/env python3

import sys
from pathlib import Path


CRAB_CONTENT_DIV = '<div class="crab-content">\n'
ARTICLES_DIR = Path("articles")


def get_header_footer() -> tuple[str, str]:
    index_source = Path("index.html").read_text()

    try:
        header_end = index_source.index("</div>")
        footer_start = index_source.index("<footer>")
    except ValueError as error:
        raise ValueError("index.html is missing the header or footer marker") from error

    return index_source[:header_end], index_source[footer_start:]


def add_header_footer(name: str, crab: str) -> str:
    header, footer = get_header_footer()
    page = (
        f"{header}<h1>{name}</h1>\n"
        f"{CRAB_CONTENT_DIV}{crab}\n</div>\n{footer}"
    )
    (ARTICLES_DIR / f"{name}.html").write_text(page)
    return name


def update_root(name: str, crab_path: Path, article_source: str) -> None:
    try:
        offset = article_source.index("<ul>\n") + len("<ul>\n")
    except ValueError as error:
        raise ValueError(f"{crab_path} is missing an unordered list") from error

    link = f'<li><a href="/articles/{name}.html">{name}</a></li>\n'
    crab_path.write_text(article_source[:offset] + link + article_source[offset:])
    print(f"Updating {crab_path}")
    add_header_footer(crab_path.name, crab_path.read_text())
    print(f"Generating html for {crab_path}")


def regenerate() -> None:
    print("Regenerating...")
    for article_path in ARTICLES_DIR.iterdir():
        if not article_path.is_file():
            continue

        article_source = article_path.read_text()
        try:
            content_start = article_source.index(CRAB_CONTENT_DIV) + len(CRAB_CONTENT_DIV)
            footer_start = article_source.index("<footer>")
            content_end = article_source.rindex("</div>", content_start, footer_start)
        except ValueError as error:
            raise ValueError(f"{article_path} is not a generated article") from error

        crab_content = article_source[content_start:content_end].removesuffix("\n")
        name = article_path.stem
        print(f"Generating for {name}")
        add_header_footer(name, crab_content)


def generate(crab_path: Path) -> None:
    name = add_header_footer(crab_path.name, crab_path.read_text())
    articles_index = Path("crab/articles")
    images_index = Path("crab/img")
    is_image = crab_path.parent.name == "images"
    reserved = {"articles", "art", "bookmarks", "img", "papers"}

    article_source = articles_index.read_text()
    if name not in article_source and name not in reserved and not is_image:
        update_root(name, articles_index, article_source)
    elif is_image:
        image_source = images_index.read_text()
        if name not in image_source:
            update_root(name, images_index, image_source)


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print(f"Usage: {Path(sys.argv[0]).name} <crab-file|regen>", file=sys.stderr)
        return 2

    if arguments[0] == "regen":
        regenerate()
    else:
        generate(Path(arguments[0]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
