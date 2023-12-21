document.addEventListener('DOMContentLoaded', function () {
    var formIndex = document.getElementById('form-index').getAttribute('data-form-index');
    const addMoreButton = document.getElementById('add-more');
    const formListContainer = document.getElementById('form-list');
    const formTemplate = document.getElementById('form-template').innerHTML;

    // Leer los datos de stage y is_closed
    const leadInfo = document.getElementById('lead-info');
    const leadStage = leadInfo.getAttribute('data-stage');
    const leadIsClosed = leadInfo.getAttribute('data-is-closed') === 'True';

    // Ocultar el botón si el lead está cerrado o si el stage es 'close_win' o 'close_lost'
    if (leadIsClosed || leadStage === 'close_win' || leadStage === 'close_lost') {
        addMoreButton.style.display = 'none';
    } else {
        addMoreButton.addEventListener('click', function () {
            let newFormHtml = formTemplate.replace(/__prefix__/g, formIndex);
            formListContainer.insertAdjacentHTML('beforeend', newFormHtml);

            // Oculta o elimina el checkbox de eliminación en el nuevo formulario
            const newForm = formListContainer.lastElementChild;
            const deleteCheckbox = newForm.querySelector('input[type="checkbox"][name$='DELETE']");
            const deleteLabel = deleteCheckbox ? deleteCheckbox.previousElementSibling : null;
            if (deleteCheckbox && deleteLabel) {
                deleteCheckbox.style.display = 'none';
                deleteLabel.style.display = 'none';
            }

            document.getElementById('id_lead_product-TOTAL_FORMS').value = ++formIndex;
        });
    }
});
