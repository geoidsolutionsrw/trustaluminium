// product-handlers.js
class ProductManager {
  constructor() {
    this.products = [];
    this.initializeElements();
    this.setupEventListeners();
  }

  initializeElements() {
    this.productSelect = document.getElementById("product_select");
    this.priceInput = document.getElementById("price");
    this.quantityInput = document.getElementById("quantity");
    this.stockInfo = document.getElementById("stock-info");
    this.taxInput = document.getElementById("tax");
    this.productsTable = document.getElementById("products-table");
    this.addBtn = document.querySelector(".btn-added");
  }

  setupEventListeners() {
    // Use Select2's change event instead of native change event
    $("#product_select").on("select2:select", (e) => {
      this.handleProductSelection(e.params.data);
    });

    // Handle clearing of selection
    $("#product_select").on("select2:clear", () => {
      this.resetProductForm();
    });

    this.quantityInput.addEventListener("input", () => this.validateQuantity());
    this.addBtn.addEventListener("click", () => this.addProduct());
  }

  async handleProductSelection(selectedData) {
    if (!selectedData || !selectedData.id) {
      this.resetProductForm();
      return;
    }

    const productId = selectedData.id;
    // Get the price from data attribute
    const selectedOption = this.productSelect.querySelector(`option[value="${productId}"]`);
    const price = selectedOption ? selectedOption.dataset.price : null;

    try {
      const response = await fetch(`/get-available-stock/${productId}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const availableStock = data.available_stock;

      // Update form fields
      this.priceInput.value = price || "";
      this.stockInfo.textContent = `Available stock: ${availableStock}`;
      this.quantityInput.value = "";
      this.quantityInput.max = availableStock;
      this.taxInput.value = "0";
    } catch (error) {
      console.error("Error fetching stock:", error);
      this.stockInfo.textContent = "Unable to fetch stock";
      this.resetProductForm();
    }
  }

  async validateQuantity() {
    const selectedId = $("#product_select").val();
    if (!selectedId) return;

    const quantity = parseInt(this.quantityInput.value);
    if (isNaN(quantity)) return;

    try {
      const response = await fetch(`/get-available-stock/${selectedId}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const availableStock = data.available_stock;

      if (quantity > availableStock) {
        this.quantityInput.value = availableStock;
        alert(`Maximum available stock is ${availableStock}`);
      }
    } catch (error) {
      console.error("Error fetching stock:", error);
    }
  }

  calculateSubtotal(product) {
    const baseAmount = product.quantity * product.price;
    const taxAmount = baseAmount * (product.tax / 100);
    return baseAmount + taxAmount;
  }

  addProduct() {
    const selectedId = $("#product_select").val();
    const selectedText = $("#product_select option:selected").text();

    if (!selectedId || !this.quantityInput.value) {
      alert("Please select a product and enter quantity");
      return;
    }

    const product = {
      id: selectedId,
      name: selectedText,
      quantity: parseInt(this.quantityInput.value),
      price: parseFloat(this.priceInput.value),
      tax: parseFloat(this.taxInput.value || 0),
    };

    product.subtotal = this.calculateSubtotal(product);
    this.products.push(product);

    this.updateProductsTable();
    this.updateTotals();
    this.resetProductForm();
    
    // Reset Select2
    $("#product_select").val(null).trigger('change');
  }

  updateProductsTable() {
    const tbody = this.productsTable.querySelector("tbody");
    tbody.innerHTML = "";

    this.products.forEach((product, index) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${index + 1}</td>
        <td>${product.name}</td>
        <td>${product.quantity}</td>
        <td>${product.price.toFixed(0)}</td>
        <td>${product.tax}%</td>
        <td>${product.subtotal.toFixed(0)} RWF</td>
        <td>
          <button type="button" class="btn btn-danger btn-sm delete-product" data-index="${index}">
            Delete
          </button>
        </td>
      `;
      tbody.appendChild(row);
    });

    document.querySelectorAll(".delete-product").forEach((button) => {
      button.addEventListener("click", (e) => {
        const index = parseInt(e.target.dataset.index);
        this.products.splice(index, 1);
        this.updateProductsTable();
        this.updateTotals();
      });
    });
  }

  updateTotals() {
    const totalTax = this.products.reduce((sum, product) => {
      const baseAmount = product.quantity * product.price;
      return sum + baseAmount * (product.tax / 100);
    }, 0);

    const grandTotal = this.products.reduce(
      (sum, product) => sum + product.subtotal,
      0
    );

    document.getElementById("total-tax").textContent = totalTax.toFixed(2);
    document.getElementById("grand-total").textContent = grandTotal.toFixed(2);
  }

  resetProductForm() {
    // Reset Select2
    $("#product_select").val(null).trigger('change');
    
    // Reset other form elements
    this.priceInput.value = "";
    this.quantityInput.value = "";
    this.taxInput.value = "0";
    this.stockInfo.textContent = "";
  }

  // Add a method to get the products array
  getProducts() {
    return this.products;
  }
}

// Initialize the product manager when DOM is loaded
let productManager;
document.addEventListener("DOMContentLoaded", () => {
  productManager = new ProductManager();
});