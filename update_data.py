"""
Download tables from Airtable (or cache) and output YAML file.
"""

import argparse
import csv
import json
import logging
import os
from pathlib import Path
import re
import sys
import traceback
from typing import Any
import yaml

# third-party packages
from markdown import markdown

__author__ = "Dan Gunter (LBNL)"

_log = logging.getLogger("idaes_plus")
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(levelname)s %(name)s %(asctime)s - %(message)s"))
_log.addHandler(_h)


class IdaesplusTables:
    table_names = ("products", "models", "ui_products")
    screenshots = None
    sshot_path = Path(__file__).parent / "screenshots.yaml"
    data_path = Path(__file__).parent / "data"

    def __init__(self, continue_on_error: bool = False):
        self._tables, self._report = {}, {}
        self._soldier_on = continue_on_error
        self._build_tables()

    @property
    def report(self):
        return self._report

    def _build_tables(self):
        for table_name in self.table_names:
            csv_file = self.data_path / f"{table_name}.csv"
            cur_table = []
            with csv_file.open("r") as f:
                csv_table = csv.reader(f)
                norm_header = None
                for i, row in enumerate(csv_table):
                    if norm_header is None:
                        norm_header = [
                            # not sure why \ufeff is appearing but whatevs
                            key.lower().replace(" ", "_").replace("\ufeff", "")
                            for key in row
                        ]
                        continue
                    fields = {norm_header[i]: row[i] for i in range(len(row))}
                    try:
                        getattr(self, f"_post_{table_name}")(table_name, fields)
                    except:
                        _log.error(
                            f"Postprocessing error in line {i + 1} of {csv_file}"
                        )
                        raise
                    cur_table.append(fields)
            self._tables[table_name] = cur_table
            self._report[table_name] = {"records": len(cur_table)}

    def dump(self, path: Path):
        """Dump to YAML file."""
        with path.open("w") as f:
            yaml.dump(self._tables, stream=f)

    def _post_projects(self, table_name: str, fields: dict[str, Any]):
        fields["active"] = bool(fields["development"].lower() == "active")

    def _post_products(self, table_name: str, fields: dict[str, Any]):
        # move 'code' fields into a nested dict
        fields["code"] = {}
        for code_field in ("github", "pypi", "conda-forge"):
            if code_field in fields:
                fields["code"][code_field] = fields[code_field]
                del fields[code_field]

    def _post_models(self, table_name: str, fields: dict[str, Any]):
        cur_name = fields["name"]
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
            fields["configurations"] = ", ".join(fields["configurations"].split("\n"))
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
            if not fields[names].strip():
                continue  # empty
            if repos not in fields:
                raise KeyError(f"Found {names} but missing {repos} in {fields}")
            name_list = self._split_list(fields[names])
            repo_list = self._split_list(fields[repos])
            url_list = []
            for r in repo_list:
                proj = r.split("/")[0]
                try:
                    url_list.append(repo_roots[proj] + "/" + r)
                except KeyError:
                    raise KeyError(
                        f"Models: Bad project name '{proj}' for '{fields}' in {cur_name}::{k}"
                    )
            if len(url_list) != len(name_list):
                if len(url_list) == 1 and len(name_list) > 1:
                    # if one url, use for all
                    url_list = url_list + [url_list[0]] * (len(name_list) - 1)
                else:
                    msg = (
                        f"Name/repo list mismatch for {cur_name}::{k}: {len(name_list)} names != {len(url_list)} urls.\n" 
                        f"  names: {name_list}\n  urls: {url_list}"
                    )
                    if self._soldier_on:
                        shorter = min(len(url_list), len(name_list))
                        url_list = url_list[:shorter]
                        name_list = name_list[:shorter]
                        _log.warning(msg)
                    else:
                        raise ValueError(msg)
            # create dict combining the information
            fields[f"{k}_data"] = {
                name: url_list[i] for i, name in enumerate(name_list)
            }

    def _post_ui_products(self, table_name: str, fields: dict[str, Any]):
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
        fields["features"] = [
            s.strip().replace("\n", " ") for s in fields["features"].split(";")
        ]
        # make list out of model compatibility
        fields["modelcompatibility"] = [
            x.strip() for x in fields["modelcompatibility"].split(",")
        ]
        # add screenshot info
        fields["screenshots"] = self.ui_screenshots(fields["name"])
        # build combined 'links' dict
        fields["links"] = {
            "gh": fields.get("repository", ""),
            "docs": fields.get("documentation", ""),
            # add name of this product if there are screenshots
            "screenshots": fields["name"] if fields["screenshots"] else "",
        }

    def ui_screenshots(self, name: str) -> dict:
        """Get screenshot info from local file."""
        # load once
        if self.screenshots is None:
            with open(self.sshot_path) as f:
                data = yaml.safe_load(f)
            # make UI names lowercase for easier matching
            self.screenshots = {k.lower(): v for k, v in data.items()}
        # look for data matching UI product name
        try:
            sshot = self.screenshots[name.lower()]
        except KeyError:
            _log.warning(
                f"No screenshots found for UI product '{name}' in file '{self.sshot_path}'"
            )
            sshot = {}
        return sshot

    @staticmethod
    def _split_list(s):
        items = []
        # split and clean up
        for x in re.split(r";|,", s):
            items.append(x.strip().replace("\n", " ").replace("  ", " "))
        return items


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output_file", metavar="OUTPUT_FILE", help="YAML output file")
    p.add_argument(
        "-E",
        "--ignore-errors",
        action="store_true",
        help="Ignore errors in input, continue anyways (but log them)",
    )
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

    tables = IdaesplusTables(continue_on_error=args.ignore_errors)
    tables.dump(output_path)
    for table_name, data in tables.report.items():
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
