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
import argparse

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
    def __init__(self, recipe, verbosity):
        self.report =  "------------------------------------------------\n"
        self.subreport = []
        self.recipe_name = recipe
        self.recipe_as_dict = {}
        self.pkginfo = {}
        self.verbosity = verbosity
        self.is_recipe = True

    def get_recipe_type(self, recipe):
        recipe_type = recipe.split('.')[-2]
        return recipe_type

    def reporter(self, report_type, report_string, inserts):
        if report_type == "fail":
            label = "[fail] "
            color = bcolors.FAIL
            verbosity_level = 0
        if report_type == "warn":
            label = "[warn] "
            color = bcolors.WARNING
            verbosity_level = 1
        if report_type == "ok":
            label = "[ ok ] "
            color = bcolors.OKBLUE
            verbosity_level = 2
        if self.verbosity >= verbosity_level:
            self.subreport.append (color
                                 + label
                                 + report_string 
                                 % inserts
                                 + bcolors.ENDC)

    def load_recipe(self):
        self.report +=  "Checking recipe %s...\n" % self.recipe_name
        if self.recipe_name.split('.')[-1] == "recipe":
            self.recipe_type = self.get_recipe_type(self.recipe_name)
            try:
                self.recipe_as_dict = plistlib.readPlist(self.recipe_name)
            except Exception, e:
                self.is_recipe = False
                self.reporter("fail", 
                              "Unable to load %s, are you sure"
                              "it is a recipe file?",
                              (self.recipe_name))
        else:
            self.is_recipe = False
            self.reporter("fail",
                          "Bailing: %s does not look like a .recipe file",
                          (self.recipe_name))

    def check_pkginfo(self, setting, config):
        if config['SET']:
            if setting not in self.pkginfo:
                self.reporter("fail",
                              '%s missing from pkginfo!',
                              (setting))
            elif self.pkginfo[setting] == '':
                self.reporter("fail",
                              '%s present but not set to any value!',
                              (setting))
            else:
                if config['VALUE']:
                    if self.pkginfo[setting] == config['VALUE']:
                        self.reporter("ok",
                                      '%s correctly set to: \'%s\'',
                                      (setting, self.pkginfo[setting]))
                    else:
                        self.reporter("warn",
                                      '%s wrongly set to: \'%s\'',
                                      (setting, self.pkginfo[setting]))
                else:
                    self.reporter("ok",
                                  '%s set to: \'%s\'',
                                  (setting, self.pkginfo[setting]))
            


    def check_recipe(self):
        if (self.recipe_type == 'munki' and 'Input' in self.recipe_as_dict
            and 'pkginfo' in self.recipe_as_dict['Input']):
            self.pkginfo = self.recipe_as_dict['Input']['pkginfo']
            for setting, config  in PKGINFO_SETTINGS.iteritems():
                self.check_pkginfo(setting, config)
        else:
            self.reporter("fail",
            '%s is not a .munki recipe',
            (self.recipe_name))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("recipe", type=str, help="a valid autopkg recipe file")
    args = parser.parse_args()

    recipe = args.recipe
    verbosity = args.verbose
    r = RecipeChecker(recipe, verbosity)
    r.load_recipe()
    if r.is_recipe:
        r.check_recipe()
    print r.report
    if r.subreport != []:
        for line in r.subreport:
            print line
    else:
        print "==> Recipe checks passed!"

if __name__ == '__main__':
    main()

