# Copyright 2018 Brian T. Park
#
# MIT License
"""
Generate the zone_info and zone_policies files for Arduino.
"""

import logging
import os
import transformer
from collections import OrderedDict
from transformer import short_name
from transformer import div_to_zero
from extractor import EPOCH_YEAR
from extractor import MAX_YEAR
from extractor import MAX_YEAR_TINY
from extractor import MIN_YEAR
from extractor import MIN_YEAR_TINY
from extractor import MAX_UNTIL_YEAR
from extractor import MAX_UNTIL_YEAR_TINY


class ArduinoGenerator:
    """Generate zone_infos and zone_policies files for Arduino/C++.
    """
    ZONE_INFOS_H_FILE_NAME = 'zone_infos.h'
    ZONE_INFOS_CPP_FILE_NAME = 'zone_infos.cpp'
    ZONE_POLICIES_H_FILE_NAME = 'zone_policies.h'
    ZONE_POLICIES_CPP_FILE_NAME = 'zone_policies.cpp'
    ZONE_STRINGS_CPP_FILE_NAME = 'zone_strings.cpp'
    ZONE_STRINGS_H_FILE_NAME = 'zone_strings.h'

    def __init__(self, invocation, tz_version, tz_files, zones_map, rules_map,
                 removed_zones, removed_policies, notable_zones,
                 notable_policies, extended):
        self.extended = extended  # extended Arduino/C++ database

        self.zone_policies_generator = ZonePoliciesGenerator(
            invocation, tz_version, tz_files, zones_map, rules_map,
            removed_zones, removed_policies, notable_zones, notable_policies,
            extended)
        self.zone_infos_generator = ZoneInfosGenerator(
            invocation, tz_version, tz_files, zones_map, rules_map,
            removed_zones, removed_policies, notable_zones, notable_policies,
            extended)
        self.zone_strings_generator = ZoneStringsGenerator(
            invocation, tz_version, tz_files, zones_map, rules_map,
            removed_zones, removed_policies, notable_zones, notable_policies,
            extended)

    def generate_files(self, output_dir):
        # zone_policies.*
        if self.extended:
            self.zone_policies_generator.collect_letter_strings()
        self._write_file(output_dir, self.ZONE_POLICIES_H_FILE_NAME,
                         self.zone_policies_generator.generate_policies_h())
        self._write_file(output_dir, self.ZONE_POLICIES_CPP_FILE_NAME,
                         self.zone_policies_generator.generate_policies_cpp())

        # zone_infos.*
        self._write_file(output_dir, self.ZONE_INFOS_H_FILE_NAME,
                         self.zone_infos_generator.generate_infos_h())
        self._write_file(output_dir, self.ZONE_INFOS_CPP_FILE_NAME,
                         self.zone_infos_generator.generate_infos_cpp())

        # zone_strings.*
        if self.extended:
            self.zone_strings_generator.collect_strings()
            self._write_file(output_dir, self.ZONE_STRINGS_H_FILE_NAME,
                             self.zone_strings_generator.generate_strings_h())
            self._write_file(output_dir, self.ZONE_STRINGS_CPP_FILE_NAME,
                             self.zone_strings_generator.generate_strings_cpp())

    def _write_file(self, output_dir, filename, content):
        full_filename = os.path.join(output_dir, filename)
        with open(full_filename, 'w', encoding='utf-8') as output_file:
            print(content, end='', file=output_file)
        logging.info("Created %s", full_filename)


class ZonePoliciesGenerator:

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

#ifndef ACE_TIME_{dbHeaderNamespace}_ZONE_POLICIES_H
#define ACE_TIME_{dbHeaderNamespace}_ZONE_POLICIES_H

#include "../common/ZonePolicy.h"

