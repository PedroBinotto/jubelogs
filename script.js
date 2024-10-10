const surprise = document.getElementById("surprise")

const splashes = [
  "lorem ipsum",
  "jubelogs",
  "canal indisiponível",
  "volte mais tarde",
  "hora de dormir",
  "socorram me subi no onibus em marrocos",
  "eles estão vendo",
  "olhe para trás",
  "heder goes here fdsa fd jhgf jhf jhgfj h j gfds gfh",
  "vamos passear na floresta... piquenique sera na propriaescola, com show do palhaço.n, jmkjplploobbyrere",
]
surprise.innerHTML = splashes[Math.floor(Math.random() * splashes.length)] + "!"
