<script>
    // extiende la fecha de cierre del lead para reabrirlo
    document.addEventListener('DOMContentLoaded', function() {
        const endDateInput = document.getElementById('id_end_date_time');
    const extendedEndDateDiv = document.getElementById('div_id_extended_end_date_time');

    function checkDates() {
            const endDateValue = endDateInput.value;

    // Verifica si endDateInput tiene un valor válido
    if (endDateValue) {
                const endDate = new Date(endDateValue);
    const now = new Date();
                // Comparar fechas en milisegundos
                if (endDate.getTime() > now.getTime()) {
        extendedEndDateDiv.style.display = 'none';
                } else {
        extendedEndDateDiv.style.display = 'block';
                }

                // Deshabilitar end_date_time si la fecha actual es mayor
                endDateInput.disabled = now.getTime() > endDate.getTime();
            }
        }

    // Inicializar en la carga
    checkDates();
    // Cambiar visibilidad y deshabilitación en el cambio de end_date_time
    endDateInput.addEventListener('change', checkDates);
    });
</script>





<script>
    //Boton para agregar un nuevo producto
    document.addEventListener('DOMContentLoaded', function () {
        var formIndex = document.getElementById('form-index').getAttribute('data-form-index');
        const addMoreButton = document.getElementById('add-more');
        const formListContainer = document.getElementById('form-list');
        const formTemplate = document.getElementById('form-template').innerHTML;

        addMoreButton.addEventListener('click', function () {
            let newFormHtml = formTemplate.replace(/__prefix__/g, formIndex);
            formListContainer.insertAdjacentHTML('beforeend', newFormHtml);

            // Oculta o elimina el checkbox de eliminación en el nuevo formulario
            const newForm = formListContainer.lastElementChild;
            const deleteCheckbox = newForm.querySelector('input[type="checkbox"][name$="DELETE"]');
            const deleteLabel = deleteCheckbox ? deleteCheckbox.previousElementSibling : null;
            if (deleteCheckbox && deleteLabel) {
                deleteCheckbox.style.display = 'none'; // O usa 'deleteCheckbox.remove();' para eliminarlo
                deleteLabel.style.display = 'none';    // O usa 'deleteLabel.remove();' para eliminarlo
            }

            document.getElementById('id_lead_product-TOTAL_FORMS').value = ++formIndex;
        });
    });
</script>
