let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5, 6, 7] },
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
      
    dataTable = $("#datatable-companies").DataTable({
        ...dataTableOptions,
        select: true  // Agrega esta línea dentro de las opciones
    });

    dataTableIsInitialized = true;
};


const listTasks = async () => {
    try {
        const companyListElement = document.getElementById('company-list');
        const organizationSlug = companyListElement.dataset.organizationSlug;
        const response = await fetch(`${BASE_URL}/${organizationSlug}/company/companies_json`);
        const data = await response.json();
        let content = ``;
        
        data.companies.forEach((company, index) => {
            const companyData = company;

            // Define un método para procesar las fechas
            const processDate = (dateString) => {
                if (dateString) {
                    return new Date(dateString).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });
                } else {
                    return "Sin asignar";  // O puedes poner 'null' o cualquier mensaje que prefieras
                }
            };

            // console.log(companyData); // Agrega esta línea para imprimir companyData en la consola
            // Procesa las fechas utilizando el método definido
            const modifiedTime = processDate(companyData.modified_time); 


            content += `
        <tr>
            <td>
                <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#dealCompanyModal" onclick='showDealCompanyDetail(${JSON.stringify(
                    companyData
                    )})'>${companyData.company_name}</a>
                </p>            
            </td>
            <td>${companyData.company_email}</td>
            <td>${companyData.company_phone}</td>
            <td>${companyData.website}</td>
            <td>${companyData.industry}</td>
            <td>${modifiedTime}</td>     
            <td>${companyData.created_by}</td>     
            <td>${companyData.industry}</td>
        </tr>
        `;
        });
        tableBody_companies.innerHTML = content;
    } catch (e) {
        alert(e);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();
});

// Muestra los datos del Deal en el modal (Deal Detail)
function showDealCompanyDetail(companyData) {
    if (typeof companyData === "string") {
      companyData = JSON.parse(companyData);
    }
    
    // Actualiza los elementos del modal con los datos del company
    document.getElementById("modal-company-name").textContent = companyData.company_name;                  
    document.getElementById("modal-company-email").textContent = companyData.company_email;
    document.getElementById("modal-company-phone").textContent = companyData.company_phone;
    document.getElementById("modal-company-website").textContent = companyData.website;
    document.getElementById("modal-company-industry").textContent = companyData.industry;
    document.getElementById('modal-company-modified-by').textContent = companyData.last_modified_by;
    document.getElementById('modal-company-created-by').textContent = companyData.created_by;
    const createdTime = new Date(companyData.created_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-company-created-time").textContent = createdTime;
    const modifiedTime = new Date(companyData.modified_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-company-modified-time").textContent = modifiedTime;


// Mostrar deals asociados al company
const companyDealsContainer = document.getElementById("modal-company-deals");
companyDealsContainer.innerHTML = "<h5>Related Deals</h5>"; // Reiniciar el contenido y agregar título
if (companyData.deals && companyData.deals.length) {
    const companyList = document.createElement("ul");
    companyData.deals.forEach((deal) => {
    const item = document.createElement("li");
    // Crear el enlace
    const link = document.createElement("a");
    link.setAttribute(
        "href",
        `/${companyData.organization__slug}/deal/${deal.id}/update/`
    );
    link.textContent = deal.deal_name;

    // Crear un elemento de lista y añadir el enlace a este elemento
    item.appendChild(link);
    companyList.appendChild(item);
    });
    companyDealsContainer.appendChild(companyList);
} else {
    companyDealsContainer.innerHTML += "<p>There isn't a related deal.</p>";
}

// Mostrar clients asociados al company
const companyClientsContainer = document.getElementById("modal-company-clients");
companyClientsContainer.innerHTML = "<h5>Related Clients</h5>"; // Reiniciar el contenido y agregar título
if (companyData.clients && companyData.clients.length) {
    const companyList = document.createElement("ul");
    companyData.clients.forEach((client) => {
    const item = document.createElement("li");
    item.textContent = client.first_name;
    companyList.appendChild(item);
    });
    companyClientsContainer.appendChild(companyList);
} else {
    companyClientsContainer.innerHTML += "<p>There isn't a related client.</p>";
}








}