namespace ace_time {{
namespace {dbNamespace} {{

// numPolicies: {numPolicies}
{policyItems}

// The following zone policies are not supported in the current version of
// AceTime.
//
// numPolicies: {numRemovedPolicies}
//
{removedPolicyItems}

// The following zone policies may have inaccuracies due to the following
// reasons:
//
// numPolicies: {numNotablePolicies}
//
{notablePolicyItems}

}}
}}

#endif
"""

    ZONE_POLICIES_H_POLICY_ITEM = """\
extern const common::ZonePolicy kPolicy{policyName};
"""

    ZONE_POLICIES_H_REMOVED_POLICY_ITEM = """\
// kPolicy{policyName} ({policyReason})
"""

    ZONE_POLICIES_H_NOTABLE_POLICY_ITEM = """\
// kPolicy{policyName} ({policyReason})
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
namespace {dbNamespace} {{

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

{letterArray}

const common::ZonePolicy kPolicy{policyName} = {{
  sizeof(kZoneRules{policyName})/sizeof(common::ZoneRule) /*numRules*/,
  kZoneRules{policyName} /*rules*/,
  {numLetters} /* numLetters */,
  {letterArrayRef} /* letters */,
}};
"""

    ZONE_POLICIES_LETTER_ARRAY = """\
static const char* const kLetters{policyName}[] = {{
{letterItems}
}};
"""

    ZONE_POLICIES_CPP_RULE_ITEM = """\
  // {rawLine}
  {{
    {fromYearTiny} /*fromYearTiny*/,
    {toYearTiny} /*toYearTiny*/,
    {inMonth} /*inMonth*/,
    {onDayOfWeek} /*onDayOfWeek*/,
    {onDayOfMonth} /*onDayOfMonth*/,
    {atTimeCode} /*atTimeCode*/,
    '{atTimeModifier}' /*atTimeModifier*/,
    {deltaCode} /*deltaCode*/,
    {letter} /*letter{letterComment}*/,
  }},
"""

    SIZEOF_ZONE_RULE_8 = 9
    SIZEOF_ZONE_RULE_32 = 9
    SIZEOF_ZONE_POLICY_8 = 3
    SIZEOF_ZONE_POLICY_32 = 5

    def __init__(self, invocation, tz_version, tz_files, zones_map, rules_map,
                 removed_zones, removed_policies, notable_zones,
                 notable_policies, extended):
        self.invocation = invocation
        self.tz_version = tz_version
        self.tz_files = tz_files
        self.zones_map = zones_map
        self.rules_map = rules_map
        self.removed_zones = removed_zones
        self.removed_policies = removed_policies
        self.notable_zones = notable_zones
        self.notable_policies = notable_policies
        self.extended = extended  # extended Arduino/C++ database

        self.letters_map = {}  # map{policy_name: map{letter: index}}
        self.db_namespace = 'zonedbx' if extended else 'zonedb'
        self.db_header_namespace = 'ZONEDBX' if extended else 'ZONEDB'

    def collect_letter_strings(self):
        """Loop through all ZoneRules and collect the LETTERs which are
        more than one letter long into self.letters_map.
        """
        letters_map = {}
        for policy, rules in self.rules_map.items():
            letters = set()
            for rule in rules:
                if len(rule.letter) > 1:
                    letters.add(rule.letter)
            indexed_letters_map = OrderedDict()
            if letters:
                for letter in sorted(letters):
                    transformer.add_string(indexed_letters_map, letter)
                letters_map[policy] = indexed_letters_map
        self.letters_map = letters_map

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
                    policyReason=reason)

        notable_policy_items = ''
        for name, reason in sorted(self.notable_policies.items()):
            notable_policy_items += \
                self.ZONE_POLICIES_H_NOTABLE_POLICY_ITEM.format(
                    policyName=name,
                    policyReason=reason)

        return self.ZONE_POLICIES_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace,
            tz_files=', '.join(self.tz_files),
            numPolicies=len(self.rules_map),
            policyItems=policy_items,
            numRemovedPolicies=len(self.removed_policies),
            removedPolicyItems=removed_policy_items,
            numNotablePolicies=len(self.notable_policies),
            notablePolicyItems=notable_policy_items)

    def generate_policies_cpp(self):
        policy_items = ''
        num_rules = 0
        for name, rules in sorted(self.rules_map.items()):
            indexed_letters = self.letters_map.get(name)
            policy_items += self._generate_policy_item(name, rules,
                indexed_letters)
            num_rules += len(rules)

        num_policies = len(self.rules_map)
        memory8 = (num_policies * self.SIZEOF_ZONE_POLICY_8 +
                   num_rules * self.SIZEOF_ZONE_RULE_8)
        memory32 = (num_policies * self.SIZEOF_ZONE_POLICY_32 +
                    num_rules * self.SIZEOF_ZONE_RULE_32)

        return self.ZONE_POLICIES_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace,
            numPolicies=num_policies,
            numRules=num_rules,
            memory8=memory8,
            memory32=memory32,
            policyItems=policy_items)

    def _generate_policy_item(self, name, rules, indexed_letters):
        rule_items = ''
        for rule in rules:
            at_time_code = div_to_zero(rule.atSecondsTruncated, 15 * 60)
            delta_code = div_to_zero(rule.deltaSecondsTruncated, 15 * 60)

            from_year = rule.fromYear
            from_year_tiny = to_tiny_year(from_year)
            to_year = rule.toYear
            to_year_tiny = to_tiny_year(to_year)

            if len(rule.letter) == 1:
                letter = "'%s'" % rule.letter
                letterComment = ''
            elif len(rule.letter) > 1:
                index = indexed_letters.get(rule.letter)
                if index == None:
                    raise Exception('Could not find index for letter (%s)'
                                    % rule.letter)
                if index >= 32:
                    raise Exception('Number of indexed letters >= 32')
                letter = index
                letterComment = ('; "%s"' % rule.letter)
            else:
                raise Exception('len(%s) == 0; should not happen' % rule.letter)

            rule_items += self.ZONE_POLICIES_CPP_RULE_ITEM.format(
                rawLine=normalize_raw(rule.rawLine),
                fromYearTiny=from_year_tiny,
                toYearTiny=to_year_tiny,
                inMonth=rule.inMonth,
                onDayOfWeek=rule.onDayOfWeek,
                onDayOfMonth=rule.onDayOfMonth,
                atTimeCode=at_time_code,
                atTimeModifier=rule.atTimeModifier,
                deltaCode=delta_code,
                letter=letter,
                letterComment=letterComment)

        num_rules = len(rules)
        memory8 = (1 * self.SIZEOF_ZONE_POLICY_8 +
                   num_rules * self.SIZEOF_ZONE_RULE_8)
        memory32 = (1 * self.SIZEOF_ZONE_POLICY_32 +
                    num_rules * self.SIZEOF_ZONE_RULE_32)

        policyName = normalize_name(name)
        numLetters = len(indexed_letters) if indexed_letters else 0
        if numLetters:
            letterArrayRef = 'kLetters%s' % policyName
            letterItems = ''
            for name, index in indexed_letters.items():
                letterItems += ('  /*%d*/ "%s",\n' % (index, name))
            letterArray = self.ZONE_POLICIES_LETTER_ARRAY.format(
                policyName=policyName,
                letterItems=letterItems)
        else:
            letterArrayRef = 'nullptr'
            letterArray = ''

        return self.ZONE_POLICIES_CPP_POLICY_ITEM.format(
            policyName=policyName,
            numRules=num_rules,
            memory8=memory8,
            memory32=memory32,
            ruleItems=rule_items,
            numLetters=numLetters,
            letterArrayRef=letterArrayRef,
            letterArray=letterArray)


class ZoneInfosGenerator:
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

#ifndef ACE_TIME_{dbHeaderNamespace}_ZONE_INFOS_H
#define ACE_TIME_{dbHeaderNamespace}_ZONE_INFOS_H

#include "../common/ZoneInfo.h"

#define ACE_TIME_TZ_DATABASE_VERSION "{tz_version}"

namespace ace_time {{
namespace {dbNamespace} {{

// numInfos: {numInfos}
{infoItems}

// The following zones are not supported in the current version of AceTime.
//
// numInfos: {numRemovedInfos}
//
{removedInfoItems}

// The following zones may have inaccuracies due to the following reasons:
//
// numInfos: {numNotableInfos}
//
{notableInfoItems}

}}
}}

#endif
"""

