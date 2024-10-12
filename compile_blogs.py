import os
import pathlib
from datetime import datetime, timezone
import markdown
import json
from bs4 import BeautifulSoup


def get_date_created(path: pathlib.Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc)


def convert_post(src_path: str, target_folder: str, template_path: str) -> dict:
    """
    Convert the file at src_path and write it to target_folder, given the html template passed in.
    """
    template_soup = BeautifulSoup(template_path, "html.parser")
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

    return blog_paths


def compile_links(blogs: list[dict], linkfile_path: str) -> None:
    with open(linkfile_path, "w", encoding="utf-8") as file:
        blogs.sort(key=lambda obj: datetime.strptime(obj["date"], "%Y-%m-%d"))
        file.write(f"const posts = {json.dumps(blogs)}")


def main(
    source_folder: str, target_folder: str, post_template: str, linkfile_path: str
) -> None:
    blogs = compile_blogs(source_folder, target_folder, post_template)
    compile_links(blogs, linkfile_path)


if __name__ == "__main__":
    source_folder = "./posts"
    target_folder = "./website/blogs"
    template_path = "./template.html"
    linkfile_path = "./website/postlinks.js"
    main(source_folder, target_folder, template_path, linkfile_path)
