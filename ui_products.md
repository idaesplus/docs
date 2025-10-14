---
title: IDAES+ UI Products
---
# IDAES+ UI Products
User interfaces for IDAES+ models.

````{datatemplate:yaml} data.yaml
```{raw} html
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDAES+ UIs</title>
        <link href="https://cdn.datatables.net/v/dt/dt-2.3.4/datatables.min.css" rel="stylesheet" integrity="sha384-pmGS6IIcXhAVIhcnh9X/mxffzZNHbuxboycGuQQoP3pAbb0SwlSUUHn2v22bOenI" crossorigin="anonymous">
    </head>
    <body>
        <dialog id="idaesplus-screenshots" closedby="any"></dialog>
        <table id="idaesplus-ui" class="display" style="width:100%"></table>
        <script src="https://cdn.datatables.net/v/dt/dt-2.3.4/datatables.min.js" integrity="sha384-X2pTSfom8FUa+vGQ+DgTCSyBZYkC1RliOduHa0X96D060s7Q//fnOh3LcazRNHyo" crossorigin="anonymous"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const data = {{ data.ui_products | tojson }};
                const feature_list = (data) => {
                    const listItems = data.map((s) => `<li>${s}</li>`);
                    return `<ul class="idaesplus-ui-features">${listItems.join("")}</ul>`;
                }
                const table = new DataTable("#idaesplus-ui", {
                    scrollX: true,
                    data: data,
                    columnDefs: [{ width: '20%', targets: 2}],
                    columns: [
                        { title: "Name", data: "name"},
                        {
                          title: "Links",
                          data: "links",
                          render: (data) => (data ? 
                            (data.gh ? `<a href="${data.gh}"><img src="_static/img/github.svg" width=20px /></a>` : "") + "&nbsp;" + 
                            (data.docs ? `<a href="${data.docs}"><img src="_static/img/docs.svg" width=20px /></a>` : "") : "") + "&nbsp;" +
                            (data.screenshots ? `<img name="${data.screenshots}" ` + 'class="idaesplus-screenshot" src="_static/img/screenshot.svg" width=20px />' : "")
                        },
                        {
                            title: "Description",
                            data: "description",
                        },
                        {
                          title: "Features",
                          data: "features",
                          render: (data) => (data ? feature_list(data) : "")
                        },
                        {
                          title: "Compatibility",
                          data: "modelcompatibility",
                          render: (data) => data.join(", ")
                        }
                    ]
                });
                // Pop-up dialog to show screenshots
                document.querySelectorAll(".idaesplus-screenshot").forEach((item) => {
                  item.addEventListener("click", (e) => {
                    const product = data.find((rec) => rec.name == item.name);
                    const dialog = document.getElementById("idaesplus-screenshots");
                    const sections = product.screenshots.map((item) =>
                      "<div>" +
                      `<h2>${item.title}</h2>` +
                      "<ul>" + 
                      item.description.map((desc) => `<li>${desc}</li>`).join("") +
                      "</ul>" +
                      `<img src=_static/img/${item.image} />` +
                      "</div>"
                    );
                    const sectionList = sections.join("\n");
                    dialog.innerHTML = `<div class="idaesplus-screenshot-details"><h1>${product.name} screenshots</h1><ul>${sectionList}</ul></div>`;
                    dialog.showModal();
                  });
                });
            });
        </script>
    </body>
    </html>
```
````
