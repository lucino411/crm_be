let dataTable;
let dataTableIsInitialized = false;
let dataOption;

const dataTableOptions = {
  columnDefs: [
    { className: "centered", targets: [0, 1, 2, 3, 4, 5, 6, 7, 8] },
    { orderable: false, targets: [0, 1, 2, 5, 8] },
    { searchable: false, targets: [0, 1] },
  ],
  pageLength: 10,
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

  await listDeals();

  dataTable = $("#datatable-deals").DataTable({
    ...dataTableOptions,
    select: true, // Agrega esta línea dentro de las opciones
  });

  dataTableIsInitialized = true;
};

const listDeals = async () => {
  try {
    const dealListElement = document.getElementById("deal-list");
    // console.log(dealListElement);
    const organizationSlug = dealListElement.dataset.organizationSlug;
    const response = await fetch(
      `${BASE_URL}/${organizationSlug}/deal/deals_json`
    );
    const data = await response.json();
    // console.log(response);
    let content = ``;

    data.deals.forEach((deal, index) => {
      const dealData = deal;

      // console.log(dealData); // Agrega esta línea para imprimir dealData en la consola
      const createdTime = new Date(dealData.created_time).toLocaleString("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });

      content += `
        <tr>
            <td> 
                <p class="p-3 m-0"><a href="#" class="link-opacity-75-hover" data-bs-toggle="modal" data-bs-target="#dealDetailModal" onclick='showDealDetail(${JSON.stringify(
                dealData
                )})'>${dealData.deal_name}</a></p>
            </td>
            <td> ${dealData.first_name}</td>
            <td>${dealData.last_name}</td>
            <td>${dealData.primary_email}</td>
            <td>${dealData.country}</td>
            <td>${createdTime}</td> 
            <td>${dealData.last_modified_by}</td> 
            <td>${dealData.assigned_to}</td>
            <td>${dealData.stage}</td>      
        </tr>
        `;
    });
    tableBody_deals.innerHTML = content;
  } catch (e) {
    alert(e);
  }
};

window.addEventListener("load", async () => {
  await initDataTable();
});

// Muestra los datos del Deal en el modal (Deal Detail)
function showDealDetail(dealData) {
  if (typeof dealData === "string") {
    dealData = JSON.parse(dealData);
  }

  // Actualiza los elementos del modal con los datos del deal
  document.getElementById("modal-deal-name").textContent = dealData.deal_name;
  document.getElementById("modal-first-name").textContent = dealData.first_name;
  document.getElementById("modal-last-name").textContent = dealData.last_name;
  // document.getElementById('modal-deal-source').textContent = dealData.deal_source;
  document.getElementById('modal-stage').textContent = dealData.stage;
  document.getElementById("modal-primary-email").textContent =
    dealData.primary_email;
  document.getElementById("modal-assigned-to").textContent =
    dealData.assigned_to;
  document.getElementById("modal-phone").textContent = dealData.phone;
  document.getElementById("modal-mobile-phone").textContent =
    dealData.mobile_phone;
  document.getElementById("modal-country").textContent = dealData.country;
  document.getElementById("modal-company").textContent = dealData.company_name;
  document.getElementById("modal-modified-by").textContent =
    dealData.last_modified_by;
  const modifiedTime = new Date(dealData.modified_time).toLocaleString("es", {
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
    "deal-update-link-container"
  );
  updateLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo

  // Crea el enlace solo si update_url está presente
  if (dealData.update_url) {
    const updateLink = document.createElement("a");
    updateLink.href = dealData.update_url; // Establece el URL del enlace
    updateLink.textContent = "Update"; // Texto del enlace
    updateLink.className = "btn btn-primary"; // Añade clases para estilos, por ejemplo, clases de Bootstrap

    updateLinkContainer.appendChild(updateLink); // Añade el enlace al contenedor
  }

  // Agrega el enlace de eliminacion
  const deleteLinkContainer = document.getElementById(
    "deal-delete-link-container"
  );
  deleteLinkContainer.innerHTML = ""; // Limpia el contenedor por si hay contenido previo

  // Crea el enlace solo si delete_url está presente
  if (dealData.delete_url) {
    const deleteLink = document.createElement("a");
    deleteLink.href = dealData.delete_url; // Establece el URL del enlace
    deleteLink.textContent = "Delete"; // Texto del enlace
    deleteLink.className = "btn btn-danger"; // Añade clases para estilos, por ejemplo, clases de Bootstrap

    deleteLinkContainer.appendChild(deleteLink); // Añade el enlace al contenedor
  }

  // Mostrar productos asociados al deal
  const dealProductsContainer = document.getElementById("modal-deal-products");
  dealProductsContainer.innerHTML = "<h5>Related Products</h5>"; // Reiniciar el contenido y agregar título
  if (dealData.deal_products && dealData.deal_products.length) {
    const productList = document.createElement("ul");
    dealData.deal_products.forEach((product) => {
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
    dealProductsContainer.appendChild(productList);
  } else {
    dealProductsContainer.innerHTML += "<p>There isn't a related product.</p>";
  }

  // Mostrar tareas asociadas al deal
  const dealTasksContainer = document.getElementById("modal-deal-tasks");
  dealTasksContainer.innerHTML = "<h5>Related Tasks</h5>"; // Reiniciar el contenido y agregar título
  if (dealData.deal_tasks && dealData.deal_tasks.length) {
    const taskList = document.createElement("ul");
    dealData.deal_tasks.forEach((task) => {
      const item = document.createElement("li");
      // Crear el enlace
      const link = document.createElement("a");

      link.setAttribute(
        "href",
        `/${dealData.organization_slug}/deal/task/${task.id}/update/`
      );
      link.textContent = task.name;

      // Crear un elemento de lista y añadir el enlace a este elemento
      item.appendChild(link);
      taskList.appendChild(item);
    });
    dealTasksContainer.appendChild(taskList);
  } else {
    dealTasksContainer.innerHTML += "<p>There isn't a related task.</p>";
  }
}
