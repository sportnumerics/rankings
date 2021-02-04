// yea.
HTMLCollection.prototype.forEach = Array.prototype.forEach;

const globalExpandedElements = [];
document
  .getElementsByClassName('expand-anchor')
  .forEach(anchor => {
    const expandableElement = anchor.nextElementSibling;

    anchor.addEventListener('click', e => {
      e.stopPropagation();
      toggle(expandableElement);
    });
});

document.addEventListener('click', e => {
  globalExpandedElements.forEach(close);
  globalExpandedElements.splice(0, globalExpandedElements.length);
});

function toggle(element) {
  const expanded = element.classList.contains('expanded');
  if (expanded) {
    close(element);
    globalExpandedElements.splice(globalExpandedElements.indexOf(element), 1);
  } else {
    show(element);
    globalExpandedElements.push(element);
  }
}

function close(element) {
  element.classList.remove('expanded');
  element.removeAttribute('aria-expanded');
}

function show(element) {
  element.classList.add('expanded');
  element.setAttribute('aria-expanded', true);
}