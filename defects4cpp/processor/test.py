import argparse
import os
import sys

import hjson
import lib
from lib import AssertFailed, ValidateFailed
from processor.actions import CommandAction


def tester_factory(actions, build_tool_name, checkout_dir):
    if actions["generator"] == "command":
        # build_tool_name, checkout_dir
        commands = []
        for c in actions["command"]:
            commands.append(
                f'docker run -v "{checkout_dir}":/workspace {build_tool_name} {c}'
            )
        return CommandAction(commands)
    else:
        return None


def run_test():
    try:
        parser = argparse.ArgumentParser(
            usage="d++ test --project=[project_name] --no=[number] [checkout directory]"
        )

        parser.add_argument("-p", "--project", required=True, help="specified project")
        parser.add_argument("-n", "--no", required=True, help="specified bug number")
        parser.add_argument(
            "-b", "--buggy", action="store_true", help="whether buggy version or not"
        )
        parser.add_argument("checkout")
        args = parser.parse_args(sys.argv[2:])

        version = "buggy" if args.buggy else "fixed"

        # validation check
        project_dir = os.path.join(lib.io.DPP_HOME, "taxonomy", args.project)
        if not os.path.exists(project_dir):
            raise ValidateFailed

        if not os.path.exists(args.checkout):
            raise AssertFailed("checkout folder not exists")

        meta_file_path = os.path.join(project_dir, "meta.hjson")
        if not os.path.exists(meta_file_path):
            raise AssertFailed("File not exists: ", meta_file_path)

        with open(meta_file_path, "r", encoding="utf-8") as meta_file:
            meta = hjson.load(meta_file)

        action = "tester"
        if action in meta["defects"][str(args.no)][version]:
            actions = meta["defects"][str(args.no)][version][action]
            lib.io.kindness_message("build procedure [DEFECT]")
        else:
            actions = meta["common"][action]
            lib.io.kindness_message("build procedure [COMMON]")

        builder = tester_factory(actions, args.project, args.checkout)

        # from
        succeed = builder.run()

        if not succeed:
            raise AssertFailed("Test Failed")

    except ValidateFailed:
        lib.io.error_message("invalid arguments, check project name or bug numbers")
    except AssertFailed as e:
        lib.io.error_message(e)
    except:
        lib.io.error_message(lib.get_trace_back())
        pass
