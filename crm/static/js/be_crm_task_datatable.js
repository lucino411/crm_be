let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 2, 5] },
        { searchable: false, targets: [0, 1] },
    ],
    pageLength: 8,
    destroy: true,
    // dom: 'Bfrtip',
    dom: 'QBfrtip',

    initComplete: function () {
        let api = this.api();

        api.columns([5]).every(function () {
            let column = this;

            let select = document.createElement('select');
            select.add(new Option(''));
            column.footer().replaceChildren(select);

            select.addEventListener('change', function () {
                var val = DataTable.util.escapeRegex(select.value);

                column
                    .search(val ? '^' + val + '$' : '', true, false)
                    .draw();
            });

            column
                .data()
                .unique()
                .sort()
                .each(function (d, j) {
                    select.add(new Option(d));
                });
        });

        // Hace un filtro al hacer clic sobre cualquier campo, menos en la columna 0
        api.on('click', 'tbody td', function (e) {
            let columnIndex = api.cell(this).index().column;

            // Si el índice de la columna es diferente de 0, realiza la búsqueda
            if (columnIndex !== 0 && columnIndex !== 1) {
                api.search(this.innerHTML).draw();
            }
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
    }

    await listTasks();

      
    dataTable = $("#datatable-tasks").DataTable({
        ...dataTableOptions,
        select: true  // Agrega esta línea dentro de las opciones
    });

    dataTableIsInitialized = true;
};


const listTasks = async () => {
    try {
        const taskListElement = document.getElementById('task-list');
        const organizationName = taskListElement.dataset.organizationName;
        const response = await fetch(`${BASE_URL}/${organizationName}/lead/tasks_json`);
        const data = await response.json();
        let content = ``;
        
        data.tasks.forEach((task, index) => {
            const taskData = task;

            // Define un método para procesar las fechas
            const processDate = (dateString) => {
                if (dateString) {
                    return new Date(dateString).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });
                } else {
                    return "Sin asignar";  // O puedes poner 'null' o cualquier mensaje que prefieras
                }
            };

            // console.log(taskData); // Agrega esta línea para imprimir taskData en la consola
            // Procesa las fechas utilizando el método definido
            const endTime = processDate(taskData.end_date_time);
            const extendedEndTime = processDate(taskData.extended_end_date_time);
            const modifiedTime = processDate(taskData.modified_time);

            // Decidir cuál tiempo mostrar
            let displayEndTime = extendedEndTime !== "Sin asignar" ? extendedEndTime : endTime; 


            content += `
        <tr>
            <td><a href="/${taskData.organization}/lead/task/${taskData.id}/" class='table-link'>${taskData.name}</a></td>
            <td>${taskData.lead_name}</td>
            <td>${taskData.product_name}</td>
            <td>${modifiedTime}</td>     
            <td>${displayEndTime}</td>
            <td>${taskData.assigned_to}</td>
        </tr>
        `;
        });
        tableBody_tasks.innerHTML = content;
    } catch (e) {
        alert(e);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();
});

// A $( document ).ready() block.
// $(document).ready(function () {
//     console.log("ready!");
//     // Agrega un evento de clic al enlace para limpiar el filtro de búsqueda
//     $('body').on('click', '.table-link', function () {
//         // Limpia el filtro de búsqueda de la tabla
//         dataTable.search('').columns().search('').draw();
//     });
// });




