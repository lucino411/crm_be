let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5, 6] },
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
        const organizationSlug = taskListElement.dataset.organizationSlug;
        const response = await fetch(`${BASE_URL}/${organizationSlug}/deal/tasks_json`);
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
            const modifiedTime = processDate(taskData.modified_time); 
                        
            content += `
            <tr>
                <td>
                    <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#dealTaskModal" onclick='showDealTaskDetail(${JSON.stringify(
                        taskData
                        )})'>${taskData.name}</a></p>            
                </td>
                <td>${taskData.deal_name}</td>
                <td>${taskData.product_name}</td>
                <td>${modifiedTime}</td>     
                <td>${taskData.created_by}</td>     
                <td>${taskData.assigned_to}</td>
                <td>${taskData.stage}</td>      
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

// Muestra los datos del Deal en el modal (Deal Detail)
function showDealTaskDetail(taskData) {
    if (typeof taskData === "string") {
      taskData = JSON.parse(taskData);
    }

    // Actualiza los elementos del modal con los datos del deal
    document.getElementById("modal-task-name").textContent = taskData.name;
       
    // taskData incluye un campo 'deal_id'
     const dealUpdateUrl = `/${taskData.organization__slug}/deal/${taskData.deal__id}/update/`; // Modifica según la estructura de tus URLs
     document.getElementById("modal-deal-name").innerHTML = `<a href="${dealUpdateUrl}">${taskData.deal_name}</a>`;
               
    
    document.getElementById("modal-product-name").textContent = taskData.product_name;
    // document.getElementById("modal-deal-name").textContent = taskData.deal_name;
    const modifiedTime = new Date(taskData.modified_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-modified-time").textContent = modifiedTime;
    document.getElementById('modal-modified-by').textContent = taskData.last_modified_by;
    document.getElementById("modal-assigned-to").textContent = taskData.assigned_to;
    document.getElementById("modal-stage").textContent = taskData.stage;

    // Agrega el enlace de actualización
    const updateLinkContainer = document.getElementById(
        "deal-task-update-link-container"
    );
    updateLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo

    // Crea el enlace solo si update_url está presente
    if (taskData.update_url) {
        const updateLink = document.createElement("a");
        updateLink.href = taskData.update_url; // Establece el URL del enlace
        updateLink.textContent = "Update"; // Texto del enlace
        updateLink.className = "btn btn-primary"; // Añade clases para estilos, por ejemplo, clases de Bootstrap

        updateLinkContainer.appendChild(updateLink); // Añade el enlace al contenedor
    }

    // Agrega el enlace de eliminacion
    const deleteLinkContainer = document.getElementById(
        "deal-task-delete-link-container"
    );
    deleteLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo

    // Crea el enlace solo si delete_url está presente
    if (taskData.delete_url) {
        const deleteLink = document.createElement("a");
        deleteLink.href = taskData.delete_url; // Establece el URL del enlace
        deleteLink.textContent = "Delete"; // Texto del enlace
        deleteLink.className = "btn btn-danger"; // Añade clases para estilos, por ejemplo, clases de Bootstrap

        deleteLinkContainer.appendChild(deleteLink); // Añade el enlace al contenedor
    }

}