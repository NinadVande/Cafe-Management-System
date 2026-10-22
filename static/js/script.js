document.addEventListener("DOMContentLoaded", () => {
  const picker = document.getElementById("menu-item-picker");
  const addButton = document.getElementById("add-menu-item");
  const cart = document.getElementById("cart-items");
  const empty = document.getElementById("empty-cart");
  if (!picker || !addButton || !cart) return;
  const refreshEmpty = () => { empty.hidden = cart.children.length !== 0; };
  const addSelected = () => {
    const option = picker.options[picker.selectedIndex];
    if (!option.value || cart.querySelector(`[data-item-id="${option.value}"]`)) return;
    const row = document.createElement("tr");
    row.dataset.itemId = option.value;
    row.innerHTML = `<td></td><td>₹${Number(option.dataset.price).toFixed(2)}</td><td><input class="qty" type="number" min="1" name="qty_${option.value}" value="1"></td><td><button type="button" class="remove-cart-item">Remove</button></td>`;
    row.firstElementChild.textContent = option.dataset.name;
    cart.appendChild(row); picker.value = ""; refreshEmpty();
  };
  addButton.addEventListener("click", addSelected);
  picker.addEventListener("change", addSelected);
  cart.addEventListener("click", event => { if (event.target.classList.contains("remove-cart-item")) { event.target.closest("tr").remove(); refreshEmpty(); } });
  refreshEmpty();
});
