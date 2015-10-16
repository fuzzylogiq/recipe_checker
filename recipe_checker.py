#!/usr/bin/python
# encoding: utf-8
'''
recipe_checker.py

Script to check through an autopkg recipe/override and ensure it meets certain
standards

Copyright (C) University of Oxford 2015
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
'''

import plistlib
import sys

DEFAULT_VERBOSITY = 2

# FIXME NOT USED YET
INPUT_SETTINGS = {
            'MUNKI_REPO_SUBDIR':
                { 'SET':True,
                'VALUE': None }
            }

PKGINFO_SETTINGS = {
            'catalogs': 
                { 'SET': True,
                'VALUE': ['testing'] },
            'category': 
                { 'SET': True,
                'VALUE': None },
            'description':
                { 'SET': True,
                'VALUE': None },
            'developer':
                { 'SET': True,
                'VALUE': None },
            'display_name': 
                { 'SET': True,
                'VALUE': None },
            'name':
                { 'SET': True,
                'VALUE': None },
            'unattended_install': 
                { 'SET': True,
                'VALUE': True }
            }


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class RecipeChecker():
    def __init__(self, recipe):
        self.report =  "------------------------------------------------\n"
        self.recipe_name = recipe
        self.recipe_as_dict = {}
        self.pkginfo = {}
        self.verbosity = DEFAULT_VERBOSITY
        self.is_recipe = True

    def get_recipe_type(self, recipe):
        recipe_type = recipe.split('.')[1]
        return recipe_type

    def load_recipe(self):
        if self.recipe_name.split('.')[-1] == "recipe":
            self.recipe_type = self.get_recipe_type(self.recipe_name)
            try:
                self.recipe_as_dict = plistlib.readPlist(self.recipe_name)
            except Exception, e:
                self.is_recipe = False
                self.report += (bcolors.FAIL
                        + "Unable to load %s, are you sure it is a recipe file?"
                        % self.recipe_name
                        + bcolors.ENDC)
        else:
            self.is_recipe = False
            self.report += (bcolors.FAIL
                    + "Bailing: %s does not look like a .recipe file"
                    % self.recipe_name
                    + bcolors.ENDC)

    def check_pkginfo(self, setting, config):
        if config['SET'] == True:
            if setting in self.pkginfo and self.pkginfo[setting] != '':
                if config['VALUE']:
                    if self.pkginfo[setting] == config['VALUE']:
                        if self.verbosity > 0:
                            self.report += (bcolors.OKBLUE
                                    + '%s correctly set to:\t\t\'%s\'\n'
                                    % (setting, self.pkginfo[setting])
                                    + bcolors.ENDC)
                    else:
                        self.report += (bcolors.WARNING
                                + '%s wrongly set to:\t\'%s\'\n'
                                % (setting, self.pkginfo[setting])
                                + bcolors.ENDC)
                else:
                    if self.verbosity > 1:
                        self.report += (bcolors.OKBLUE
                                + '%s set to:\t\t\t\'%s\'\n'
                                % (setting, self.pkginfo[setting])
                                + bcolors.ENDC)
            elif setting not in self.pkginfo:
                self.report += (bcolors.FAIL
                        + '>>> %s missing from pkginfo! <<<\n'
                        % (setting)
                        + bcolors.ENDC)
            elif self.pkginfo[setting] == '':
                self.report += (bcolors.WARNING
                        + '%s present but not set to any value!\n'
                        % (setting)
                        + bcolors.ENDC)


    def check_recipe(self):
        self.report +=  "Checking recipe %s\n" % self.recipe_name
        if self.recipe_type == 'munki':
            if 'Input' in self.recipe_as_dict:
                if 'pkginfo' in self.recipe_as_dict['Input']:
                    self.pkginfo = self.recipe_as_dict['Input']['pkginfo']
                    for setting, config  in PKGINFO_SETTINGS.iteritems():
                        self.check_pkginfo(setting, config)
        else:
            self.report += (bcolors.FAIL
            + '%s is not a .munki recipe\n'
            % self.recipe_name
            + bcolors.ENDC)

def main():
    recipe = sys.argv[1]
    r = RecipeChecker(recipe)
    r.load_recipe()
    if r.is_recipe:
        r.check_recipe()
    print r.report

if __name__ == '__main__':
    main()