    ZONE_INFOS_H_INFO_ITEM = """\
extern const common::ZoneInfo kZone{zoneShortName}; // {zoneFullName}
"""

    ZONE_INFOS_H_REMOVED_INFO_ITEM = """\
// {zoneFullName} ({infoReason})
"""

    ZONE_INFOS_H_NOTABLE_INFO_ITEM = """\
// {zoneFullName} ({infoReason})
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
// Strings: {stringLength}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//
// DO NOT EDIT

#include "zone_policies.h"
#include "zone_infos.h"

namespace ace_time {{
namespace {dbNamespace} {{

{infoItems}

}}
}}
"""

    ZONE_INFOS_CPP_INFO_ITEM = """\
//---------------------------------------------------------------------------
// Zone name: {zoneFullName}
// Era count: {numEras}
// Strings: {stringLength}
// Memory (8-bit): {memory8}
// Memory (32-bit): {memory32}
//---------------------------------------------------------------------------

static const common::ZoneEra kZoneEra{zoneShortName}[] = {{
{eraItems}
}};

const common::ZoneInfo kZone{zoneShortName} = {{
  "{zoneFullName}" /*name*/,
  kZoneEra{zoneShortName} /*eras*/,
  sizeof(kZoneEra{zoneShortName})/sizeof(common::ZoneEra) /*numEras*/,
}};

"""

