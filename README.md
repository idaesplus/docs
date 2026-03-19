[![Documentation Status](https://app.readthedocs.org/projects/idaesplus/badge/?version=latest)](https://idaesplus.readthedocs.io/latest)

# IDAES+ Documentation

This repository has the source code for the IDAES+ documentation,
which covers all projects that use the [IDAES](https://idaes.org) platform.

## Updating tabular input data

The data that builds tables of content for several pages is in CSV files under  data/. 
Filenames in that directory should correspond to Markdown files they belong to.
This data is post-processed into YAML that is then used by the documentation pages
to create content.

To update the CSV, just use your favorite spreadsheet program or
a text editor. Make sure to save as plain CSV again, and commit your
changes to the repository.

When you're done, you need to update the YAML input files from the CSV,
run the `update_data.py` script and write the output to `data.yaml`.

For example: `python update_data.py data.yaml`
