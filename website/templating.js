document.addEventListener('DOMContentLoaded', function() {
  fetch('/layout.html')
    .then(response => response.text())
    .then(layout => {
      const parser = new DOMParser();
      const layoutDoc = parser.parseFromString(layout, 'text/html');

      const body = document.getElementsByTagName("body").item(0)
      const content = document.getElementById("content")

      layoutDoc.getElementById('main').appendChild(content)
      body.replaceChildren(layoutDoc.getElementById("container"))
    })
    .catch(error => console.error(`Error loading layout.html:`, error));
});
