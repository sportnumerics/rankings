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

document.addEventListener('click', closeAll);

function toggle(element) {
  const expanded = element.classList.contains('expanded');
  if (expanded) {
    close(element);
    globalExpandedElements.splice(globalExpandedElements.indexOf(element), 1);
  } else {
    closeAll();
    show(element);
    globalExpandedElements.push(element);
  }
}

function close(element) {
  element.classList.remove('expanded');
  element.removeAttribute('aria-expanded');
}

function closeAll() {
  globalExpandedElements.forEach(close);
  globalExpandedElements.splice(0, globalExpandedElements.length);
}

function show(element) {
  element.classList.add('expanded');
  element.setAttribute('aria-expanded', true);
}