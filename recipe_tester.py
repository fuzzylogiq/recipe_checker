#!/usr/bin/python
# encoding: utf-8
"""
recipe_checker3.py

Takes autopkg recipe file(s) and runs tests on them, outputting
results to console or as a json object.

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
import json
import argparse
import glob
import os

SUPPORTED_RECIPE_TYPES = ['download', 'pkg', 'munki']
RECIPE = 'StatPlus_mac_LE.munki.recipe'
TESTS_FOLDER = './tests'

class Recipe(dict):
    ''' Represents an autopkg recipe '''
    def __init__(self, recipe_file):
        self.recipe_file = recipe_file
        self.load_recipe()
        self.set_recipe_type()
        
    def load_recipe(self):
        try:
            with open(self.recipe_file, 'r') as infile:
                self.update(plistlib.readPlist(infile))
        except Exception, e:
            print e

    def set_recipe_type(self):
        # Set recipe type based on extension
        recipe_type = ''
        try:
            recipe_type = self.recipe_file.split('.')[-2]
        except IndexError as e:
            pass
        if recipe_type in SUPPORTED_RECIPE_TYPES:
            self.recipe_type = recipe_type
        else:
            self.recipe_type = 'unknown'


class RecipeTester(object):
    ''' Generic recipe testing class '''
    def __init__(self, recipe_file, test_suite):
        self.test_suite = test_suite
        self.recipe = {}
        self.results = []
        self.stop_running_tests = False
        try:
            self.recipe = Recipe(recipe_file)
            self.recipe_type = self.recipe.recipe_type
        except Exception as e:
            print 'Unable to load recipe plist from file.'

    def test_recipe_is_loaded(self, severity):
        '''Tests if recipe can be loaded successfully.'''
        fail_reason = 'The recipe could not be loaded'
        this_result = {
            'test_type': 'recipe_is_loaded'
            }
        if self.recipe:
            this_result.update({
                'result': True
                })
        else:
            self.stop_running_tests = True
            this_result.update({
                'result': False,
                'fail_severity': severity,
                'fail_reason': fail_reason
                })
        self.results.append(this_result)
        return this_result['result']

    def test_recipe_has_correct_ext(self, severity):
        '''Tests if recipe has correct extension (.recipe)'''
        fail_reason = 'The recipe should have the extension \'.recipe\''
        this_result = {'test_type': 'recipe_has_correct_ext'}
        if self.recipe:
            if self.recipe.recipe_file.split('.')[-1] == 'recipe':
                this_result.update({
                    'result': True
                    })
            else:
                this_result.update({
                    'result': False,
                    'fail_severity': severity,
                    'fail_reason': fail_reason
                    })
            self.results.append(this_result)
            return this_result['result']

    def test_key_exists(self, keypath, severity):
        fail_reason = 'The key \'%s\' should exist and does not' % keypath
        this_result = {
            'test_type': 'key_exists',
            'keypath': keypath
            }
        split_keypath = keypath.split('/')
        key_dict = {}
        key_dict[keypath] = {}
        cur = self.recipe
        for key in split_keypath:
            if key not in cur:
                this_result.update({
                    'result': False,
                    'fail_severity': severity,
                    'fail_reason': fail_reason
                })
                self.results.append(this_result)
                return this_result['result']
            else:
                cur = cur[key]
        this_result['result'] = True
        self.results.append(this_result)
        return this_result['result']

    def test_key_exists_and_has_expected_value(
            self, keypath, expected, severity):
        fail_reason = 'The key \'%s\' should have the value ' \
            '\'%s\' and it does not.' % (keypath, expected)
        this_result = {
            'test_type': 'key_has_expected_value',
            'keypath': keypath,
            'expected_value': expected
            }
        keypath_split = keypath.split('/')
        if self.test_key_exists(keypath, severity=2):
            cur = self.recipe
            for key in keypath_split:
                cur = cur[key]
                if cur == expected:
                    this_result['result'] = True
                else:
                    this_result['result'] = False
            if this_result['result'] == False:
                this_result.update({
                    'fail_severity': severity,
                    'fail_reason': fail_reason
                })
            self.results.append(this_result)
            return this_result['result']

    def test_key_exists_and_is_not_blank(self, keypath, severity):
        fail_reason = 'The key \'%s\' should be non-blank' \
            'and it is not.' % (keypath)
        this_result = {
            'test_type': 'key_exists_and_is_not_blank',
            'keypath': keypath
            }
        keypath_split = keypath.split('/')
        if self.test_key_exists(keypath, severity=2):
            cur = self.recipe
            for key in keypath_split:
                cur = cur[key]
                if cur != '':
                    this_result['result'] = True
                else:
                    this_result['result'] = False
            if this_result['result'] == False:
                this_result.update({
                    'fail_severity': severity,
                    'fail_reason': fail_reason
                })
            self.results.append(this_result)
            return this_result['result']

    def run_tests(self):
        if self.recipe.recipe_type == self.test_suite['test_suite']:
            for test in self.test_suite['tests']:
                if not self.stop_running_tests:
                    if test['test_type'] == 'recipe_is_loaded':
                        self.test_recipe_is_loaded(
                            test['fail_severity']
                            )
                    elif test['test_type'] == 'recipe_has_correct_ext':
                        self.test_recipe_has_correct_ext(
                            test['fail_severity']
                            )
                    elif test['test_type'] == 'key_exists':
                        for keypath in test['keypaths']:
                            self.test_key_exists(
                                keypath['keypath'],
                                keypath['fail_severity']
                                )
                    elif test['test_type'] == 'key_exists_and_is_not_blank':
                        for keypath in test['keypaths']:
                            self.test_key_exists_and_is_not_blank(
                                keypath['keypath'],
                                keypath['fail_severity']
                                )
                    elif test['test_type'] == 'key_exists_and_has_expected_value':
                        for keypath in test['keypaths']:
                            self.test_key_exists_and_has_expected_value(
                                keypath['keypath'],
                                keypath['expected_value'],
                                keypath['fail_severity']
                                )
                    else:
                        print 'Invalid test_type found: %s' % test['test_type']

    def output_test_results(self, method):
        if method == 'console':
            results = ''
            results += 'Testing %s...\n' % self.recipe.recipe_file
            fails = 0
            warns = 0
            passes = 0
            for result in self.results:
                if 'result' in result and result['result'] == False:
                    if result['fail_severity'] == 2:
                        fails += 1
                        results += 'The test \'%s\' failed! Reason: \'%s\'\n' % (
                            result['test_type'],
                            result['fail_reason'])
                    elif result['fail_severity'] == 1:
                        warns += 1
                        results += 'Warning! In test \'%s\': \'%s\'\n' % (
                            result['test_type'],
                            result['fail_reason'])
                else:
                    passes += 1
            results += '%s tests run. %i passes, %i warnings, %i failures\n' % (
                len(self.results), passes, warns, fails)
            if fails > 0:
                results += '\nSHAME, SHAME, SHAME! 🔔\n'
            else:
                results += '\nNo failed tests. 🎉\n'
            results += 72*'-'
            return results 

        if method == 'json':
            return json.dumps(
                self.results,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
                )

def load_all_tests():
    all_tests = {}
    for f in os.listdir(TESTS_FOLDER):
        try:
            with open (os.path.join(TESTS_FOLDER, f), 'r') as infile:
                all_tests.update(plistlib.readPlist(infile))
        except Exception as e:
            print e
    return all_tests

def main():  
    
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", action="store_true")
    group.add_argument("--console", action="store_true")
    parser.add_argument("recipe", action='append', nargs='+', type=str,
                         help="at least one autopkg recipe file")
    args = parser.parse_args()
    
    for recipe in args.recipe[0]:
        rt = RecipeTester(recipe, load_all_tests())

        rt.run_tests()
        if args.json:
            print rt.output_test_results('json')
        elif args.console:
            print rt.output_test_results('console')

if __name__ == '__main__':
    main()
