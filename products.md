---
title: IDAES+ Software Products
---

# IDAES+ Software Products

````{datatemplate:yaml} data.yaml
```{raw} html
    <!DOCTYPE html>
    <html>
    <head>
        <title>IDAES+ Projects</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css">
    </head>
    <body>
        <table id="idaesplus-products" class="display" style="width:100%"></table>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function () {
                function shieldsIO (text, color, logo) {
                  const normalized = text.replace("-", "--");
                  return `<img alt="${text}" src="https://img.shields.io/badge/${normalized}-${color}?logo=${logo}"></img>`
                };
                function simpleIconsLink (url, color, logo) {
                  const size = 32;
                  return `<a href="${url}" target="_blank"><img height="${size}" width="${size}" style="display:inline-block" src="https://cdn.simpleicons.org/${logo}"></img></a>`
                }
                function renderGitHub (repository) {
                  return simpleIconsLink(`https://github.com/${repository}`, "black", "github");
                };
                function renderPyPI (name) {
                  return simpleIconsLink(`https://pypi.org/project/${name}`, "blue", "pypi");
                };
                function renderCondaForge (name) {
                  return simpleIconsLink(`https://anaconda.org/conda-forge/${name}`, "gray", "condaforge");
                }
                var data = {{ data.products | tojson }};
                $('#idaesplus-products').DataTable({
                    data: data,
                    columns: [
                        { title: "Name", data: "name"},
                        {
                            title: "Description",
                            data: "description",
                        },
                        {
                          title: "Code",
                          data: "code",
                          render: function (data, type, row, meta) {
                            var items = [];
                            if (data.github) {
                              items.push(renderGitHub(data.github));
                            };
                            if (data.pypi) {
                              items.push(renderPyPI(data.pypi));
                            };
                            if (data["conda-forge"]) {
                              items.push(renderCondaForge(data["conda-forge"]));
                            }
                            return `<span>${items.join("")}</span>`;
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
