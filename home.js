// MOVE ME !

String.prototype.truncate = String.prototype.truncate ||
  function(n, useWordBoundary) {
    if (this.length <= n) { return this; }
    const subString = this.slice(0, n - 1); // the original check
    return (useWordBoundary
      ? subString.slice(0, subString.lastIndexOf(" "))
      : subString) + "&hellip;";
  };

const SYNOPSIS_WORD_LIMIT = 500;

document.addEventListener('DOMContentLoaded', function() {
  const blogList = document.getElementById('blog-list');
  const surprise = document.getElementById("surprise");

  surprise.innerHTML = splashes[Math.floor(Math.random() * splashes.length)] + "!"
  posts.reverse().forEach(post => {
    const listItem = document.createElement('li');
    const link = document.createElement('a');
    const header = document.createElement('h2');
    const synopsis = document.createElement('p');

    header.classList = "special-text"
    link.style = "color: white"
    link.href = post.url;
    link.textContent = post.title;
    synopsis.innerHTML = post.synopsis.truncate(SYNOPSIS_WORD_LIMIT, true)

    header.appendChild(link)

    listItem.appendChild(header);
    listItem.appendChild(synopsis);

    blogList.appendChild(listItem);
  });
});
