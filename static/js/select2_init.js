// select2-init.js
document.addEventListener("DOMContentLoaded", () => {
    $("#customer").select2({
      placeholder: "Choose Customer",
      allowClear: true
    });
  
    $("#product_select").select2({
      placeholder: "Choose Product",
      allowClear: true
    });
  });