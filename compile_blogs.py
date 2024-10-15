import os
import pathlib
from datetime import datetime, timezone
import markdown
from bs4 import BeautifulSoup

SYNOPSIS_LENGTH_LIMIT = 200


def get_date_created(path: pathlib.Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc)


def convert_post(src_path: str, target_folder: str, template_markup: str) -> dict:
    """
    Convert the file at `src_path` and write it to `target_folder`, given the html template passed in.
    """
    template_soup = BeautifulSoup(template_markup, "html.parser")
    src_file = pathlib.Path(src_path)

    with open(src_file, "r", encoding="utf-8") as file:
        src_content = file.read()
        compiled_html = BeautifulSoup(
            markdown.markdown(src_content, extensions=["extra"]), "html.parser"
        )

    title = compiled_html.find("h1")
    synopsis = compiled_html.find("p").string

    template_soup.title.string = f"jubelogs - {title.string}"
    template_soup.find(id="content").append(compiled_html)

    target_filename = f"{os.path.splitext(os.path.basename(src_path))[0]}.html"
    target_path = os.path.join(target_folder, target_filename)
    with open(target_path, "w", encoding="utf-8") as target_file:
        target_file.write(str(template_soup.prettify()))

    return {
        "url": f"/blogs/{target_filename}",
        "title": title.string,
        "date": get_date_created(src_file).strftime("%Y-%m-%d"),
        "synopsis": synopsis,
    }


def compile_blogs(
    source_folder: str, target_folder: str, post_template: str
) -> list[dict]:
    """
    Given the path for the source and target folders and the blank html template, convert and write all blog posts to
    location
    """
    blog_paths = []
    os.makedirs(target_folder, exist_ok=True)

    with open(post_template, "r", encoding="utf-8") as file:
        template_content = file.read()

    for filename in os.listdir(source_folder):
        path = os.path.join(source_folder, filename)
        if os.path.isfile(path):
            blog_paths.append(convert_post(path, target_folder, template_content))

    blog_paths.sort(
        key=lambda blog: datetime.strptime(blog["date"], "%Y-%m-%d"), reverse=True
    )
    return blog_paths


def compile_index(blogs: list[dict], index_path: str, layout_path: str) -> None:
    with open("./templates/home.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    blog_list = soup.find(id="blog-list")

    for i, blog in enumerate(blogs):
        with open(
            "./templates/blog_link.html", "r", encoding="utf-8"
        ) as template_contents:
            link_template_soup = BeautifulSoup(template_contents.read(), "html.parser")

        link = link_template_soup.find(id="synopsis-link")
        date = link_template_soup.find(id="synopsis-date")
        synopsis = link_template_soup.find(id="synopsis-paragraph")

        link.string = blog["title"]
        date.string = f'({blog['date'] if blog['date'] is not None else 'sem data'}) - '
        synopsis.string = blog["synopsis"][:SYNOPSIS_LENGTH_LIMIT] + "..."

        link["href"] = blog["url"]

        link["id"] = f"{link["id"]}_{str(i)}"
        date["id"] = f"{date["id"]}_{str(i)}"
        synopsis["id"] = f"{synopsis["id"]}_{str(i)}"

        blog_list.append(link_template_soup)

    with open(layout_path, "r", encoding="utf-8") as file:
        template_content = file.read()
        template_soup = BeautifulSoup(template_content, "html.parser")

        title = "Home"
        template_soup.title.string = f"jubelogs - {title}"
        template_soup.find(id="content").append(soup)
        with open(index_path, "w", encoding="utf-8") as index:
            index.write(template_soup.prettify())


def main(
    source_folder: str, target_folder: str, post_template: str, index_path: str
) -> None:
    blogs = compile_blogs(source_folder, target_folder, post_template)
    compile_index(blogs, index_path, post_template)


if __name__ == "__main__":
    source_folder = "./posts"
    target_folder = "./website/blogs"
    template_path = "./templates/layout.html"
    index_path = "./website/index.html"
    main(source_folder, target_folder, template_path, index_path)
