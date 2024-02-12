let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5, 6] },
        { orderable: false, targets: [0, 1, 2, 5] },
        { searchable: false, targets: [0, 1] },
    ],
    pageLength: 5,
    destroy: true,
    // dom: 'Bfrtip',
    dom: 'QBfrtip',

    initComplete: function () {
        let api = this.api();

        api.columns([3]).every(function () {
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
            if (columnIndex !== 0) {
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

    await listClients();

    dataTable = $("#datatable-clients").DataTable({
        ...dataTableOptions,
        select: true  // Agrega esta línea dentro de las opciones
    });    

    dataTableIsInitialized = true;
};


const listClients = async () => {
    try {
        const clientListElement = document.getElementById('client-list');
        const organizationSlug = clientListElement.dataset.organizationSlug;
        const response = await fetch(`${BASE_URL}/${organizationSlug}/client/clients_json`);
        const data = await response.json();
        let content = ``;
        
        data.clients.forEach((client, index) => {
            const clientData = client;         

            // console.log(clientData); // Agrega esta línea para imprimir clientData en la consola
            const createdTime = new Date(clientData.created_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });
            // const modifiedTime = new Date(clientData.modified_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });

            content += `
        <tr>
            <td>
                <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#dealClientModal" onclick='showDealClientDetail(${JSON.stringify(
                    clientData
                    )})'>${clientData.first_name}</a>
                </p>            
            </td>
            <td>${clientData.last_name}</td>
            <td>${clientData.primary_email}</td>
            <td>${clientData.phone}</td>      
            <td>${clientData.country}</td>
            <td>${createdTime}</td> 
            <td>${clientData.last_modified_by}</td> 
        </tr>
        `;
        });
        tableBody_clients.innerHTML = content;
    } catch (e) {
        alert(e);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();
});

// Muestra los datos del Deal en el modal (Deal Detail)
function showDealClientDetail(clientData) {
    if (typeof clientData === "string") {
      clientData = JSON.parse(clientData);
    }

    // Actualiza los elementos del modal con los datos del client
    document.getElementById("modal-client-first-name").textContent = clientData.first_name;                  
    document.getElementById("modal-client-last-name").textContent = clientData.last_name;
    document.getElementById("modal-client-primary-email").textContent = clientData.primary_email;
    document.getElementById("modal-client-title").textContent = clientData.title;
    document.getElementById("modal-client-phone").textContent = clientData.phone;
    document.getElementById("modal-client-mobile-phone").textContent = clientData.mobile_phone;
    document.getElementById("modal-client-company").textContent = clientData.company__company_name;
    const createdTime = new Date(clientData.created_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-client-created-time").textContent = createdTime;
    document.getElementById('modal-client-created-by').textContent = clientData.created_by;
    const modifiedTime = new Date(clientData.modified_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-client-modified-time").textContent = modifiedTime;
    document.getElementById('modal-client-modified-by').textContent = clientData.last_modified_by;
    document.getElementById("modal-client-country").textContent = clientData.country;
    
    // Mostrar deals asociados al client
    const clientDealsContainer = document.getElementById("modal-client-deals");
    clientDealsContainer.innerHTML = "<h5>Related Deals</h5>"; // Reiniciar el contenido y agregar título
    if (clientData.deals && clientData.deals.length) {
        const clientList = document.createElement("ul");
        clientData.deals.forEach((deal) => {
        const item = document.createElement("li");
        // Crear el enlace
        const link = document.createElement("a");
        link.setAttribute(
            "href",
            `/${clientData.organization__slug}/deal/${deal.id}/update/`
        );
        link.textContent = deal.deal_name;

        // Crear un elemento de lista y añadir el enlace a este elemento
        item.appendChild(link);
        clientList.appendChild(item);
        });
        clientDealsContainer.appendChild(clientList);
    } else {
        clientDealsContainer.innerHTML += "<p>There isn't a related deal.</p>";
    }

}




