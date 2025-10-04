---
title: IDAES+ Projects
---
# IDAES+ Projects

````{datatemplate:yaml} data.yaml
```{raw} html
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDAES+ Projects</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css">
    </head>
    <body>
        <table id="idaesplus-projects" class="display" style="width:100%"></table>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function () {
                // hack to make width match window
                $('.wy-nav-content')[0].style['max-width'] = 'none';
                var data = {{ data.projects | tojson }};
                $('#idaesplus-projects').DataTable({
                    data: data,
                    columns: [
                        { title: "Name", data: "name"},
                        {
                          title: "Website",
                          data: "website",
                          render: function (data, type, row, meta) {
                            return `<a href="${data}" target="_blank">🔗</a>`
                          }
                        },
                        {
                            title: "Description",
                            data: "description",
                        },
                        {
                          title: "Active",
                          data: "active",
                        },
                        {
                          title: "Keywords",
                          data: "keywords",
                          render: function (data, type, row, meta) {
                            return data.join(", ")
                          }
                        }
                    ]
                });
            });
        </script>
    </body>
    </html>
```
````