    ZONE_INFOS_CPP_ERA_ITEM = """\
  // {rawLine}
  {{
    {offsetCode} /*offsetCode*/,
    {zonePolicy} /*zonePolicy*/,
    {deltaCode} /*deltaCode*/,
    "{format}" /*format*/,
    {untilYearTiny} /*untilYearTiny*/,
    {untilMonth} /*untilMonth*/,
    {untilDay} /*untilDay*/,
    {untilTimeCode} /*untilTimeCode*/,
    '{untilTimeModifier}' /*untilTimeModifier*/,
  }},
"""

    SIZEOF_ZONE_ERA_8 = 11
    SIZEOF_ZONE_ERA_32 = 15
    SIZEOF_ZONE_INFO_8 = 5
    SIZEOF_ZONE_INFO_32 = 9

    def __init__(self, invocation, tz_version, tz_files, zones_map, rules_map,
                 removed_zones, removed_policies, notable_zones,
                 notable_policies, extended):
        self.invocation = invocation
        self.tz_version = tz_version
        self.tz_files = tz_files
        self.zones_map = zones_map
        self.rules_map = rules_map
        self.removed_zones = removed_zones
        self.removed_policies = removed_policies
        self.notable_zones = notable_zones
        self.notable_policies = notable_policies
        self.extended = extended  # extended Arduino/C++ database

        self.db_namespace = 'zonedbx' if extended else 'zonedb'
        self.db_header_namespace = 'ZONEDBX' if extended else 'ZONEDB'

    def generate_infos_h(self):
        info_items = ''
        for name, zones in sorted(self.zones_map.items()):
            info_items += self.ZONE_INFOS_H_INFO_ITEM.format(
                zoneShortName=normalize_name(short_name(name)),
                zoneFullName=name)

        removed_info_items = ''
        for name, reason in sorted(self.removed_zones.items()):
            removed_info_items += self.ZONE_INFOS_H_REMOVED_INFO_ITEM.format(
                zoneFullName=name, infoReason=reason)

