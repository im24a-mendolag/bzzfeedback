// JS for choose_subject page
(function(){
  var select = document.getElementById('category_id');
  if (!select) return;
  var wrap = document.getElementById('custom_category_wrap');
  function toggle(){
    var isCustom = (select.value === '__custom__');
    if (wrap) wrap.style.display = isCustom ? 'block' : 'none';
    var input = document.getElementById('custom_category');
    if (input) {
      input.required = isCustom;
      if (!isCustom) input.value = '';
    }
  }
  select.addEventListener('change', toggle);
  toggle();
})();

