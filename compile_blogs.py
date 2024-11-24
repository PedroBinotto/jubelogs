import os
import pathlib
import re
from datetime import datetime, timezone
import markdown
import unicodedata
from dataclasses import dataclass
from bs4 import BeautifulSoup

SYNOPSIS_LENGTH_LIMIT = 200
SITE_NAME = "jubelogs"
TEMPLATE_PATH = "./templates/layout.html"
SOUP_PARSER = "html.parser"
POSTS_FRAGMET = "blogs"
DEFAULT_TITLE = "sem título"


@dataclass
class Blog:
    url: str
    title: str
    date: str
    synopsis: str
    path: str
    markup: str
    category: str | None


def date_from_path(path: str) -> str:
    return datetime.fromtimestamp(
        pathlib.Path(path).stat().st_ctime, tz=timezone.utc
    ).strftime("%Y-%m-%d")


def read_from_path(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def normalize_string(string: str | None) -> str:
    if not string:
        return
    normalized_str = unicodedata.normalize("NFKD", string)
    ascii_str = "".join(c for c in normalized_str if not unicodedata.combining(c))
    formatted_str = ascii_str.replace(" ", "_").lower()
    return formatted_str


def subindex_name(category_name: str) -> str:
    return f"index_{normalize_string(category_name)}.html"


def extract_category(path: str) -> str | None:
    with open(path, "r", encoding="utf-8") as file:
        first_line = file.readline()
        match = re.search(r"\[comment\]: # \((.*)\)", first_line)
        if match is not None:
            return match.group(1).strip()


def write_to_path(path: str, contents: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)


def soup_from_path(path: str) -> BeautifulSoup:
    return BeautifulSoup(read_from_path(path), SOUP_PARSER)


def apply_layout(
    content_markup: str, layout_markup: str, page_title: str, blog_categories: set[str]
) -> str:
    """Apply layout to content markup"""
    content_soup = BeautifulSoup(content_markup, SOUP_PARSER)
    layout_soup = BeautifulSoup(layout_markup, SOUP_PARSER)

    layout_soup.title.string = f"{SITE_NAME} - {page_title}"
    layout_soup.find(id="content").append(content_soup)

    if len(blog_categories):
        category_list_container = layout_soup.find(id="category_list")
        category_list_soup = soup_from_path("./templates/category_list.html")

        for category in blog_categories:
            category_link_soup = soup_from_path("./templates/category_link.html")
            anchor = category_link_soup.find("a")
            anchor["href"] = f"/{subindex_name(category)}"
            anchor.string = category
            category_list_soup.append(category_link_soup)

        category_list_container.append(category_list_soup)

    return layout_soup.prettify()


def convert_post(src_path: str, target_folder: str) -> Blog:
    """
    Convert the file at `src_path` and write it to `target_folder`, given the html template passed in.
    """

    src_file = read_from_path(src_path)

    transpiled_soup = BeautifulSoup(
        markdown.markdown(src_file, extensions=["extra"]), SOUP_PARSER
    )

    if not transpiled_soup.find("h1"):
        header = transpiled_soup.new_tag("h1")
        header.string = DEFAULT_TITLE
        transpiled_soup.insert(0, header)

    title_element = transpiled_soup.find("h1")
    content_container = soup_from_path("./templates/blog_contents.html").find(
        id="blog-contents-container"
    )
    category = extract_category(src_path)
    synopsis = transpiled_soup.find("p").string

    for element in title_element.find_all_next():
        content_container.append(element.extract())

    title_element.insert_after(content_container)

    if category:
        category_tag = transpiled_soup.new_tag("h3")
        category_link = transpiled_soup.new_tag("a")
        category_link["href"] = f"/{subindex_name(category)}"
        category_link.string = f"[{category}]"
        category_tag.append(category_link)

        transpiled_soup.find("h1").insert_after(category_tag)

    target_filename = f"{os.path.splitext(os.path.basename(src_path))[0]}.html"
    target_path = os.path.join(target_folder, POSTS_FRAGMET, target_filename)

    blog = Blog(
        url=f"/blogs/{target_filename}",
        title=title_element.string,
        date=date_from_path(src_path),
        synopsis=synopsis,
        path=target_path,
        markup=transpiled_soup.prettify(),
        category=category,
    )

    return blog


def compile_blogs(
    source_folder: str, target_folder: str, categories: set[str]
) -> list[Blog]:
    """
    Given the path for the source and target folders and the blank html template, convert and write all blog posts to
    location
    """

    blogs: list[Blog] = []

    os.makedirs(target_folder, exist_ok=True)
    os.makedirs(os.path.join(target_folder, POSTS_FRAGMET), exist_ok=True)

    for filename in os.listdir(source_folder):
        src_path = os.path.join(source_folder, filename)  # ./posts/post.md
        if os.path.isfile(src_path) and pathlib.Path(src_path).suffix in [
            ".md",
            ".MD",
            ".markdown",
        ]:
            blog = convert_post(src_path, target_folder)
            blogs.append(blog)
            if blog.category:
                categories.add(blog.category)

    template_markup = read_from_path(TEMPLATE_PATH)
    blogs.sort(key=lambda blog: datetime.strptime(blog.date, "%Y-%m-%d"), reverse=True)

    for blog in blogs:
        blog.markup = apply_layout(blog.markup, template_markup, blog.title, categories)
        write_to_path(blog.path, blog.markup)

    compile_index(blogs, target_folder, categories)
    for category in categories:
        compile_index(blogs, target_folder, categories, category)
    return blogs


def compile_index(
    blogs: list[Blog],
    target_folder: str,
    categories: set[str],
    subindex_categoria: str = None,
) -> None:
    """Compile index.html file with links to all blogs"""

    if subindex_categoria:
        filename = subindex_name(subindex_categoria)
        title = subindex_categoria
        blogs = filter(
            lambda blog: normalize_string(blog.category)
            == normalize_string(subindex_categoria),
            blogs,
        )
    else:
        filename = "index.html"
        title = "Home"

    index_path = pathlib.Path(target_folder) / filename

    link_template_path = "./templates/blog_link.html"
    index_page_template_path = "./templates/home.html"

    soup = soup_from_path(index_page_template_path)
    blog_list = soup.find(id="blog-list")

    for i, blog in enumerate(blogs):
        link_template_soup = soup_from_path(link_template_path)

        link = link_template_soup.find(id="synopsis-link")
        date = link_template_soup.find(id="synopsis-date")
        category = link_template_soup.find(id="synopsis-category")
        synopsis = link_template_soup.find(id="synopsis-paragraph")

        link.string = blog.title
        date.string = f'({blog.date if blog.date is not None else 'sem data'}) - '
        if blog.category:
            category.string = f"[{blog.category}] - "

        synopsis.string = blog.synopsis[:SYNOPSIS_LENGTH_LIMIT] + "..."

        link["href"] = blog.url

        link["id"] = f"{link["id"]}_{str(i)}"
        date["id"] = f"{date["id"]}_{str(i)}"
        synopsis["id"] = f"{synopsis["id"]}_{str(i)}"

        blog_list.append(link_template_soup)

    write_to_path(
        index_path,
        apply_layout(soup.prettify(), read_from_path(TEMPLATE_PATH), title, categories),
    )


def main() -> None:
    categories = set()

    source_folder = "./blogs"
    target_folder = "./website"

    compile_blogs(source_folder, target_folder, categories)


if __name__ == "__main__":
    main()
