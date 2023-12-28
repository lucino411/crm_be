function updateButtonState() {
    if (endDateInput.value !== "") {
        // Si hay una fecha, habilitar el botón
        updateButton.disabled = false;
    } else {
        // Si no hay fecha, deshabilitar el botón
        updateButton.disabled = true;
    }
}