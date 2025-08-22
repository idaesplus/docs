# IDAES Connectivity Tool

Quickly create visual diagrams showing the connectivity of flowsheet units and streams. 

{octicon}`mark-github` [GitHub repository](https://github.com/prommis/idaes-connectivity)

{octicon}`book` [Documentation](https://prommis.github.io/idaes-connectivity/)

## Major Features

* Python library to generate connectivity data in useful formats
* Run from command-line, script, or Jupyter Notebook
* View connectivity in text-based diagrams Mermaid or D2
* Add unit names, stream names, and user-defined annotations
* Export connectivity as a table (CSV) for re-use in other tools

## Compatibility

Runs on all Pyomo models and IDAES-based flowsheets.
Pure Python code, runs on Windows, MacOS, and Linux.

## Screenshots

You can run the `idaes-conn` command line tool with a Python module, 
invoking the `build()` function to build the model, and
translating the output into a [Mermaid][mermaidjs] diagram.
```
idaes-conn example.py --to mermaid --labels
```

Output:
```{figure} ../../_static/img/example_mermaid.png
Example mermaid chart
```

[mermaidjs]: https://mermaid.js.org