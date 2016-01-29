#!/usr/bin/python
# encoding: utf-8
"""
recipe_checker2.py

2nd version of recipe checker written more as a test suite

Copyright (C) University of Oxford 2016
    Ben Goodstein <ben.goodstein at it.ox.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import plistlib
import sys
import re

VALID_IDENTIFIERS = [re.compile(r'\buk\.ac\.ox\.orchard\.'),
                     re.compile(r'\blocal\.')]

MUNKI_RECIPE_CONDITIONS = {
    'recipe_loads_successfully': {
        'fail_level': 'fail',
        'reason': 'The recipe could not be loaded as a plist'
    },
    'recipe_looks_like_recipe': {
        'fail_level': 'fail',
        'reason': 'The recipe filename should end in .recipe'
    },
    'recipe_type_is_munki': {
        'fail_level': 'fail',
        'reason': 'A munki recipe should end in .munki.recipe'
    },
    'recipe_has_identifier': {
        'fail_level': 'fail',
        'reason': 'Recipe must have an Identifier'
    },
    'recipe_input_has_pkginfo': {
        'fail_level': 'fail',
        'reason': 'No pkginfo was found in the recipe\'s Input dict'
    },
    'description_is_blank': {
        'fail_level': 'fail',
        'reason': 'Recipe must have a useful Description'
    },
    'identifier_is_sane': {
        'fail_level': 'fail',
        'reason': 'Recipe Identifier must start with uk.ac.ox.orchard. ' \
        'for a recipe or local. for an override'
    },
    'pkginfo_keys_exist': {
        'catalogs': {
            'fail_level': 'fail',
            'reason': 'You must have a catalog key in your pkginfo dict'
        },
        'developer': {
            'fail_level': 'fail',
            'reason': 'You must have a developer key in your pkginfo dict'
        },
        'category': {
            'fail_level': 'fail',
            'reason': 'You must have a category key in your pkginfo dict'
        },
        'description': {
            'fail_level': 'fail',
            'reason': 'You must have a description key in your pkginfo dict'
        },
        'unattended_install': {
            'fail_level': 'fail',
            'reason': 'You must have an unattended_install key in your pkginfo dict'
        }
    },
    'pkginfo_keys_have_expected_value': {
        'catalogs': {
            'fail_level': 'warn',
            'reason': 'catalogs should usually be set to [\'testing\']'
        },
        'unattended_install': {
            'fail_level': 'warn',
            'reason': 'unattended_install should usually be set to True'
        }
    }
}


class LoadError(Exception):
    pass


class Recipe(dict):

    def load_recipe(self, recipe_file):
        try:
            with open(recipe_file, "r") as infile:
                self.update(plistlib.readPlist(infile))
        except Exception as e:
            raise LoadError


class RecipeTester(object):

    def __init__(self, recipe_file):
        self.recipe = Recipe()
        self.recipe_file = recipe_file
        self.test_results = {}
        try:
            self.recipe.load_recipe(recipe_file)
            self.test_results['recipe_loads_successfully'] = True
        except LoadError as e:
            self.test_results['recipe_loads_successfully'] = False

    def test_recipe_looks_like_recipe(self):
        if self.recipe_file.split('.')[-1] == "recipe":
            self.test_results['recipe_looks_like_recipe'] = True
        else:
            self.test_results['recipe_looks_like_recipe'] = False
        return self.test_results['recipe_looks_like_recipe']

    def test_recipe_type(self):
        self.test_results['recipe_type'] = self.recipe_file.split('.')[-2]
        return self.test_results['recipe_type']

    def test_recipe_type_is_download(self):
        if self.test_recipe_type() == "download":
            self.test_results['recipe_type_is_download'] = True
        else:
            self.test_results['recipe_type_is_download'] = False
        return self.test_results['recipe_type_is_download']

    def test_recipe_type_is_pkg(self):
        if self.test_recipe_type() == "pkg":
            self.test_results['recipe_type_is_pkg'] = True
        else:
            self.test_results['recipe_type_is_pkg'] = False
        return self.test_results['recipe_type_is_pkg']

    def test_recipe_type_is_munki(self):
        if self.test_recipe_type() == "munki":
            self.test_results['recipe_type_is_munki'] = True
        else:
            self.test_results['recipe_type_is_munki'] = False
        return self.test_results['recipe_type_is_munki']

    def test_recipe_is_loaded(self):
        if self.recipe:
            self.test_results['recipe_is_loaded'] = True
        else:
            self.test_results['recipe_is_loaded'] = False
        return self.test_results['recipe_is_loaded']

    def test_recipe_has_identifier(self):
        if 'Identifier' in self.recipe:
            self.test_results['recipe_has_identifier'] = True
        else:
            self.test_results['recipe_has_identifier'] = False
        return self.test_results['recipe_has_identifier']

    def test_identifier_is_sane(self):
        for valid_identifier in VALID_IDENTIFIERS:
            if re.match(valid_identifier, self.recipe['Identifier']):
                self.test_results['identifier_is_sane'] = True
            else:
                self.test_results['identifier_is_sane'] = False
        return self.test_results['identifier_is_sane']

    def test_recipe_has_description(self):
        if 'Description' in self.recipe:
            self.test_results['recipe_has_description'] = True
        else:
            self.test_results['recipe_has_description'] = False
        return self.test_results['recipe_has_description']

    def test_description_is_blank(self):
        if self.test_recipe_has_description():
            if self.recipe['Description'] is "":
                self.test_results['description_is_blank'] = True
            else:
                self.test_results['description_is_blank'] = False
            return self.test_results['description_is_blank']

    def test_recipe_has_input(self):
        if 'Input' in self.recipe:
            self.test_results['recipe_has_input'] = True
        else:
            self.test_results['recipe_has_input'] = False
        return self.test_results['recipe_has_input']

    def test_recipe_input_has_pkginfo(self):
        if self.test_recipe_has_input():
            if 'pkginfo' in self.recipe['Input']:
                self.test_results['recipe_input_has_pkginfo'] = True
            else:
                self.test_results['recipe_input_has_pkginfo'] = False
            return self.test_results['recipe_input_has_pkginfo']

    def test_pkginfo_key_exists(self, key):
        if self.test_recipe_input_has_pkginfo():
            if key in self.recipe['Input']['pkginfo']:
                return True
            else:
                return False

    def test_pkginfo_key_has_expected_value(self, key, value):
        if self.test_recipe_input_has_pkginfo():
            if self.test_pkginfo_key_exists(key):
                if self.recipe['Input']['pkginfo'][key] == value:
                    return True
                else:
                    return False

    def check_fail_levels(self, conditions):
        pass

    # MUNKI RECIPE TESTS

    def run_munki_test_suite(self):
        self.test_results['pkginfo_keys_exist'] = {}
        self.test_results['pkginfo_keys_have_expected_value'] = {}
        try:
            self.test_recipe_looks_like_recipe()
            self.test_recipe_type_is_munki()
            self.test_recipe_input_has_pkginfo()

            for key in ['name', 'display_name', 'category', 'catalogs',
                        'developer', 'unattended_install', 'description']:
                self.test_results['pkginfo_keys_exist'][
                    key] = self.test_pkginfo_key_exists(key)
            for key, value in {'catalogs': ['testing'],
                               'unattended_install': True}.iteritems():
                self.test_results['pkginfo_keys_have_expected_value'][key] = [
                    self.test_pkginfo_key_has_expected_value(key, value), value]
        except Exception as e:
            pass
        finally:
            for key, value in MUNKI_RECIPE_CONDITIONS.iteritems():
                if key in self.test_results and not self.test_results[
                        key] and value == 'warn':
                    print "WARN - %s is False" % key
                if key in self.test_results and not self.test_results[
                        key] and value == 'fail':
                    print "FAIL - %s is False" % key
        return self.test_results
