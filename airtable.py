"""
Download tables from Airtable and output YAML
"""
import argparse
import logging
import os
from pathlib import Path
import requests
import sys
import yaml

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
        self.tables = {}
        for table_name in self.table_names:
            url = f"{self.url}/{self.baseid}/{table_name}"
            _log.debug(f"Begin:Request url={url}")
            d = requests.get(url, headers={"Authorization": f"Bearer {tok}"})
            _log.debug(f"End:Request url={url} ; status={d.status_code}")
            if d.status_code != 200:
                if d.status_code == 401:
                    raise RuntimeError(f"Unauthorized. Check your API key")
                else:
                    raise RuntimeError(f"Fetching '{url}': HTTP status {d.status_code}")
            self.tables[table_name] = d.json()["records"]

    def dump(self, path):
        report = {}
        y = {}
        for table_name, table_contents in self.tables.items():
            y[table_name] = []
            for record in table_contents:
                r = {"id": record["id"]}
                r.update(record["fields"])
                y[table_name].append(r)
            report[table_name] = {"records": len(y[table_name])}
        with path.open("w") as f:
            yaml.dump(y, stream=f)
        return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("output_file", metavar="PATH", help="YAML output file")
    p.add_argument("-t", "--token", help=f"API token, otherwise look in {TOKENV}")
    p.add_argument("-v", "--verbose", action="count", default=0, help="Increase log verbosity")
    args = p.parse_args()

    if args.verbose > 1:
        _log.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        _log.setLevel(logging.INFO)
    else:
        _log.setLevel(logging.WARNING)

    output_path = Path(args.output_file)
    if not output_path.parent.exists():
        _log.fatal(f"Output directory '{output_path.parent}' not found. "
                   f"Please create it or provide a different path.")
        return 1

    if args.token:
        tok = args.token
    else:
        try:
            tok = os.environ[TOKENV]
        except KeyError:
            print(f"Please provide the token via the -t/--token option "
                  f"or setting the environment variable {TOKENV}")
            return 1


    _log.info("Fetching data from airtable")
    at = IdaesplusAirtable(tok)

    _log.info(f"Writing YAML file {output_path}")
    report = at.dump(output_path)

    for table_name, data in report.items():
        print(f"Wrote {data['records']} records for table {table_name}")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as err:
        _log.fatal(err)
        sys.exit(-1)

