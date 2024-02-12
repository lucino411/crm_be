let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5, 6, 7] },
        { orderable: false, targets: [0, 1, 2, 5] },
        { searchable: false, targets: [0, 1] },
    ],
    pageLength: 5,
    destroy: true,
    // dom: 'Bfrtip',
    dom: 'QBfrtip',

    initComplete: function () {
        let api = this.api();

        api.columns([3, 7]).every(function () {
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

    await listContacts();

    dataTable = $("#datatable-contacts").DataTable({
        ...dataTableOptions,
        select: true  // Agrega esta línea dentro de las opciones
    });    

    dataTableIsInitialized = true;
};


const listContacts = async () => {
    try {
        const contactListElement = document.getElementById('contact-list');
        const organizationSlug = contactListElement.dataset.organizationSlug;
        const response = await fetch(`${BASE_URL}/${organizationSlug}/contact/contacts_json`);
        const data = await response.json();
        let content = ``;
        
        data.contacts.forEach((contact, index) => {
            const contactData = contact;         

            // console.log(contactData); // Agrega esta línea para imprimir contactData en la consola
            const createdTime = new Date(contactData.created_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });
            // const modifiedTime = new Date(contactData.modified_time).toLocaleString('es', { day: 'numeric', month: 'short', year: 'numeric' });

            content += `
        <tr>
            <td>
                <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#leadContactModal" onclick='showLeadContactDetail(${JSON.stringify(
                    contactData
                    )})'>${contactData.first_name}</a>
                </p>            
            </td>
            <td>${contactData.last_name}</td>
            <td>${contactData.primary_email}</td>
            <td>${contactData.country}</td>
            <td>${createdTime}</td> 
            <td>${contactData.last_modified_by}</td> 
            <td>${contactData.organization}</td>      
            <td>${contactData.is_client  ? 'Cliente' : 'Contacto'}</td>
        </tr>
        `;
        });
        tableBody_contacts.innerHTML = content;
    } catch (e) {
        alert(e);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();
});

// Muestra los datos del Deal en el modal (Deal Detail)
function showLeadContactDetail(contactData) {
    if (typeof contactData === "string") {
      contactData = JSON.parse(contactData);
    }

    // Actualiza los elementos del modal con los datos del contact
    document.getElementById("modal-contact-first-name").textContent = contactData.first_name;                  
    document.getElementById("modal-contact-last-name").textContent = contactData.last_name;
    document.getElementById("modal-contact-primary-email").textContent = contactData.primary_email;
    document.getElementById("modal-contact-title").textContent = contactData.title;
    document.getElementById("modal-contact-phone").textContent = contactData.phone;
    document.getElementById("modal-contact-mobile-phone").textContent = contactData.mobile_phone;
    document.getElementById("modal-contact-company").textContent = contactData.company__company_name;
    const createdTime = new Date(contactData.created_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-contact-created-time").textContent = createdTime;
    document.getElementById('modal-contact-created-by').textContent = contactData.created_by;
    const modifiedTime = new Date(contactData.modified_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-contact-modified-time").textContent = modifiedTime;
    document.getElementById('modal-contact-modified-by').textContent = contactData.last_modified_by;
    document.getElementById("modal-contact-country").textContent = contactData.country;    

    // Mostrar leads asociados al contact
    const contactLeadsContainer = document.getElementById("modal-contact-leads");
    contactLeadsContainer.innerHTML = "<h5>Related Leads</h5>"; // Reiniciar el contenido y agregar título
    if (contactData.leads && contactData.leads.length) {
        const contactList = document.createElement("ul");
        contactData.leads.forEach((lead) => {
        const item = document.createElement("li");
        // Crear el enlace
        const link = document.createElement("a");
        link.setAttribute(
            "href",
            `/${contactData.organization__slug}/lead/${lead.id}/update/`
        );
        link.textContent = lead.lead_name;

        // Crear un elemento de lista y añadir el enlace a este elemento
        item.appendChild(link);
        contactList.appendChild(item);
        });
        contactLeadsContainer.appendChild(contactList);
    } else {
        contactLeadsContainer.innerHTML += "<p>There isn't a related lead.</p>";
    }

}




