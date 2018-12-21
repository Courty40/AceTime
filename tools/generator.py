# Copyright 2018 Brian T. Park
#
# MIT License
"""
Generate the zone_info and zone_policies files.
"""

import logging
import os

from transformer import short_name

class Generator:
    ZONE_POLICIES_H_FILE = """\
// This file was generated by the following script:
//
//  $ {invocation}
//
// using the TZ Database files
//
//  {tz_files}
//
// from https://github.com/eggert/tz/releases/tag/{tz_version}
//
// DO NOT EDIT

#ifndef ACE_TIME_ZONE_POLICIES_H
#define ACE_TIME_ZONE_POLICIES_H

#include "../common/ZonePolicy.h"

namespace ace_time {{
namespace zonedb {{

// numPolicies: {numPolicies}
{policyItems}

}}
}}

#endif
"""

    ZONE_POLICIES_H_POLICY_ITEM = """\
extern const common::ZonePolicy kPolicy{policyName};
"""

    ZONE_POLICIES_CPP_FILE = """\
// This file was generated by the following script:
//
//   $ {invocation}
//
// using the TZ Database files from
//  https://github.com/eggert/tz/releases/tag/{tz_version}
//
// Policy count: {numPolicies}
// Rule count: {numRules}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//
// DO NOT EDIT

#include "zone_policies.h"

namespace ace_time {{
namespace zonedb {{

{policyItems}

}}
}}
"""

    ZONE_POLICIES_CPP_POLICY_ITEM = """\
//---------------------------------------------------------------------------
// Policy name: {policyName}
// Rule count: {numRules}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//---------------------------------------------------------------------------

static const common::ZoneRule kZoneRules{policyName}[] = {{
{ruleItems}
}};

const common::ZonePolicy kPolicy{policyName} = {{
  sizeof(kZoneRules{policyName})/sizeof(common::ZoneRule) /*numRules*/,
  kZoneRules{policyName} /*rules*/,
}};

"""

    ZONE_POLICIES_CPP_RULE_ITEM = """\
  // {rawLine}
  {{
    {fromYearFull} /*fromYearFull*/,
    {toYearFull} /*toYearFull*/,
    {inMonth} /*inMonth*/,
    {onDayOfWeek} /*onDayOfWeek*/,
    {onDayOfMonth} /*onDayOfMonth*/,
    {atHour} /*atHour*/,
    '{atHourModifier}' /*atHourModifier*/,
    {deltaCode} /*deltaCode*/,
    '{letter}' /*letter*/,
  }},
"""

    ZONE_INFOS_H_FILE = """\
// This file was generated by the following script:
//
//  $ {invocation}
//
// using the TZ Database files
//
//  {tz_files}
//
// from https://github.com/eggert/tz/releases/tag/{tz_version}
//
// DO NOT EDIT

#ifndef ACE_TIME_ZONE_INFOS_H
#define ACE_TIME_ZONE_INFOS_H

#include "../common/ZoneInfo.h"

#define ACE_TIME_TZ_DATABASE_VERSION "{tz_version}"

namespace ace_time {{
namespace zonedb {{

// numInfos: {numInfos}
{infoItems}

// The following zones are not supported in the current version of AceTime.
// numInfos: {numRemovedInfos}

{removedInfoItems}

}}
}}

#endif
"""

    ZONE_INFOS_H_INFO_ITEM = """\
extern const common::ZoneInfo kZone{infoShortName}; // {infoFullName}
"""

    ZONE_INFOS_H_REMOVED_INFO_ITEM = """\
// {infoFullName}
"""

    ZONE_INFOS_CPP_FILE = """\
// This file was generated by the following script:
//
//   $ {invocation}
//
// using the TZ Database files from
// https://github.com/eggert/tz/releases/tag/{tz_version}
//
// Zone info count: {numInfos}
// Zone entry count: {numEntries}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//
// DO NOT EDIT

#include "../common/ZoneInfo.h"
#include "zone_policies.h"
#include "zone_infos.h"

namespace ace_time {{
namespace zonedb {{

{infoItems}

}}
}}
"""

    ZONE_INFOS_CPP_INFO_ITEM = """\
//---------------------------------------------------------------------------
// Zone name: {infoFullName}
// Entry count: {numEntries}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//---------------------------------------------------------------------------

static const common::ZoneEntry kZoneEntry{infoShortName}[] = {{
{entryItems}
}};

const common::ZoneInfo kZone{infoShortName} = {{
  "{infoFullName}" /*name*/,
  kZoneEntry{infoShortName} /*entries*/,
  sizeof(kZoneEntry{infoShortName})/sizeof(common::ZoneEntry) /*numEntries*/,
}};

"""

    ZONE_INFOS_CPP_ENTRY_ITEM = """\
  // {rawLine}
  {{
    {offsetCode} /*offsetCode*/,
    {zonePolicy} /*zonePolicy*/,
    "{format}" /*format*/,
    {untilYearShort} /*untilYearShort*/,
  }},
"""

    ZONE_INFOS_H_FILE_NAME = 'zone_infos.h'
    ZONE_INFOS_CPP_FILE_NAME = 'zone_infos.cpp'
    ZONE_POLICIES_H_FILE_NAME = 'zone_policies.h'
    ZONE_POLICIES_CPP_FILE_NAME = 'zone_policies.cpp'

    ZONE_INFO_EPOCH_YEAR = 2000
    YEAR_SHORT_MAX = 127
    YEAR_MAX = 9999

    SIZEOF_ZONE_ENTRY_8 = 6
    SIZEOF_ZONE_ENTRY_32 = 10
    SIZEOF_ZONE_INFO_8 = 5
    SIZEOF_ZONE_INFO_32 = 9
    SIZEOF_ZONE_RULE_8 = 11
    SIZEOF_ZONE_RULE_32 = 11
    SIZEOF_ZONE_POLICY_8 = 3
    SIZEOF_ZONE_POLICY_32 = 5

    def __init__(self, invocation, tz_version, tz_files,
                 zones, rules, removed_zones):
        self.invocation = invocation
        self.tz_version = tz_version
        self.tz_files = tz_files
        self.zones = zones
        self.rules = rules
        self.removed_zones = removed_zones

    def print_generated_policies(self):
        print(self.generate_policies_h())
        print(self.generate_policies_cpp())

    def print_generated_infos(self):
        print(self.generate_infos_h())
        print(self.generate_infos_cpp())

    def generate_files(self, output_dir):
        self.write_file(output_dir,
            self.ZONE_POLICIES_H_FILE_NAME, self.generate_policies_h())
        self.write_file(output_dir,
            self.ZONE_POLICIES_CPP_FILE_NAME, self.generate_policies_cpp())

        self.write_file(output_dir,
            self.ZONE_INFOS_H_FILE_NAME, self.generate_infos_h())
        self.write_file(output_dir,
            self.ZONE_INFOS_CPP_FILE_NAME, self.generate_infos_cpp())

    def write_file(self, output_dir, filename, content):
        full_filename = os.path.join(output_dir, filename)
        with open(full_filename, 'w', encoding='utf-8') as output_file:
            print(content, end='', file=output_file)
        logging.info("Created %s", full_filename)

    def generate_policies_h(self):
        policy_items = ''
        for name, rules in sorted(self.rules.items()):
            policy_items += self.ZONE_POLICIES_H_POLICY_ITEM.format(
                policyName=normalize_name(name))

        return self.ZONE_POLICIES_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            tz_files=', '.join(self.tz_files),
            numPolicies=len(self.rules),
            policyItems=policy_items)

    def generate_policies_cpp(self):
        policy_items = ''
        num_rules = 0
        for name, rules in sorted(self.rules.items()):
            policy_items += self.generate_policy_item(name, rules)
            num_rules += len(rules)

        num_policies = len(self.rules)
        memory8 = (num_policies * self.SIZEOF_ZONE_POLICY_8 +
            num_rules * self.SIZEOF_ZONE_RULE_8)
        memory32 = (num_policies * self.SIZEOF_ZONE_POLICY_32 +
            num_rules * self.SIZEOF_ZONE_RULE_32)

        return self.ZONE_POLICIES_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            numPolicies=num_policies,
            numRules=num_rules,
            memory8=memory8,
            memory32=memory32,
            policyItems=policy_items
        )

    def generate_policy_item(self, name, rules):
        rule_items = ''
        for rule in rules:
            atHour = rule['atMinute'] // 60
            rule_items += self.ZONE_POLICIES_CPP_RULE_ITEM.format(
                rawLine=normalize_raw(rule['rawLine']),
                fromYearFull=rule['fromYear'],
                toYearFull=rule['toYear'],
                inMonth=rule['inMonth'],
                onDayOfWeek=rule['onDayOfWeek'],
                onDayOfMonth=rule['onDayOfMonth'],
                atHour=atHour,
                atHourModifier=rule['atHourModifier'],
                deltaCode=rule['deltaCode'],
                letter=rule['letter'])

        num_rules = len(rules)
        memory8 = (1 * self.SIZEOF_ZONE_POLICY_8 +
            num_rules * self.SIZEOF_ZONE_RULE_8)
        memory32 = (1 * self.SIZEOF_ZONE_POLICY_32 +
            num_rules * self.SIZEOF_ZONE_RULE_32)

        return self.ZONE_POLICIES_CPP_POLICY_ITEM.format(
            policyName=normalize_name(name),
            numRules=num_rules,
            memory8=memory8,
            memory32=memory32,
            ruleItems=rule_items)

    def generate_infos_h(self):
        info_items = ''
        for name, zones in sorted(self.zones.items()):
            info_items += self.ZONE_INFOS_H_INFO_ITEM.format(
                infoShortName=normalize_name(short_name(name)),
                infoFullName=name)

        removed_info_items = ''
        for name in sorted(self.removed_zones):
            removed_info_items += self.ZONE_INFOS_H_REMOVED_INFO_ITEM.format(
                infoFullName=name)

        return self.ZONE_INFOS_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            tz_files=', '.join(self.tz_files),
            numInfos=len(self.zones),
            infoItems=info_items,
            numRemovedInfos=len(self.removed_zones),
            removedInfoItems=removed_info_items)

    def generate_infos_cpp(self):
        info_items = ''
        num_entries = 0
        string_length = 0
        for name, entries in sorted(self.zones.items()):
            (info_item, format_length) = self.generate_entry_item(name, entries)
            info_items += info_item
            string_length += format_length
            num_entries += len(entries)

        num_infos = len(self.zones)
        memory8 = (string_length + num_entries * self.SIZEOF_ZONE_ENTRY_8 +
            num_infos * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_entries * self.SIZEOF_ZONE_ENTRY_32 +
            num_infos *self.SIZEOF_ZONE_INFO_32)

        return self.ZONE_INFOS_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            numInfos=num_infos,
            numEntries=num_entries,
            memory8=memory8,
            memory32=memory32,
            infoItems=info_items)

    def generate_entry_item(self, name, entries):
        entry_items = ''
        string_length = 0
        for entry in entries:
            rules = entry['rules']
            if rules == '-':
                zonePolicy = 'nullptr'
            else:
                zonePolicy = '&kPolicy%s' % rules

            until_year = entry['untilYear']
            if until_year == self.YEAR_MAX:
                until_year_short = self.YEAR_SHORT_MAX
            else:
                until_year_short = until_year - self.ZONE_INFO_EPOCH_YEAR

            string_length += len(entry['format']) + 1

            entry_items += self.ZONE_INFOS_CPP_ENTRY_ITEM.format(
                rawLine=normalize_raw(entry['rawLine']),
                offsetCode=entry['offsetCode'],
                zonePolicy=zonePolicy,
                format=entry['format'],
                untilYearShort=until_year_short)

        string_length += len(name) + 1
        num_entries = len(entries)
        memory8 = (string_length + num_entries * self.SIZEOF_ZONE_ENTRY_8 +
            1 * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_entries * self.SIZEOF_ZONE_ENTRY_32 +
            1 *self.SIZEOF_ZONE_INFO_32)

        info_item = self.ZONE_INFOS_CPP_INFO_ITEM.format(
            infoFullName=normalize_name(name),
            infoShortName=normalize_name(short_name(name)),
            numEntries=num_entries,
            memory8=memory8,
            memory32=memory32,
            entryItems=entry_items)
        return (info_item, string_length)

def normalize_name(name):
    """Replace hyphen with underscore so that the C++ symbol can compile.
    """
    return name.replace('-', '_')

def normalize_raw(raw_line):
    """Replace hard tabs with 4 spaces.
    """
    return raw_line.replace('\t', '    ')