        notable_info_items = ''
        for name, reason in sorted(self.notable_zones.items()):
            notable_info_items += self.ZONE_INFOS_H_NOTABLE_INFO_ITEM.format(
                zoneFullName=name, infoReason=reason)

        return self.ZONE_INFOS_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace,
            tz_files=', '.join(self.tz_files),
            numInfos=len(self.zones_map),
            infoItems=info_items,
            numRemovedInfos=len(self.removed_zones),
            removedInfoItems=removed_info_items,
            numNotableInfos=len(self.notable_zones),
            notableInfoItems=notable_info_items)

    def generate_infos_cpp(self):
        info_items = ''
        num_eras = 0
        string_length = 0
        for name, eras in sorted(self.zones_map.items()):
            (info_item, info_string_length) = self._generate_info_item(
                name, eras)
            info_items += info_item
            string_length += info_string_length
            num_eras += len(eras)

        num_infos = len(self.zones_map)
        memory8 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_8 +
                   num_infos * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_32 +
                    num_infos * self.SIZEOF_ZONE_INFO_32)

        return self.ZONE_INFOS_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace,
            numInfos=num_infos,
            numEras=num_eras,
            stringLength=string_length,
            memory8=memory8,
            memory32=memory32,
            infoItems=info_items)

    def _generate_info_item(self, name, eras):
        era_items = ''
        string_length = 0
        for era in eras:
            (era_item, length) = self._generate_era_item(name, era)
            era_items += era_item
            string_length += length

        string_length += len(name) + 1
        num_eras = len(eras)
        memory8 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_8 +
                   1 * self.SIZEOF_ZONE_INFO_8)
        memory32 = (string_length + num_eras * self.SIZEOF_ZONE_ERA_32 +
                    1 * self.SIZEOF_ZONE_INFO_32)

        info_item = self.ZONE_INFOS_CPP_INFO_ITEM.format(
            zoneFullName=normalize_name(name),
            zoneShortName=normalize_name(short_name(name)),
            numEras=num_eras,
            stringLength=string_length,
            memory8=memory8,
            memory32=memory32,
            eraItems=era_items)
        return (info_item, string_length)

    def _generate_era_item(self, name, era):
        policy_name = era.rules
        if policy_name == '-' or policy_name == ':':
            zone_policy = 'nullptr'
            delta_code = div_to_zero(era.rulesDeltaSecondsTruncated, 15 * 60)
        else:
            zone_policy = '&kPolicy%s' % normalize_name(policy_name)
            delta_code = 0

        until_year = era.untilYear
        if until_year == MAX_UNTIL_YEAR:
            until_year_tiny = MAX_UNTIL_YEAR_TINY
        else:
            until_year_tiny = until_year - EPOCH_YEAR

        until_month = era.untilMonth
        if not until_month:
            until_month = 1

        until_day = era.untilDay
        if not until_day:
            until_day = 1

        until_time_code = div_to_zero(era.untilSecondsTruncated, 15 * 60)
        until_time_modifier = era.untilTimeModifier
        offset_code = div_to_zero(era.offsetSecondsTruncated, 15 * 60)

        # Replace %s with just a % for C++
        format = era.format.replace('%s', '%')
        string_length = len(format) + 1

        era_item = self.ZONE_INFOS_CPP_ERA_ITEM.format(
            rawLine=normalize_raw(era.rawLine),
            offsetCode=offset_code,
            deltaCode=delta_code,
            zonePolicy=zone_policy,
            format=format,
            untilYearTiny=until_year_tiny,
            untilMonth=until_month,
            untilDay=until_day,
            untilTimeCode=until_time_code,
            untilTimeModifier=until_time_modifier)

        return (era_item, string_length)


