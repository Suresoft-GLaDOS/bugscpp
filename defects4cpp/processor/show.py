import os
import lib
import sys
import argparse


def run_show():
    try:
        parser = argparse.ArgumentParser(usage="d++ show [options]")
        # lib.io.kindness_message("HOME = %s" % lib.io.DPP_HOME)

        parser.add_argument("-p", "--project", default=False, action="store_true", help="show only project lists")
        args = parser.parse_args(sys.argv[2:])

        # display project list
        if args.project:
            lib.io.kindness_message("=== Taxonomy Project Lists ===")
            dirs = os.listdir(os.path.join(lib.io.DPP_HOME, "taxonomy"))
            for d in dirs:
                lib.io.kindness_message("%s" % d)
            pass
        # display all status summary
        else:
            lib.io.kindness_message("=== Taxonomy Summaries ===")

    except:
        pass
