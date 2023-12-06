let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] },
        { orderable: false, targets: [0, 1, 2, 3, 4, 5, 8] },
        { searchable: false, targets: [0, 1, 10] },
    ],
    pageLength: 5,
    destroy: true,
    // dom: 'Bfrtip',
    dom: 'QBfrtip',

    // API in Callbacks FILTRO EN CADA COLUMNA
    initComplete: function () {
        let api = this.api();

        api.columns([4, 8, 9]).every(function () {
            let column = this;

            // Create select element
            let select = document.createElement('select');
            select.add(new Option(''));
            column.footer().replaceChildren(select);



            // Apply listener for user change in value
            select.addEventListener('change', function () {
                var val = DataTable.util.escapeRegex(select.value);

                column
                    .search(val ? '^' + val + '$' : '', true, false)
                    .draw();
            });

            // Add list of options
            column
                .data()
                .unique()
                .sort()
                .each(function (d, j) {
                    select.add(new Option(d));
                });
        });

        api.on('click', 'tbody td', function () {
            api.search(this.innerHTML).draw();
        });

    },

    // BOTONES DESCARGAR

    buttons: [
        {
            extend: 'collection',
            text: 'Exportar',
            buttons: [
                {
                    extend: 'csv',
                    text: '<u>C</u>SV',
                    key: {
                        key: 'c',
                        altKey: true
                    }
                },
                {
                    extend: 'print',
                    text: '<u>P</u>rint',
                    key: {
                        key: 'p',
                        altKey: true
                    }
                },
                {
                    extend: 'pdf',
                    text: '<u>P</u>DF',
                    key: {
                        key: 'p',
                        altKey: true
                    }
                },
            ]
        }
    ],    
};

const initDataTable = async () => {
    if (dataTableIsInitialized) {
        dataTable.destroy();
    };
    await listLeads();

    dataTable = $("#datatable-leads").DataTable(dataTableOptions);
    dataTableIsInitialized = true;
    select: true

};

const listLeads = async () => {
    try {
        const response = await fetch(`${BASE_URL}/leads/leads_json`);
        const data = await response.json();
        let content = ``;

        data.leads.forEach((lead, index) => {
            const leadData = lead;

            console.log(leadData); // Agrega esta línea para imprimir leadData en la consola

            const createdTime = new Date(leadData.created_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });
            const modifiedTime = new Date(leadData.modified_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });

            content += `
        <tr>
            <td>${index + 1}</td>
            <td><a href="/leads/${leadData.id}/" class='table-link'>${leadData.first_name}</a></td>
            <td>${leadData.last_name}</td>
            <td>${leadData.primary_email}</td>
            <td>${leadData.country}</td>
            <td>${createdTime}</td> 
            <td>${modifiedTime}</td> 
            <td>${leadData.assigned_to}</td>
            <td>${leadData.created_by}</td>
            <td>${leadData.organization}</td>
            <td>
                <a href="/leads/${leadData.id}/update/" class="btn btn-sm btn-secondary"><i class='fa-solid fa-pencil'></i></a>
                <a href="/leads/${leadData.id}/delete/" class="btn btn-sm btn-danger"><i class='fa-solid fa-trash-can'></i></i></a>
            </td>        
        </tr>
        `;
        });
        tableBody_leads.innerHTML = content;
    } catch (e) {
        alert(e);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();
});

// // A $( document ).ready() block.
// $(document).ready(function () {
//     console.log("ready!");
//     // Agrega un evento de clic al enlace para limpiar el filtro de búsqueda
//     $('body').on('click', '.table-link', function () {
//         // Limpia el filtro de búsqueda de la tabla
//         dataTable.search('').columns().search('').draw();
//     });
// });