class ZoneStringsGenerator:

    ZONE_STRINGS_CPP_FILE = """\
// This file was generated by the following script:
//
//   $ {invocation}
//
// using the TZ Database files from
// https://github.com/eggert/tz/releases/tag/{tz_version}
//
// DO NOT EDIT
namespace ace_time {{
namespace {dbNamespace} {{

// numStrings: {numStrings}
// memory: {sizeStrings}
// memory original: {originalSizeStrings}
const char* const kStrings[] = {{
{stringItems}
}};

}}
}}
"""

    ZONE_STRINGS_ITEM = """\
  /*{index:3}*/ "{stringName}",
"""

    ZONE_STRINGS_H_FILE = """\
// This file was generated by the following script:
//
//   $ {invocation}
//
// using the TZ Database files from
// https://github.com/eggert/tz/releases/tag/{tz_version}
//
// DO NOT EDIT
#ifndef ACE_TIME_{dbHeaderNamespace}_ZONE_STRINGS_H
#define ACE_TIME_{dbHeaderNamespace}_ZONE_STRINGS_H

namespace ace_time {{
namespace {dbNamespace} {{

extern const char* const kStrings[];

}}
}}
#endif
"""

    def __init__(self, invocation, tz_version, tz_files, zones_map, rules_map,
                 removed_zones, removed_policies, notable_zones,
                 notable_policies, extended):
        self.invocation = invocation
        self.tz_version = tz_version
        self.tz_files = tz_files
        self.zones_map = zones_map
        self.rules_map = rules_map
        self.removed_zones = removed_zones
        self.removed_policies = removed_policies
        self.notable_zones = notable_zones
        self.notable_policies = notable_policies
        self.extended = extended  # extended Arduino/C++ database

        self.db_namespace = 'zonedbx' if extended else 'zonedb'
        self.db_header_namespace = 'ZONEDBX' if extended else 'ZONEDB'
        self.strings = OrderedDict()
        self.strings_size = 0
        self.strings_original_size = 0

    def collect_strings(self):
        """Collect all ZoneRule.letter and ZoneEra.format strings into a single
        array, for deduplication. However, bringing all strings into a single
        array means that this gets loaded even if the application uses only a
        few zones. See collect_letter_strings() for code that collects only the
        ZoneRule.letter strings.
        """
        strings_count = {}
        for name, eras in self.zones_map.items():
            for era in eras:
                format = era.format.replace('%s', '%')
                count = strings_count.get(format)
                if count == None:
                    count = 1
                strings_count[format] = count + 1
        for name, rules in self.rules_map.items():
            for rule in rules:
                count = strings_count.get(rule.letter)
                if count == None:
                    count = 1
                strings_count[rule.letter] = count + 1

        size = 0
        original_size = 0
        for name in sorted(strings_count):
            transformer.add_string(self.strings, name)
            csize = len(name) + 1  # including NUL char in C String
            size += csize
            original_size += strings_count[name] * csize
        self.strings_size = size
        self.strings_original_size = original_size

    def generate_strings_cpp(self):
        string_items = ''
        for name, index in self.strings.items():
            string_items += self.ZONE_STRINGS_ITEM.format(
                stringName=name,
                index=index)

        return self.ZONE_STRINGS_CPP_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace,
            numStrings=len(self.strings),
            sizeStrings=self.strings_size,
            originalSizeStrings=self.strings_original_size,
            stringItems=string_items)

    def generate_strings_h(self):
        return self.ZONE_STRINGS_H_FILE.format(
            invocation=self.invocation,
            tz_version=self.tz_version,
            dbNamespace=self.db_namespace,
            dbHeaderNamespace=self.db_header_namespace)


def to_tiny_year(year):
    if year == MAX_YEAR:
        return MAX_YEAR_TINY
    elif year == MIN_YEAR:
        return MIN_YEAR_TINY
    else:
        return year - EPOCH_YEAR


def normalize_name(name):
    """Replace hyphen with underscore so that the C++ symbol can compile.
    """
    return name.replace('-', '_')


def normalize_raw(raw_line):
    """Replace hard tabs with 4 spaces.
    """
    return raw_line.replace('\t', '    ')
