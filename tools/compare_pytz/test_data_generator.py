#!/usr/bin/env python3
#
# Copyright 2020 Brian T. Park
#
# MIT License
#
# Generate the validation_data.{h,cpp} and validation_test.cpp files
# given the 'zones.txt' file from the tzcompiler.py.
#
# Usage
# $ ./test_data_generator.py \
#   --scope (basic | extended) \
#   --tz_version {version}
#   [--db_namespace {db}] \
#   [--start_year start] \
#   [--until_year until] < zones.txt
#

import sys
import logging
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import List

from tdgenerator import TestDataGenerator
from arvalgenerator import ArduinoValidationGenerator


def main(
    invocation: str,
    scope: str,
    db_namespace: str,
    tz_version: str,
    start_year: int,
    until_year: int,
    output_dir: str,
) -> None:
    zones = read_zones()

    generator = TestDataGenerator(start_year, until_year)
    test_data = generator.create_test_data(zones)
    
    arval_generator = ArduinoValidationGenerator(
        invocation, tz_version, db_namespace, scope, test_data)
    arval_generator.generate_files(output_dir)


def read_zones() -> List[str]:
    """Read the list of zone_names from the sys.stdin."""
    zones: List[str] = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        zones.append(line)
    return zones


if __name__ == '__main__':
    parser = ArgumentParser(description='Generate Test Data.')

    # Scope (of the zones in the database):
    # basic: 241 of the simpler time zones for BasicZoneSpecifier
    # extended: all 348 time zones for ExtendedZoneSpecifier
    parser.add_argument(
        '--scope',
        help='Size of the generated database (basic|extended)',
        required=True)

    # C++ namespace names for language=arduino. If not specified, it will
    # automatically be set to 'zonedb' or 'zonedbx' depending on the 'scope'.
    parser.add_argument(
        '--db_namespace',
        help='C++ namespace for the zonedb files (default: zonedb or zonedbx)')

    # Options for file generators
    parser.add_argument(
        '--tz_version', help='Version string of the TZ files', required=True)

    parser.add_argument(
        '--start_year',
        help='Start year of validation (default: start_year)',
        type=int,
        default=2000)
    parser.add_argument(
        '--until_year',
        help='Until year of validation (default: 2038)',
        type=int,
        default=2038)

    parser.add_argument(
        '--output_dir',
        help='Location of the output directory',
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    invocation = ' '.join(sys.argv)

    main(
        invocation,
        args.scope,
        args.db_namespace,
        args.tz_version,
        int(args.start_year),
        int(args.until_year),
        args.output_dir,
    )
