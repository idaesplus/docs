# IDAES+ Documentation

This repository has the source code for the IDAES+ documentation,
which covers all projects that use the [IDAES](https://idaes.org) platform.

## Updating pages from Airtable

### What and Why

These pages have tables created from data in the IDAES+ project on Airtable.
[Airtable](https://airtable.com) is a central spreadsheet-like database that can be jointly
edited by the team.

The current method of connecting this data to the documentation pages
is to fetch that data and format it as a YAML file:
  - The downside to this procedure, as opposed to fetching the data directly from
    within the documentation pages via JavaScript, is an extra step to propagate changes
    from Airtable to the documentation.
  - The upside is that changes in the documentation are deployed intentionally and
    not accidentally when the Airtable data is changed. This should result in 
    less surprises and more chances to check for errors.

### How

To update the file, run the `airtable.py` script and write the output to `data.yaml`.
For example: `python airtable.py data.yaml`
Run `airtable.py -h` for help on arguments.
