// payment-handlers.js
class PaymentManager {
  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.setupObserver();
  }

  initializeElements() {
    this.paymentStatus = document.getElementById("payment_status");
    this.paymentAmount = document.getElementById("payment_amount");
    this.grandTotalSpan = document.getElementById("grand-total");
    this.paidAmount = document.getElementById("paid_amount");
    
    // Initialize values
    if (this.paymentStatus.value) {
      this.updatePaymentAmounts(this.paymentStatus.value);
    }
  }

  setupEventListeners() {
    // Listen for payment status changes
    this.paymentStatus.addEventListener("change", () => {
      this.updatePaymentAmounts(this.paymentStatus.value);
    });

    // Listen for payment amount changes
    if (this.paymentAmount) {
      this.paymentAmount.addEventListener("input", () => {
        this.validatePaymentAmount();
      });
    }
  }

  setupObserver() {
    // Observer for grand total changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach(() => {
        if (this.paymentStatus.value) {
          this.updatePaymentAmounts(this.paymentStatus.value);
        }
      });
    });

    if (this.grandTotalSpan) {
      observer.observe(this.grandTotalSpan, {
        characterData: true,
        childList: true,
        subtree: true,
      });
    }
  }

  validatePaymentAmount() {
    const grandTotal = parseFloat(this.grandTotalSpan.textContent);
    const currentPayment = parseFloat(this.paymentAmount.value) || 0;

    if (this.paymentStatus.value === "FULL" && currentPayment !== grandTotal) {
      this.paymentAmount.value = grandTotal.toFixed(2);
    } else if (this.paymentStatus.value === "PARTIAL") {
      if (currentPayment > grandTotal) {
        alert("Payment amount cannot exceed total amount");
        this.paymentAmount.value = grandTotal.toFixed(2);
      } else if (currentPayment <= 0) {
        alert("Payment amount must be greater than 0 for partial payment");
        this.paymentAmount.value = "0.00";
      }
    }

    // Update paid amount display if it exists
    if (this.paidAmount) {
      this.paidAmount.textContent = parseFloat(this.paymentAmount.value).toFixed(2);
    }
  }

  updatePaymentAmounts(status) {
    const grandTotal = parseFloat(this.grandTotalSpan.textContent);

    switch (status) {
      case "FULL":
        this.paymentAmount.value = grandTotal.toFixed(2);
        if (this.paidAmount) {
          this.paidAmount.textContent = grandTotal.toFixed(2);
        }
        this.paymentAmount.readOnly = true;
        break;

      case "PARTIAL":
        // Set to 0 or keep current value if it's valid
        const currentAmount = parseFloat(this.paymentAmount.value) || 0;
        if (currentAmount > grandTotal) {
          this.paymentAmount.value = "0.00";
        }
        this.paymentAmount.readOnly = false;
        break;

      case "PENDING":
        this.paymentAmount.value = "0.00";
        if (this.paidAmount) {
          this.paidAmount.textContent = "0.00";
        }
        this.paymentAmount.readOnly = true;
        break;

      default:
        this.paymentAmount.value = "0.00";
        if (this.paidAmount) {
          this.paidAmount.textContent = "0.00";
        }
        this.paymentAmount.readOnly = true;
    }

    // Ensure paid amount display is updated
    if (this.paidAmount) {
      this.paidAmount.textContent = this.paymentAmount.value;
    }
  }
}

// Initialize the payment manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new PaymentManager();
});