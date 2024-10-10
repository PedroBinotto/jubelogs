document.addEventListener('DOMContentLoaded', function() {
  fetch('/layout.html')
    .then(response => response.text())
    .then(layout => {
      const body = document.getElementsByTagName("body")
      const content = document.getElementById("content")
      layout.getElementById('main').appendChild(content)
      body.replaceChildren(layout)
    })
    .catch(error => console.error(`Error loading layout.html:`, error));
});
