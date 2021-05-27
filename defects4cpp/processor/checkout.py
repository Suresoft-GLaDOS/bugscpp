import os
import lib
import sys
import argparse
import subprocess
import hjson

# Exceptions
class ValidataionFailed(Exception): pass
class AssertFailed(Exception): pass

class AbstractAction():
    def run(self):
        pass


class CommandAction(AbstractAction):
    def __init__(self, commands):
        self._COMMANDS = commands

    def run(self):
        for c in self._COMMANDS:
            print("RUN: ", c)
            if subprocess.call(c) != 0:
                return False
        return True


def checkout_factory(checkout_info):
    if checkout_info['generator'] == 'command':
        return CommandAction(checkout_info['command'])
    else:
        return None


def run_checkout():
    try:
        parser = argparse.ArgumentParser(usage="d++ checkout --project=[project_name] --no=[number]")
        # lib.io.kindness_message("HOME = %s" % lib.io.DPP_HOME)

        parser.add_argument("-p", "--project", required=True, help="specified project")
        parser.add_argument("-n", "--no", required=True, help="specified bug number")
        parser.add_argument("-b", "--buggy", action="store_true", help="checkout buggy version")
        parser.add_argument("-t", "--target", default=None)
        args = parser.parse_args(sys.argv[2:])

        version = 'buggy' if args.buggy else 'fixed'
        # validation check
        project_dir = os.path.join(lib.io.DPP_HOME, 'taxonomy', args.project)
        if not os.path.exists(project_dir):
            raise ValidataionFailed

        if args.target is not None:
            target_dir = args.target
        else:
            target_dir = os.path.join(os.getcwd(), "%s_%s_%s" % (args.project, args.no, version))
        lib.io.kindness_message("checkout current directory = %s" % target_dir)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        os.chdir(project_dir)
        # do checkout
        # 1. build docker image
        build = f'docker build -t "{args.project}" .'
        print(build)
        if subprocess.call(build) != 0:
            raise AssertFailed("docker is not working properly: ", build)

        meta_file_path = os.path.join(project_dir, "meta.hjson")
        if not os.path.exists(meta_file_path):
            raise AssertFailed("File not exists: ", meta_file_path)

        with open(meta_file_path, "r", encoding='utf-8') as meta_file:
            meta = hjson.load(meta_file)

        action = 'checkout'
        version_checkout_info = meta['defects'][str(args.no)][version][action]
        from_command = meta['from']

        checkout = checkout_factory(version_checkout_info)

        # from
        os.chdir(target_dir)
        cloned = os.path.exists(os.path.join(target_dir, '.git'))
        if not cloned and subprocess.call(from_command) != 0:
            raise AssertFailed("Cloning Failed")

        succeed = checkout.run()

        if not succeed:
            raise AssertFailed("Checkout Failed")

        # 2. connect to target_dir to docker image
        # commands = [['git', 'clone', 'https://github.com/libsndfile/libsndfile.git']]
        # for c in commands:
        #     run = f'docker run -v "{target_dir}":/workspace {args.project} "{c}"'
        #     print(run)

    except ValidataionFailed:
        lib.io.error_message("invalid arguments, check project name or bug numbers")
    except AssertFailed as e:
        lib.io.error_message(e)
    except:
        lib.io.error_message(lib.get_trace_back())
        pass
