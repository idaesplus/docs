---
title: IDAES+ Models
---
# IDAES+ Models
Select model (click on its row) to see all fields, including full descriptions.

````{datatemplate:yaml} data.yaml
```{raw} html
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDAES+ Models</title>
        <link href="https://cdn.datatables.net/v/dt/dt-2.3.4/datatables.min.css" rel="stylesheet" integrity="sha384-pmGS6IIcXhAVIhcnh9X/mxffzZNHbuxboycGuQQoP3pAbb0SwlSUUHn2v22bOenI" crossorigin="anonymous">
    </head>
    <body>
        <dialog id="idaesplus-details" closedby="any"></dialog>
        <table id="idaesplus-models" class="display" style="width:100%"></table>
        <script src="https://cdn.datatables.net/v/dt/dt-2.3.4/datatables.min.js" integrity="sha384-X2pTSfom8FUa+vGQ+DgTCSyBZYkC1RliOduHa0X96D060s7Q//fnOh3LcazRNHyo" crossorigin="anonymous"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const data = {{ data.models | tojson }};
                const repo_list = (data) => {
                    const items = Object.entries(data).map((kvp) => `<li><a href='${kvp[1]}' target='_blank'>${kvp[0]}</a></li>`);
                    return `<ul class='idaesplus-cell'>${items.join("")}</ul>`;
                }
                const table = new DataTable("#idaesplus-models", {
                    scrollX: true,
                    data: data,
                    columns: [
                        { title: "Name", data: "name"},
                        { title: "Project", data: "project"},
                        {
                            title: "Description",
                            data: "description",
                        },
                        {
                          title: "Flowsheet module",
                          data: "flowsheet_module"
                        },
                        {
                          title: "Unit model(s)",
                          data: "unit_model_data",
                          render: (data) => (data ? repo_list(data) : "")
                        },
                        {
                          title: "Property package(s)",
                          data: "property_package_data",
                          render: (data) => (data ? repo_list(data) : "")
                        },
                        {
                          title: "Reaction package(s)",
                          data: "reaction_package_data",
                          render: (data) => (data ? repo_list(data) : "")
                        },
                        {
                          title: "Control volume(s)",
                          data: "control_volume_data",
                          render: (data) => (data ? repo_list(data) : "")
                        },
                    ]
                });
                // Show details on name click
                table.on('click', 'tbody tr', function (e) {
                  if (e.target.nodeName == "A") return; // hyperlink
                  const data = table.row(this).data();
                  const dialogId = "idaesplus-details";
                  let fields = [
                    ["description", "Description"],
                    ["flowsheet_module", "Flowsheet Module"],
                    ["unit_models", "Unit Models"], ["unit_model_repositories", "Unit Model Repositories"], 
                    ["property_packages", "Property Packages"], ["property_package_repositories", "Property Package Repositories"], 
                    ["reaction_packages", "Reaction Packages"], ["reaction_package_repositories", "Reaction Package Repositories"],
                    ["control_volumes", "Control Volume Packages"], ["control_volume_repositories","Control Volume Package Repositories"],
                    ["configurations", "Configurations"], 
                    ["specifications_for_operating_conditions", "Operating Conditions"]
                  ];
                  if (data["full_description"] !== undefined) {
                    fields.splice(0, 1, ["full_description", "Description"])
                  }
                  const fieldList = fields.map((item) => "<li><span class='field-term'>" + item[1] + "</span><span class='field-val'>" + (data[item[0]] ?? "-") + "</span></li>");
                  document.getElementById(dialogId).innerHTML = "<h1>" + data["name"] + "</h1><ul>" + fieldList.join("") + "</ul>";
                  document.getElementById(dialogId).showModal();
                });
            });
        </script>
    </body>
    </html>
```
````
