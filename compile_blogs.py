import os
import pathlib
from datetime import datetime, timezone
import markdown
from dataclasses import dataclass
from bs4 import BeautifulSoup

SYNOPSIS_LENGTH_LIMIT = 200


@dataclass
class Blog:
    url: str
    title: str
    date: str
    synopsis: str
    path: str
    markup: str


def date_from_path(path: str) -> str:
    return datetime.fromtimestamp(
        pathlib.Path(path).stat().st_ctime, tz=timezone.utc
    ).strftime("%Y-%m-%d")


def read_from_path(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def write_to_path(path: str, contents: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        file.write(contents)


def soup_from_path(path: str) -> BeautifulSoup:
    return BeautifulSoup(read_from_path(path), "html.parser")


def apply_layout(content_markup: str, layout_markup: str, page_title: str) -> str:
    content_soup = BeautifulSoup(content_markup, "html.parser")
    layout_soup = BeautifulSoup(layout_markup, "html.parser")

    layout_soup.title.string = f"jubelogs - {page_title}"
    layout_soup.find(id="content").append(content_soup)

    return layout_soup.prettify()


def convert_post(src_path: str, target_folder: str, template_markup: str) -> Blog:
    """
    Convert the file at `src_path` and write it to `target_folder`, given the html template passed in.
    """
    transpiled_soup = BeautifulSoup(
        markdown.markdown(read_from_path(src_path), extensions=["extra"]), "html.parser"
    )

    title = transpiled_soup.find("h1")
    synopsis = transpiled_soup.find("p").string

    target_markup = apply_layout(
        transpiled_soup.prettify(), template_markup, f"jubelogs - {title.string}"
    )

    target_filename = f"{os.path.splitext(os.path.basename(src_path))[0]}.html"
    target_path = os.path.join(target_folder, target_filename)

    return Blog(
        url=f"/blogs/{target_filename}",
        title=title.string,
        date=date_from_path(src_path),
        synopsis=synopsis,
        path=target_path,
        markup=target_markup,
    )


def compile_blogs(
    source_folder: str, target_folder: str, template_path: str
) -> list[Blog]:
    """
    Given the path for the source and target folders and the blank html template, convert and write all blog posts to
    location
    """
    blogs: list[Blog] = []

    os.makedirs(target_folder, exist_ok=True)

    template_markup = read_from_path(template_path)

    for filename in os.listdir(source_folder):
        src_path = os.path.join(source_folder, filename)
        if os.path.isfile(src_path):
            blog = convert_post(src_path, target_folder, template_markup)
            blogs.append(blog)
            write_to_path(blog.path, blog.markup)

    blogs.sort(key=lambda blog: datetime.strptime(blog.date, "%Y-%m-%d"), reverse=True)

    return blogs


def compile_index(
    blogs: list[Blog],
    index_path: str,
    layout_path: str,
    link_template_path: str,
    index_page_template_path: str,
) -> None:
    soup = soup_from_path(index_page_template_path)
    blog_list = soup.find(id="blog-list")

    for i, blog in enumerate(blogs):
        link_template_soup = soup_from_path(link_template_path)

        link = link_template_soup.find(id="synopsis-link")
        date = link_template_soup.find(id="synopsis-date")
        synopsis = link_template_soup.find(id="synopsis-paragraph")

        link.string = blog.title
        date.string = f'({blog.date if blog.date is not None else 'sem data'}) - '
        synopsis.string = blog.synopsis[:SYNOPSIS_LENGTH_LIMIT] + "..."

        link["href"] = blog.url

        link["id"] = f"{link["id"]}_{str(i)}"
        date["id"] = f"{date["id"]}_{str(i)}"
        synopsis["id"] = f"{synopsis["id"]}_{str(i)}"

        blog_list.append(link_template_soup)

    write_to_path(
        index_path, apply_layout(soup.prettify(), read_from_path(layout_path), "Home")
    )


def main(
    source_folder: str,
    target_folder: str,
    post_template: str,
    index_path: str,
    link_template_path: str,
    index_page_template_path: str,
) -> None:
    blogs = compile_blogs(source_folder, target_folder, post_template)
    compile_index(
        blogs, index_path, post_template, link_template_path, index_page_template_path
    )


if __name__ == "__main__":
    source_folder = "./posts"
    target_folder = "./website/blogs"
    template_path = "./templates/layout.html"
    index_path = "./website/index.html"
    link_template_path = "./templates/blog_link.html"
    index_page_template_path = "./templates/home.html"

    main(
        source_folder,
        target_folder,
        template_path,
        index_path,
        link_template_path,
        index_page_template_path,
    )
