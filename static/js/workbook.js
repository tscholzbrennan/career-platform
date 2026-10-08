// Formula bar + moving selection: hovering, focusing or tapping a cell with a
// data-formula shows its cell reference and formula/source, and the selection
// outline glides to it. Purely visual; sources are also in the page as text.
(function () {
  var sheet = document.querySelector(".sheet");
  var out = document.querySelector("[data-formula-out]");
  var box = document.querySelector("[data-namebox]");
  if (!sheet || !out || !box) return;

  var LETTERS = "ABCDEFGHIJKL";
  var rows = Array.prototype.slice.call(sheet.querySelectorAll(":scope > .r"));
  var narrow = window.matchMedia("(max-width: 760px)");

  function span(cell) {
    var match = cell.className.match(/\bs(\d+)\b/);
    return match ? parseInt(match[1], 10) : 1;
  }

  function reference(cell) {
    var column = 0;
    if (!narrow.matches) {
      for (var sibling = cell.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
        column += span(sibling);
      }
    }
    return LETTERS.charAt(Math.min(column, 11)) + (rows.indexOf(cell.parentElement) + 1);
  }

  var selection = document.createElement("div");
  selection.className = "selection instant";
  selection.setAttribute("aria-hidden", "true");
  sheet.appendChild(selection);

  var current = null;

  function place(cell) {
    var sheetBox = sheet.getBoundingClientRect();
    var cellBox = cell.getBoundingClientRect();
    selection.style.transform = "translate(" + (cellBox.left - sheetBox.left - 1) + "px," + (cellBox.top - sheetBox.top - 1) + "px)";
    selection.style.width = cellBox.width + 1 + "px";
    selection.style.height = cellBox.height + 1 + "px";
    selection.style.visibility = "visible";
  }

  function select(cell) {
    current = cell;
    place(cell);
    var heading = cell.querySelector("h1, h2");
    var formula = cell.dataset.formula || (heading ? '="' + heading.textContent.trim() + '"' : "");
    if (formula) {
      box.textContent = reference(cell);
      out.textContent = formula;
    }
  }

  var cells = sheet.querySelectorAll(".r > .c[data-formula]");
  Array.prototype.forEach.call(cells, function (cell) {
    cell.addEventListener("mouseenter", function () { select(cell); });
    cell.addEventListener("focusin", function () { select(cell); });
    cell.addEventListener("click", function () { select(cell); });
  });

  var start = sheet.querySelector(".r.selected > .c") || cells[0] || sheet.querySelector(".r > .name-cell");
  if (!start) return;

  // Re-place without animating whenever layout shifts (font swap, resize, reflow).
  function settle() {
    selection.classList.add("instant");
    place(current || start);
    requestAnimationFrame(function () { selection.classList.remove("instant"); });
  }

  sheet.addEventListener("mouseleave", function () { select(start); });
  if ("ResizeObserver" in window) new ResizeObserver(settle).observe(sheet);
  else window.addEventListener("resize", settle);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(settle);
  select(start);
  settle();
})();
