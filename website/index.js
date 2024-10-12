// TODO: Compile index file in place on deploy

String.prototype.truncate = String.prototype.truncate ||
  function(n, useWordBoundary) {
    if (this.length <= n) { return this; }
    const subString = this.slice(0, n - 1); // the original check
    return (useWordBoundary
      ? subString.slice(0, subString.lastIndexOf(" "))
      : subString) + "&hellip;";
  };

const SYNOPSIS_WORD_LIMIT = 200;

document.addEventListener('DOMContentLoaded', function() {
  const blogList = document.getElementById('blog-list');
  const surprise = document.getElementById("surprise");

  surprise.innerHTML = splashes[Math.floor(Math.random() * splashes.length)] + "!"
  posts.reverse().forEach(post => {
    const listItem = document.createElement('dd');
    const date = document.createElement('small');
    const link = document.createElement('a');
    const wrapper = document.createElement('div');
    const header = document.createElement('h2');
    const synopsisBox = document.createElement('div');
    const synopsis = document.createElement('p');

    date.innerHTML = `(${post.date ?? 'sem data'}) - `;
    wrapper.classList = "blog-box";
    header.classList = "special-text";
    synopsisBox.classList = "synopsis";
    link.style = "color: white";
    link.href = post.url;
    link.textContent = post.title;
    synopsis.innerHTML = post.synopsis.truncate(SYNOPSIS_WORD_LIMIT, true);

    header.appendChild(date);
    header.appendChild(link);

    synopsisBox.append(synopsis)

    wrapper.appendChild(header);
    wrapper.appendChild(synopsisBox);

    listItem.append(wrapper);

    blogList.appendChild(listItem);
  });
});
