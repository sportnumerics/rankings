// yea.
HTMLCollection.prototype.forEach = Array.prototype.forEach;

document
  .getElementsByClassName('expand-anchor')
  .forEach(anchor => {
    anchor.onclick = function(e) {
      anchor
        .getElementsByClassName('expandable')
        .forEach(expandable => {
          expandable.style.display = expandable.style.display !== 'flex' ? expandable.style.display = 'flex' : expandable.style.display = 'none';
        })
    }
  });
