function showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.classList.add("toast");

    if (type === "success") toast.style.backgroundColor = "#4CAF50";
    if (type === "error") toast.style.backgroundColor = "#f44336";
    if (type === "warning") toast.style.backgroundColor = "#ff9800";

    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}
