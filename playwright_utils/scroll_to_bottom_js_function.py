scroll_to_bottom_js_function = """
function scrollUntilNoData() {
  let previousHeight = 0;

  function checkAndScroll() {
    const currentHeight = document.documentElement.scrollHeight || document.documentElement.offsetHeight;

    if (currentHeight > previousHeight) {
      window.scrollTo(0, currentHeight);
      previousHeight = currentHeight;
      setTimeout(checkAndScroll, 2000);
    } else {
      return;
    }
  }

  checkAndScroll();
}
"""
