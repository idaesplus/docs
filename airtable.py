"""
Download tables from Airtable and output YAML
"""

import argparse
import json
import logging
import os
from pathlib import Path
import requests
import sys
from typing import Any
import yaml

# third-party packages
from markdown import markdown

__author__ = "Dan Gunter (LBNL)"

TOKENV = "IDAES_AIRTABLE_APIKEY"

_log = logging.getLogger("idaes_airtable")
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(levelname)s %(name)s %(asctime)s - %(message)s"))
_log.addHandler(_h)


class IdaesplusAirtable:
    url = "https://api.airtable.com/v0"
    baseid = "appcXhVXfV2YOYrrM"
    table_names = ("projects", "products", "models")

    def __init__(self, tok):
        self._tok = tok

    def get_tables(self):
        tables = {}
        for table_name in self.table_names:
            url = f"{self.url}/{self.baseid}/{table_name}"
            _log.debug(f"Begin:Request url={url}")
            d = requests.get(url, headers={"Authorization": f"Bearer {self._tok}"})
            _log.debug(f"End:Request url={url} ; status={d.status_code}")
            if d.status_code != 200:
                if d.status_code == 401:
                    raise RuntimeError(f"Unauthorized. Check your API key")
                else:
                    raise RuntimeError(f"Fetching '{url}': HTTP status {d.status_code}")
            tables[table_name] = d.json()["records"]
        return tables

    @classmethod
    def dump_tables(cls, path, tables):
        report = {}
        y = {}
        for table_name, table_contents in tables.items():
            y[table_name] = []
            for record in table_contents:
                r = {"id": record["id"]}
                norm_fields = {
                    key.lower().replace(" ", "_"): value
                    for key, value in record["fields"].items()
                }
                r.update(cls.postprocess(table_name, norm_fields))
                y[table_name].append(r)
            report[table_name] = {"records": len(y[table_name])}
        with path.open("w") as f:
            yaml.dump(y, stream=f)
        return report

    @classmethod
    def postprocess(cls, table_name: str, fields: dict[str, Any]):
        if table_name == "projects":
            fields["active"] = bool(fields["development"].lower() == "active")
        elif table_name == "products":
            # move 'code' fields into a nested dict
            fields["code"] = {}
            for code_field in ("github", "pypi", "conda-forge"):
                if code_field in fields:
                    fields["code"][code_field] = fields[code_field]
                    del fields[code_field]
        elif table_name == "models":
            # fill in blank values for certain required fields
            for req_field in (
                "flowsheet_module",
                "unit_models",
                "property_package",
                "reaction_package",
            ):
                if req_field not in fields:
                    fields[req_field] = ""
            fields["description"] = markdown(fields["description"])
        return fields


def get_token(t):
    if t:
        return t

    try:
        return os.environ[TOKENV]
    except KeyError:
        raise KeyError(
            f"Please provide the token via the -t/--token option "
            f"or by setting the environment variable {TOKENV}"
        )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output_file", metavar="PATH", help="YAML output file")
    p.add_argument(
        "--cache",
        metavar="FILE",
        help="For local testing, use cached JSON data in FILE "
        "instead of querying Airtable; "
        "If the file does not exist it will be created from Airtable first",
        default=None,
    )
    p.add_argument("-t", "--token", help=f"API token, otherwise look in {TOKENV}")
    p.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase log verbosity"
    )
    args = p.parse_args()

    if args.verbose > 1:
        _log.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        _log.setLevel(logging.INFO)
    else:
        _log.setLevel(logging.WARNING)

    output_path = Path(args.output_file)
    if not output_path.parent.exists():
        _log.fatal(
            f"Output directory '{output_path.parent}' not found. "
            f"Please create it or provide a different path."
        )
        return 1

    if args.cache:
        p = Path(args.cache)
        # if existing file, load it
        if p.exists():
            _log.info(f"Loading data from cache file '{p}'")
            with p.open() as f:
                tables = json.load(f)
        # otherwise query airtable and create for next time
        else:
            _log.info(f"Fetching data from airtable (cache)")
            tables = IdaesplusAirtable(get_token(args.token)).get_tables()
            _log.info(f"Writing airtable data to cache file '{p}'")
            with p.open("w") as f:
                json.dump(tables, f)
    else:
        _log.info("Fetching data from airtable")
        tables = IdaesplusAirtable(get_token(args.token)).get_tables()

    _log.info(f"Writing YAML file {output_path}")
    report = IdaesplusAirtable.dump_tables(output_path, tables)

    for table_name, data in report.items():
        print(f"Wrote {data['records']} records for table {table_name}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as err:
        _log.fatal(err)
        sys.exit(-1)
