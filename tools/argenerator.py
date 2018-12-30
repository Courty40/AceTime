# Copyright 2018 Brian T. Park
#
# MIT License
"""
Generate the zone_info and zone_policies files for Arduino.
"""

import logging
import os

from transformer import short_name

class ArduinoGenerator:
    """Generate Arduino/C++ files for zone infos and policies.
    """

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

// The following zone policies are not supported in the current version of
// AceTime.
//
// numPolicies: {numRemovedPolicies}
//
{removedPolicyItems}

}}
}}

#endif
"""

    ZONE_POLICIES_H_POLICY_ITEM = """\
extern const common::ZonePolicy kPolicy{policyName};
"""

    ZONE_POLICIES_H_REMOVED_POLICY_ITEM = """\
// kPolicy{policyName} ({policyRemovalReason})
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
    {fromYearShort} /*fromYearShort*/,
    {toYearShort} /*toYearShort*/,
    {inMonth} /*inMonth*/,
    {onDayOfWeek} /*onDayOfWeek*/,
    {onDayOfMonth} /*onDayOfMonth*/,
    {atHour} /*atHour*/,
    '{atTimeModifier}' /*atTimeModifier*/,
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
//
// numInfos: {numRemovedInfos}
//
{removedInfoItems}

}}
}}

#endif
"""

    ZONE_INFOS_H_INFO_ITEM = """\
extern const common::ZoneInfo kZone{infoShortName}; // {infoFullName}
"""

    ZONE_INFOS_H_REMOVED_INFO_ITEM = """\
// {infoFullName} ({infoRemovalReason})
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
// Zone era count: {numEras}
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
// Era count: {numEras}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//---------------------------------------------------------------------------

static const common::ZoneEra kZoneEra{infoShortName}[] = {{
{eraItems}
}};

const common::ZoneInfo kZone{infoShortName} = {{
  "{infoFullName}" /*name*/,
  kZoneEra{infoShortName} /*eras*/,
  sizeof(kZoneEra{infoShortName})/sizeof(common::ZoneEra) /*numEras*/,
}};

"""

    ZONE_INFOS_CPP_ERA_ITEM = """\
  // {rawLine}
  {{
    {offsetCode} /*offsetCode*/,
    {zonePolicy} /*zonePolicy*/,
    "{format}" /*format*/,
    {untilYearShort} /*untilYearShort*/,
    {untilMonth} /*untilMonth*/,
    {untilDay} /*untilDay*/,
    {untilHour} /*untilHour*/,
    '{untilTimeModifier}' /*untilTimeModifier*/,
  }},
