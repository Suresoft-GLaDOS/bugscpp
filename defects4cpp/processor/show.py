import argparse
import os
import sys

import hjson
import lib


def run_show():
    try:
        # display project list
        lib.io.kindness_message("=== Taxonomy Project Lists ===")
        dirs = os.listdir(os.path.join(lib.io.DPP_HOME, "taxonomy"))
        for d in dirs:
            meta_file_path = os.path.join(lib.io.DPP_HOME, "taxonomy", d, "meta.hjson")
            with open(meta_file_path, "r", encoding="utf-8") as meta_file:
                meta = hjson.load(meta_file)
                taxonomy_cnt = len(meta["defects"])
                lib.io.info_message("[%s], # of taxonomies: %d" % (d, taxonomy_cnt))
                lib.io.info2_message("URL: %s" % meta["info"]["url"])
                lib.io.info2_message("DESC: %s" % meta["info"]["short-desc"])
        pass

    except:
        pass
