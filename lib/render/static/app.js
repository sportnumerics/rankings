// yea.
HTMLCollection.prototype.forEach = Array.prototype.forEach;

document
  .getElementsByClassName('expand-anchor')
  .forEach(anchor => {
    const expandableElement = anchor.nextElementSibling;

    anchor.addEventListener('click', e => toggle(expandableElement));

    anchor.addEventListener('focusout', e => hide(expandableElement));
});

function toggle(element) {
  element.style.display = element.style.display !== 'flex'
    ? 'flex'
    : '';
}

function hide(element) {
  element.style.display = '';
}