"""
Download tables from Airtable (or cache) and output YAML file.
"""

import argparse
import json
import logging
import os
from pathlib import Path
import requests
import sys
import traceback
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
    table_names = ("projects", "products", "models", "ui_products")
    screenshots = None
    sshot_path = Path(__file__).parent / "screenshots.yaml"

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
                pp_data = cls.postprocess(table_name, norm_fields)
                if pp_data is None:
                    _log.warning("Skip empty record")
                else:
                    r.update(pp_data)
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
                "description",
                "flowsheet_module",
                "unit_models",
                "property_package",
                "reaction_package",
            ):
                if req_field not in fields:
                    fields[req_field] = ""
            # break long descriptions into 2 fields
            desc = fields["description"]
            if len(desc) > 85:
                fields["description"] = desc[:80] + "..."
                fields["full_description"] = desc
            if "configurations" in fields:
                fields["configurations"] = ", ".join(
                    fields["configurations"].split("\n")
                )
            # put sub-packages and links for unit models, etc.
            # into '<type>_data' dict for easy processing later
            gh = "https://github.com/"
            repo_roots = {
                "watertap": f"{gh}watertap-org/watertap/tree/main",
                "prommis": f"{gh}prommis/prommis/tree/main/src",
                "idaes": f"{gh}idaes/idaes-pse/tree/main",
            }
            for k in (
                "unit_model",
                "reaction_package",
                "control_volume",
                "property_package",
            ):
                names, repos = f"{k}s", f"{k}_repositories"
                if names not in fields:
                    continue
                if repos not in fields:
                    raise KeyError(
                        f"Found {names} but missing {repos} in {fields['name']}"
                    )
                name_list = [s.strip() for s in fields[names].split(";")]
                repo_list = [s.strip() for s in fields[repos].split(";")]
                url_list = []
                for r in repo_list:
                    proj = r.split("/")[0]
                    try:
                        url_list.append(repo_roots[proj] + "/" + r)
                    except KeyError:
                        raise KeyError(
                            f"Bad project name '{proj}' for '{fields['name']}' in {k}"
                        )
                if len(url_list) != len(name_list):
                    raise ValueError(
                        f"Name/repo list mismatch for {k} in {fields['name']}: {len(name_list)} names != {len(url_list)} urls"
                    )
                # create dict combining the information
                fields[f"{k}_data"] = {
                    name: url_list[i] for i, name in enumerate(name_list)
                }
        elif table_name == "ui_products":
            # check if empty
            if "name" not in fields:
                return None
            # fill in blank values for certain required fields
            for req_field in (
                "description",
                "features",
            ):
                if req_field not in fields:
                    fields[req_field] = ""
            # delete dumb fields
            del fields["attachment_summary"]
            # make list out of features
            fields["features"] = [s.strip() for s in fields["features"].split(";")]
            # add screenshot info
            fields["screenshots"] = cls.ui_screenshots(fields["name"])
            # build combined 'links' dict
            fields["links"] = {
                "gh": fields.get("repository", ""),
                "docs": fields.get("documentation", ""),
                # add name of this product if there are screenshots
                "screenshots": fields["name"] if fields["screenshots"] else "",
            }
        return fields

    @classmethod
    def ui_screenshots(cls, name: str) -> dict:
        """Get screenshot info from local file."""
        # load once
        if cls.screenshots is None:
            with open(cls.sshot_path) as f:
                data = yaml.safe_load(f)
            # make UI names lowercase for easier matching
            cls.screenshots = {k.lower(): v for k, v in data.items()}
        # look for data matching UI product name
        try:
            sshot = cls.screenshots[name.lower()]
        except KeyError:
            _log.warning(
                f"No screenshots found for UI product '{name}' in file '{cls.sshot_path}'"
            )
            sshot = {}
        return sshot

    def _split_fields(f, key):
        return


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
        help="Use cached JSON data in FILE. "
        "If the file does not exist it will be created.",
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
        if _log.isEnabledFor(logging.INFO):
            traceback.print_exc()
        sys.exit(-1)
