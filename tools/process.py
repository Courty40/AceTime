#!/usr/bin/env python3
#
# Copyright 2018 Brian T. Park
#
# MIT License.
"""
Main driver for the Extractor, Printer, Transformer, and Generator.
"""

import argparse
import logging
import sys

from printer import Printer
from extractor import Extractor
from transformer import Transformer
from generator import Generator

def main():
    """Read the test data chunks from the STDIN and print them out. The ability
    to run this from the command line is intended mostly for testing purposes.

    Usage:
        process.py [flags...]
    """
    # Configure command line flags.
    parser = argparse.ArgumentParser(description='Generate Zone Info.')

    # Extractor
    parser.add_argument(
        '--input_dir', help='Location of the input directory', required=True)
    parser.add_argument(
        '--print_summary',
        help='Print summary of rules and zones',
        action="store_true",
        default=False)

    # Transformer
    parser.add_argument(
        '--print_removed',
        help='Print names of removed zones and policies',
        action="store_true",
        default=True)

    # Printer
    parser.add_argument(
        '--print_rules',
        help='Print list of rules',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_rules_historical',
        help='Print rules which start and end before year 2000',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_rules_long_dst_letter',
        help='Print rules with long DST letter',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones',
        help='Print list of zones',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_short_name',
        help='Print the short zone names',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_with_until_month',
        help='Print the Zones with "UNTIL" month fields',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_with_offset_as_rules',
        help='Print rules which contains a DST offset in the RULES column',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_without_rules',
        help='Print rules which contain "-" in the RULES column',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_with_unknown_rules',
        help='Print rules which contain a valid RULES that cannot be found',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_zones_requiring_historic_rules',
        help='Print rules which require historic transition rules',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_transformed_zones',
        help='Print transformed zones',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_transformed_rules',
        help='Print transformed rules',
        action="store_true",
        default=False)

    # Generator
    parser.add_argument(
        '--tz_version', help='Version string of the TZ files', required=True)
    parser.add_argument(
        '--output_dir', help='Location of the output directory', required=False)
    parser.add_argument(
        '--print_generated_policies',
        help='Print generated zone_policies.h and zone_policies.cpp',
        action="store_true",
        default=False)
    parser.add_argument(
        '--print_generated_infos',
        help='Print generated zone_infos.h and zone_infos.cpp',
        action="store_true",
        default=False)

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # How the script was invoked
    invocation = " ".join(sys.argv)

    # Extract the TZ files
    extractor = Extractor(args.input_dir)
    extractor.parse_zone_files()
    extractor.process_rules()
    extractor.process_zones()
    (zones, rules) = extractor.get_data()

    # Extractor summary
    if args.print_summary:
        extractor.print_summary()

    # Transform the TZ zones and rules
    transformer = Transformer(zones, rules, args.print_removed)
    transformer.transform()
    (zones, rules) = transformer.get_data()

    # create the generator
    generator = Generator(invocation, args.tz_version, zones, rules)

    # Print various slices of the data
    printer = Printer(zones, rules)
    # rules
    if args.print_rules:
        printer.print_rules()
    if args.print_rules_historical:
        printer.print_rules_historical()
    if args.print_rules_long_dst_letter:
        printer.print_rules_long_dst_letter()
    # zones
    if args.print_zones:
        printer.print_zones()
    if args.print_zones_short_name:
        printer.print_zones_short_name()
    if args.print_zones_with_until_month:
        printer.print_zones_with_until_month()
    if args.print_zones_with_offset_as_rules:
        printer.print_zones_with_offset_as_rules()
    if args.print_zones_without_rules:
        printer.print_zones_without_rules()
    if args.print_zones_with_unknown_rules:
        printer.print_zones_with_unknown_rules()
    if args.print_zones_with_unknown_rules:
        printer.print_zones_with_unknown_rules()
    if args.print_zones_requiring_historic_rules:
        printer.print_zones_requiring_historic_rules()

    # printer for the transformer
    (zones, rules) = transformer.get_data()
    printer = Printer(zones, rules)

    # print the transformed data
    if args.print_transformed_zones:
        printer.print_zones()
    if args.print_transformed_rules:
        printer.print_rules()

    # print the generated zone_policies.*
    if args.print_generated_policies:
        generator.print_generated_policies()

    # print the generated zone_infos.*
    if args.print_generated_infos:
        generator.print_generated_infos()

    # generate files
    if args.output_dir:
        generator.generate_files(args.output_dir)

if __name__ == '__main__':
    main()
