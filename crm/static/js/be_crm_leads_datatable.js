let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
  columnDefs: [
    { className: "centered", targets: [0, 1, 2, 3, 4, 5, 6, 7, 8] },
    { orderable: false, targets: [0, 1, 2, 5, 8] },
    { searchable: false, targets: [0, 1] },
  ],
  pageLength: 15,
  destroy: true,
  // dom: 'Bfrtip',
  dom: "QBfrtip",

  initComplete: function () {
    let api = this.api();

    api.columns([4, 8]).every(function () {
      let column = this;

      let select = document.createElement("select");
      select.add(new Option(""));
      column.footer().replaceChildren(select);

      select.addEventListener("change", function () {
        var val = DataTable.util.escapeRegex(select.value);

        column.search(val ? "^" + val + "$" : "", true, false).draw();
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
    api.on("click", "tbody td", function (e) {
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
      extend: "collection",
      text: "Exportar",
      buttons: [
        {
          extend: "csv",
          text: "<u>C</u>SV",
          key: {
            key: "c",
            altKey: true,
          },
        },
        {
          extend: "print",
          text: "<u>P</u>rint",
          key: {
            key: "p",
            altKey: true,
          },
        },
        {
          extend: "pdf",
          text: "<u>P</u>DF",
          key: {
            key: "p",
            altKey: true,
          },
        },
      ],
    },
  ],
};

const initDataTable = async () => {
  if (dataTableIsInitialized) {
    dataTable.destroy();
  }

  await listLeads();

  dataTable = $("#datatable-leads").DataTable({
    ...dataTableOptions,
    select: true, // Agrega esta línea dentro de las opciones
  });

  dataTableIsInitialized = true;
};

const listLeads = async () => {
  try {
    const leadListElement = document.getElementById("lead-list");
    // console.log(leadListElement);
    const organizationSlug = leadListElement.dataset.organizationSlug;
    const response = await fetch(
      `${BASE_URL}/${organizationSlug}/lead/leads_json`
    );
    const data = await response.json();
    // console.log(response);
    let content = ``;

    data.leads.forEach((lead, index) => {
      const leadData = lead;

      // console.log(leadData); // Agrega esta línea para imprimir leadData en la consola
      const createdTime = new Date(leadData.created_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });

      content += `
        <tr>
            <td>
                <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#leadDetailModal" onclick='showDealDetails(${JSON.stringify(
                    leadData
                )})'>${leadData.lead_name}</a></p>        
            </td>
            <td>${leadData.first_name}</td>
            <td>${leadData.last_name}</td>
            <td>${leadData.primary_email}</td>
            <td>${leadData.country}</td>
            <td>${createdTime}</td> 
            <td>${leadData.last_modified_by}</td> 
            <td>${leadData.assigned_to}</td>
            <td>${leadData.stage}</td>      
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

// Muestra los datos del Deal en el modal (Deal Detail)
function showDealDetails(leadData) {
    // Asegúrate de que leadData es un objeto
    if (typeof leadData === "string") {
      leadData = JSON.parse(leadData);
    }
  
    // Actualiza los elementos del modal con los datos del lead
    document.getElementById("modal-lead-name").textContent = leadData.lead_name;
    document.getElementById("modal-first-name").textContent = leadData.first_name;
    document.getElementById("modal-last-name").textContent = leadData.last_name;
    // document.getElementById('modal-lead-source').textContent = leadData.lead_source;
    document.getElementById('modal-stage').textContent = leadData.stage;
    document.getElementById("modal-primary-email").textContent =
      leadData.primary_email;
    document.getElementById("modal-assigned-to").textContent =
      leadData.assigned_to;
    document.getElementById("modal-phone").textContent = leadData.phone;
    document.getElementById("modal-mobile-phone").textContent =
      leadData.mobile_phone;
    document.getElementById("modal-country").textContent = leadData.country;
    document.getElementById("modal-company").textContent = leadData.company_name;
    document.getElementById("modal-modified-by").textContent =
      leadData.last_modified_by;
    const modifiedTime = new Date(leadData.modified_time).toLocaleString("es", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true, // Cambiar a false si prefieres el formato de 24 horas
    });
    document.getElementById("modal-modified-time").textContent = modifiedTime;
  
    // Agrega el enlace de actualización
    const updateLinkContainer = document.getElementById(
      "lead-update-link-container"
    );
    updateLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo
  
    // Crea el enlace solo si update_url está presente
    if (leadData.update_url) {
      const updateLink = document.createElement("a");
      updateLink.href = leadData.update_url; // Establece el URL del enlace
      updateLink.textContent = "Update"; // Texto del enlace
      updateLink.className = "btn btn-primary"; // Añade clases para estilos, por ejemplo, clases de Bootstrap
  
      updateLinkContainer.appendChild(updateLink); // Añade el enlace al contenedor
    }
  
    // Agrega el enlace de eliminacion
    const deleteLinkContainer = document.getElementById(
      "lead-delete-link-container"
    );
    deleteLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo
  
    // Crea el enlace solo si delete_url está presente
    if (leadData.delete_url) {
      const deleteLink = document.createElement("a");
      deleteLink.href = leadData.delete_url; // Establece el URL del enlace
      deleteLink.textContent = "Delete"; // Texto del enlace
      deleteLink.className = "btn btn-danger"; // Añade clases para estilos, por ejemplo, clases de Bootstrap
  
      deleteLinkContainer.appendChild(deleteLink); // Añade el enlace al contenedor
    }
  
    // Mostrar productos asociados al lead
    const leadProductsContainer = document.getElementById("modal-lead-products");
    leadProductsContainer.innerHTML = "<h5>Productos Asociados</h5>"; // Reiniciar el contenido y agregar título
    if (leadData.lead_products && leadData.lead_products.length) {
      const productList = document.createElement("ul");
      leadData.lead_products.forEach((product) => {
        const item = document.createElement("li");
  
        const link = document.createElement("a");
        link.href = product.product_url; // Usa el product_url para el enlace
        link.textContent = product.product__name; // Asume que también envías el nombre del producto
        link.target = "_blank"; // Opcional: abre el enlace en una nueva pestaña
  
        // Añade el enlace al elemento de la lista (li)
        item.appendChild(link); // Aquí es donde necesitas añadir el enlace al item, no establecer el textContent de item
        // Añade el elemento de la lista al contenedor de la lista de productos
        productList.appendChild(item);
      });
      leadProductsContainer.appendChild(productList);
    } else {
      leadProductsContainer.innerHTML += "<p>No hay productos asociados.</p>";
    }
  
    // Mostrar tareas asociadas al lead
    const leadTasksContainer = document.getElementById("modal-lead-tasks");
    leadTasksContainer.innerHTML = "<h5>Tareas Asociadas</h5>"; // Reiniciar el contenido y agregar título
    if (leadData.lead_tasks && leadData.lead_tasks.length) {
      const taskList = document.createElement("ul");
      leadData.lead_tasks.forEach((task) => {
        const item = document.createElement("li");
        // Crear el enlace
        const link = document.createElement("a");
  
        link.setAttribute(
          "href",
          `/${leadData.organization_slug}/lead/task/${task.id}/update/`
        );
        link.textContent = task.name;
  
        // Crear un elemento de lista y añadir el enlace a este elemento
        item.appendChild(link);
        taskList.appendChild(item);
      });
      leadTasksContainer.appendChild(taskList);
    } else {
      leadTasksContainer.innerHTML += "<p>No hay tareas asociadas.</p>";
    }
  }
  
