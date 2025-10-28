[![Documentation Status](https://app.readthedocs.org/projects/idaesplus/badge/?version=latest)](https://idaesplus.readthedocs.io/latest)

# IDAES+ Documentation

This repository has the source code for the IDAES+ documentation,
which covers all projects that use the [IDAES](https://idaes.org) platform.

## Updating pages from Airtable

### Explanation

These pages have tables created from data in the IDAES+ project on Airtable.
[Airtable](https://airtable.com) is an online database that can be jointly
edited like a shared spreadsheet.

The current method of connecting this data to the documentation pages is to
fetch that data and format it as a YAML file. The downside to this procedure, as
opposed to fetching the data directly from within the documentation pages via
JavaScript, is an extra step to propagate changes from Airtable to the
documentation. The upside is that changes in the documentation are deployed
intentionally and not accidentally when the Airtable data is changed. This
should result in less surprises and more chances to check for errors.

### How-to

To update the file, run the `update_data.py` script and write the output to `data.yaml`.

For example: `python update_data.py data.yaml`

In order to connect to Airtable and retrieve the data, you will need to provide
the correct API key for IDAES+. This is a secret and not in this repository.
Once you have obtained this key either provide it directly on the command-line
or set it in the environment variable `IDAES_AIRTABLE_APIKEY`.

You can cache the data retrieved from Airtable with the `--cache` option, e.g.:
`python update_data.py data.yaml --cache cache.json`. In this mode, no new data
is fetched, but the raw data is reformatted for the web pages. This is useful
when working on the script itself. Note also that if the cache file exists the
script does not attempt to connect to Airtable, so the API key is not needed.
