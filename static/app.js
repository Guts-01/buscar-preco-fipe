const form = document.querySelector("#vehicle-form");

if (form) {
  form.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", () => {
      for (const id of (select.dataset.reset || "").split(",").filter(Boolean)) {
        const dependent = document.getElementById(id);
        if (dependent) {
          dependent.value = "";
        }
      }
      form.submit();
    });
  });
}
