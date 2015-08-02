#!/usr/bin/env python3
# -*- coding: utf8 -*-

__version__ = 0.1
REPO = '/home/clabaut/Images'

from gi.repository import GExiv2, GLib
import sys
import os, os.path
import yaml
import logging
import platform
from argparse import ArgumentParser, Namespace
from collections import defaultdict

options = Namespace()
logging.basicConfig(format="%(levelname)-8s %(message)s")
logger = logging.getLogger()


def process_main_options():
    global options
    options.verbose = logging.WARNING
    parser = ArgumentParser(description="Rename or collect tags of people in photos.")
    # first retrieve config file if any :
    _version= "renamePeopleTags {0} -- {1} {2}".format(__version__,
            platform.python_implementation(), platform.python_version())
    parser.add_argument('-d', '--directory',
            help="Directory scanned for photos", default=REPO)
    parser.add_argument('-o', '--output',
            help="Output yaml files", default="people.yaml")
    parser.add_argument('-i', '--input',
                        help="Input yaml files with renaming info. "
                        "The content should be a dictionary "
                        "{oldtag1: newtag1, oldtag2; newtag2}",
                        default="rename.yaml")
    parser.add_argument('action', choices=['collect', 'rename'], help="Collect or rename tags",
                        default='collect')
    parser.add_argument("--locations",
                        action="store_const", const=True, default=False,
                        help="Add tag locations in collected file")
    parser.add_argument("-q", "--quiet",
            action="store_const", const=logging.CRITICAL, dest="verbose",
            help="don't print status messages to stderr")
    parser.add_argument("-w", "--warning",
            action="store_const", const=logging.WARNING, dest="verbose",
            help="output warning information to stderr (default)")
    parser.add_argument("-v", "--verbose",
            action="store_const", const=logging.INFO, dest="verbose",
            help="output verbose status (info) to stderr")
    parser.add_argument("--debug",
            action="store_const", const=logging.DEBUG, dest="verbose",
            help="output debug information to stderr")
    parser.add_argument('--version', action='version', version=_version)
    parser.parse_args(namespace=options)
    logger.setLevel(options.verbose)

def get_peopletag(filename):
    peoples = set()
    try:
        image = GExiv2.Metadata(filename)
    except GLib.Error:
        pass
    else:
        tags = image.get_tag_multiple('Xmp.digiKam.TagsList')
        for t in tags:
            peoples.add(t)
        tags = image.get_tag_string('Xmp.lr.hierarchicalSubject')
        tags = tags.split(', ') if tags else []
        for t in tags:
            nt = t.replace('|', '/')
            peoples.add(nt)
        pt = [ t for t in image.get_tags() if
            'MPReg:PersonDisplayName' in t or 'mwg-rs:Name' in t]
        for t in pt:
            peoples.add(image.get(t))
        image.free()
    return peoples


def get_peopletag_collection(files):
    peoples = defaultdict(set)
    for f in files:
        for t in get_peopletag(f):
            peoples[t].add(f)
    return peoples


def rename_peopletag_collection(files):
    global options
    logger.info("Renaming tags")
    renameinfo = {}
    with  open(options.input, 'r') as infile:
        renameinfo = yaml.load(infile)
    if not renameinfo:
        return
    for f in files:
        taglist = []
        for t in get_peopletag(f):
            if t in renameinfo:
                taglist.append(renameinfo[t])
            else:
                taglist.append(t)
        write_people_tags(f, taglist, renameinfo)

def write_people_tags(filename, taglist, renameinfo):
    try:
        image = GExiv2.Metadata(filename)
    except GLib.Error:
        pass
    else:
        logging.debug(taglist)
        image.set_tag_multiple('Xmp.digiKam.TagsList', taglist)
        logging.debug(taglist)
        ntlist = []
        for t in taglist:
            ntlist.append(t.replace('/', '|'))
        logging.debug(ntlist)
        image.set_tag_multiple('Xmp.lr.hierarchicalSubject', [])
        image.set_tag_string('Xmp.lr.hierarchicalSubject', ', '.join(ntlist))
        pt = [ t for t in image.get_tags() if
            'MPReg:PersonDisplayName' in t or 'mwg-rs:Name' in t]
        for t in pt:
            name = image.get(t)
            if name in renameinfo:
                image.set_tag_string(t, renameinfo[name])
        image.save_file()
        image.free()


def get_people_region_collection(files):
    peoples = set()
    for f in files:
        try:
            image = GExiv2.Metadata(f)
        except GLib.Error:
            pass
        else:
            pt = [ t for t in image.get_tags() if
                'MPReg:PersonDisplayName' in t or 'mwg-rs:Name' in t]
            for t in pt:
                peoples.add(image.get(t))
    return peoples


def collect_photoѕ():
    photos = []
    prevdir = ""
    for subdir, dirs, files in os.walk(options.directory):
        if subdir != prevdir:
            logger.info("Collecting files in '%s'" % subdir)
            prevdir=subdir
        for f in files:
            photos.append(os.path.join(subdir, f))
    return photos

def people_to_yaml(photos):
    global options
    logger.info("Collecting tags")
    tags = get_peopletag_collection(photos)
    #print(sorted(list(tags))
    logger.info("Creating Yaml output '%s'" % options.output)
    with  open(options.output, 'w') as outfile:
        if options.locations:
            yaml.dump(tags, outfile, encoding='utf-8',
                    allow_unicode=True, default_flow_style=False)
        else:
            yaml.dump(sorted(list(tags.keys())), outfile, encoding='utf-8',
                    allow_unicode=True, default_flow_style=False)

def main():
    global options
    process_main_options()
    photos = collect_photoѕ()
    if options.action == 'collect':
        people_to_yaml(photos)
    elif options.action == 'rename':
        rename_peopletag_collection(photos)


def info(type, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
    # we are in interactive mode or we don't have a tty-like
    # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback
        # we are NOT in interactive mode, print the exception…
        traceback.print_exception(type, value, tb)
        print
        # …then start the debugger in post-mortem mode.
        try:
            import ipdb
            ipdb.pm()
        except:
            import pdb
            # pdb.pm() # deprecated
            pdb.post_mortem(tb) # more “modern”

#TODO : remove for production
sys.excepthook = info

if __name__ == "__main__":
    sys.exit(main())


# vim: sw=4 sts=4 ts=4 et ai

