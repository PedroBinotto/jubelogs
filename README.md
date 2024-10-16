# jubelogs

[jubelogs.neocities.org](https://jubelogs.neocities.org/)

web dev 1.0 was so much more fun :sparkles:

_self-contained, single-purpose, home-grown **static blog generator** written in Python_

## compiling blogs

blogs are compiled from .md files in `posts`:

```
.
├── compile_blogs.py
├── deploy.sh
├── poetry.lock
├── posts
│   └── *** POSTS GO HERE ***
├── pyproject.toml
├── README.md
├── templates
│   ├── blog_link.html
│   ├── home.html
│   └── layout.html
└── website
    ├── assets
    │   ├── bgtile.gif
    │   └── header.png
    ├── blogs
    │   └── *** COMPILED BLOG POSTS ARE PLACED HERE ***
    ├── index.html
    └── styles.css
```

posts MUST begin with a top-level H1 heading:

```markdown
# My first post!

This is a paragraph

...
```

`compile_blogs.py` will compile all posts to the html template and copy them to `website/blogs`

## deployment to neocities

run `deploy.sh` to compile all blogs and deploy to [neocities](neocities.org)

```bash
# pwd: jubelogs
./deploy.sh
```

dependencies:
- [python](https://www.python.org/);
- [poetry](https://python-poetry.org/);

---

this is a hobby project; no compromise, no guarantee of stability :heart:
