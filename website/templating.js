document.addEventListener('DOMContentLoaded', function() {
  fetch('/layout.html')
    .then(response => response.text())
    .then(layout => {
      const parser = new DOMParser();
      const layoutDoc = parser.parseFromString(layout, 'text/html');

      const body = document.getElementsByTagName("body")
      const content = document.getElementById("content")

      console.log("body", body)
      console.log("content", content)
      console.log("document", document)
      console.log("layoutDoc", layoutDoc)

      layoutDoc.getElementById('main').appendChild(content)
      body.replaceChildren(layoutDoc)
    })
    .catch(error => console.error(`Error loading layout.html:`, error));
});