"""

    ZONE_INFOS_H_FILE_NAME = 'zone_infos.h'
    ZONE_INFOS_CPP_FILE_NAME = 'zone_infos.cpp'
    ZONE_POLICIES_H_FILE_NAME = 'zone_policies.h'
    ZONE_POLICIES_CPP_FILE_NAME = 'zone_policies.cpp'

    EPOCH_YEAR = 2000
    MAX_YEAR_SHORT = 127
    MAX_YEAR = 9999

    SIZEOF_ZONE_ERA_8 = 6
    SIZEOF_ZONE_ERA_32 = 10
    SIZEOF_ZONE_INFO_8 = 5
    SIZEOF_ZONE_INFO_32 = 9
    SIZEOF_ZONE_RULE_8 = 9
    SIZEOF_ZONE_RULE_32 = 9
    SIZEOF_ZONE_POLICY_8 = 3
    SIZEOF_ZONE_POLICY_32 = 5

    def __init__(self, invocation, tz_version, tz_files,
                 zones_map, rules_map, removed_zones, removed_policies):
        self.invocation = invocation
        self.tz_version = tz_version
        self.tz_files = tz_files
        self.zones_map = zones_map
        self.rules_map = rules_map
        self.removed_zones = removed_zones
        self.removed_policies = removed_policies

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
        for name, rules in sorted(self.rules_map.items()):
            policy_items += self.ZONE_POLICIES_H_POLICY_ITEM.format(
                policyName=normalize_name(name))

        removed_policy_items = ''
        for name, reason in sorted(self.removed_policies.items()):
            removed_policy_items += \
                self.ZONE_POLICIES_H_REMOVED_POLICY_ITEM.format(
                    policyName=name,
                    policyRemovalReason=reason)

        return self.ZONE_POLICIES_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            tz_files=', '.join(self.tz_files),
            numPolicies=len(self.rules_map),
            policyItems=policy_items,
            numRemovedPolicies=len(self.removed_policies),
            removedPolicyItems=removed_policy_items)

    def generate_policies_cpp(self):
        policy_items = ''
        num_rules = 0
        for name, rules in sorted(self.rules_map.items()):
            policy_items += self.generate_policy_item(name, rules)
            num_rules += len(rules)

        num_policies = len(self.rules_map)
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
            atHour = rule['atHour']

            from_year = rule['fromYear']
            from_year_short = (from_year - self.EPOCH_YEAR
                if from_year != self.MAX_YEAR
                else self.MAX_YEAR_SHORT)

            to_year = rule['toYear']
            to_year_short = (to_year - self.EPOCH_YEAR
                if to_year != self.MAX_YEAR
                else self.MAX_YEAR_SHORT)

            rule_items += self.ZONE_POLICIES_CPP_RULE_ITEM.format(
                rawLine=normalize_raw(rule['rawLine']),
                fromYearShort=from_year_short,
                toYearShort=to_year_short,
                inMonth=rule['inMonth'],
                onDayOfWeek=rule['onDayOfWeek'],
                onDayOfMonth=rule['onDayOfMonth'],
                atHour=atHour,
                atTimeModifier=rule['atTimeModifier'],
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
        for name, zones in sorted(self.zones_map.items()):
            info_items += self.ZONE_INFOS_H_INFO_ITEM.format(
                infoShortName=normalize_name(short_name(name)),
                infoFullName=name)

        removed_info_items = ''
        for name, reason in sorted(self.removed_zones.items()):
            removed_info_items += self.ZONE_INFOS_H_REMOVED_INFO_ITEM.format(
                infoFullName=name,
                infoRemovalReason=reason)

        return self.ZONE_INFOS_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            tz_files=', '.join(self.tz_files),
            numInfos=len(self.zones_map),
            infoItems=info_items,
            numRemovedInfos=len(self.removed_zones),
            removedInfoItems=removed_info_items)

    def generate_infos_cpp(self):
        info_items = ''
        num_eras = 0
        string_length = 0
        for name, eras in sorted(self.zones_map.items()):
            (info_item, format_length) = self.generate_info_item(name, eras)
            info_items += info_item
            string_length += format_length
            num_eras += len(eras)

        num_infos = len(self.zones_map)
        memory8 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_8 +
            num_infos * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_32 +
            num_infos *self.SIZEOF_ZONE_INFO_32)

        return self.ZONE_INFOS_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            numInfos=num_infos,
            numEras=num_eras,
            memory8=memory8,
            memory32=memory32,
            infoItems=info_items)

    def generate_info_item(self, name, eras):
        era_items = ''
        string_length = 0
        for era in eras:
            (era_item, length) = self.generate_era_item(name, era)
            era_items += era_item
            string_length += length

        string_length += len(name) + 1
        num_eras = len(eras)
        memory8 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_8 +
            1 * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_32 +
            1 *self.SIZEOF_ZONE_INFO_32)

        info_item = self.ZONE_INFOS_CPP_INFO_ITEM.format(
            infoFullName=normalize_name(name),
            infoShortName=normalize_name(short_name(name)),
            numEras=num_eras,
            memory8=memory8,
            memory32=memory32,
            eraItems=era_items)
        return (info_item, string_length)

    def generate_era_item(self, name, era):
        policy_name = era['rules']
        if policy_name == '-':
            zonePolicy = 'nullptr'
        else:
            zonePolicy = '&kPolicy%s' % normalize_name(policy_name)

        until_year = era['untilYear']
        if until_year == self.MAX_YEAR:
            until_year_short = self.MAX_YEAR_SHORT
        else:
            until_year_short = until_year - self.EPOCH_YEAR

        until_month = era['untilMonth']
        if not until_month:
            until_month = 1

        until_day = era['untilDay']
        if not until_day:
            until_day = 1

        until_hour = era['untilHour']
        if not until_hour:
            until_hour = 0

        until_time_modifier = era['untilTimeModifier']

        # Replace %s with just a % for C++
        format = era['format'].replace('%s', '%')
        string_length = len(format) + 1

        era_item = self.ZONE_INFOS_CPP_ERA_ITEM.format(
            rawLine=normalize_raw(era['rawLine']),
            offsetCode=era['offsetCode'],
            zonePolicy=zonePolicy,
            format=format,
            untilYearShort=until_year_short,
            untilMonth=until_month,
            untilDay=until_day,
            untilHour=until_hour,
            untilTimeModifier=until_time_modifier)

        return (era_item, string_length)


def normalize_name(name):
    """Replace hyphen with underscore so that the C++ symbol can compile.
    """
    return name.replace('-', '_')

def normalize_raw(raw_line):
    """Replace hard tabs with 4 spaces.
    """
    return raw_line.replace('\t', '    ')
