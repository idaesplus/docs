---
title: IDAES+ Models
---
# IDAES+ Models

````{datatemplate:yaml} data.yaml
```{raw} html
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDAES+ Models</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css">
    </head>
    <body>
        <table id="idaesplus-models" class="display" style="width:100%"></table>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function () {
              // hack to make width match window
              $('.wy-nav-content')[0].style['max-width'] = 'none';
                var data = {{ data.models | tojson }};
                console.debug("data = ", data);
                $('#idaesplus-models').DataTable({
                    data: data,
                    columns: [
                        { title: "Name", data: "name"},
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
                          data: "unit_models"
                        },
                        {
                          title: "Property package",
                          data: "property_package"
                        },
                        {
                          title: "Reaction package",
                          data: "reaction_package"
                        },
                    ]
                });
            });
        </script>
    </body>
    </html>
```
````
