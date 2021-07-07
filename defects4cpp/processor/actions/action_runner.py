import argparse
import os
import sys
import time

import hjson

import lib
from lib import AssertFailed, ValidateFailed
from processor.actions import CommandAction


def tester_factory(actions, build_tool_name, checkout_dir, test_list, action_name):
    if actions["generator"] == "command":
        # build_tool_name, checkout_dir
        commands = []
        for c in actions["command"]:
            commands.append(
                f'docker run -v "{checkout_dir}":/workspace {build_tool_name} {c}'
            )

        for test_info in test_list:
            test_name = test_info["name"]
            tester = test_info["tester"]
            date = time.strftime('%Y%m%d_%H%M')
            if action_name.startswith("tester"):
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} mkdir -p result'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} mkdir -p result/{test_name}_{date}'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} sh -c "{tester} > result.txt"'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} '
                    f'cp result.txt result/{test_name}_{date}'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} rm result.txt'
                )
            if action_name == "tester-cov":
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} gcov {tester}'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} '
                    f'cp {test_name}.c.gcov result/{test_name}_{date}'
                )
                commands.append(
                    f'docker run -v "{checkout_dir}":/workspace {build_tool_name} '
                    f'rm {test_name}.c.gcov'
                )

        return CommandAction(commands)
    else:
        return None


class ActionRunner(object):
    def __init__(self, usage, action_name):
        self.usage = usage
        self.action_name = action_name

        self.parser = argparse.ArgumentParser(usage=self.usage)

        self.parser.add_argument("-p", "--project", required=True, help="specified project")
        self.parser.add_argument("-n", "--no", required=True, help="specified bug number")
        self.parser.add_argument(
            "-b", "--buggy", action="store_true", help="whether buggy version or not"
        )
        self.parser.add_argument("-t", "--target", required=True, help="checkout directory")
        self.parser.add_argument("-tl", "--test_list", required=False, nargs="+", help="test list")

    def run(self):
        args = self.parser.parse_args(sys.argv[2:])

        version = "buggy" if args.buggy else "fixed"

        # validation check
        project_dir = os.path.join(lib.io.DPP_HOME, "taxonomy", args.project)
        if not os.path.exists(project_dir):
            raise ValidateFailed

        if not os.path.exists(args.target):
            raise AssertFailed("checkout folder not exists")

        meta_file_path = os.path.join(project_dir, "meta.hjson")
        if not os.path.exists(meta_file_path):
            raise AssertFailed("File not exists: ", meta_file_path)

        with open(meta_file_path, "r", encoding="utf-8") as meta_file:
            meta = hjson.load(meta_file)

        if self.action_name in meta["defects"][str(args.no)][version]:
            actions = meta["defects"][str(args.no)][version][self.action_name]
            lib.io.kindness_message("%s procedure [DEFECT]" % self.action_name)
        else:
            actions = meta["common"][self.action_name]
            lib.io.kindness_message("%s procedure [COMMON]" % self.action_name)

        test_list = []
        if args.test_list:
            for test_name in args.test_list:
                for test_info in meta["defects"][str(args.no)][version]["test"]:
                    if test_name == test_info["name"]:
                        test_list.append(test_info)
                        lib.io.kindness_message("test %s for [DEFECT]" % test_name)
                        break

        builder = tester_factory(actions, args.project, args.target, test_list, self.action_name)
        return builder.run()

