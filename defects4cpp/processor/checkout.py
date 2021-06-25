from defects4cpp.processor.core.command import SimpleCommand


def checkout_factory(checkout_info, build_tool_name, checkout_dir):
    if checkout_info["generator"] == "command":
        commands = []
        for c in checkout_info["command"]:
            commands.append(
                f'docker run -v "{checkout_dir}":/workspace {build_tool_name} {c}'
            )
        # return CommandAction(commands)
    else:
        return None


def run_checkout():
    pass
    # try:
    #     parser = argparse.ArgumentParser(
    #         usage="d++ checkout --project=[project_name] --no=[number]"
    #     )
    #     # lib.io.kindness_message("HOME = %s" % lib.io.DPP_HOME)

    #     parser.add_argument("-p", "--project", required=True, help="specified project")
    #     parser.add_argument("-n", "--no", required=True, help="specified bug number")
    #     parser.add_argument(
    #         "-b", "--buggy", action="store_true", help="checkout buggy version"
    #     )
    #     parser.add_argument("-t", "--target", default=None)
    #     args = parser.parse_args(sys.argv[2:])

    #     version = "buggy" if args.buggy else "fixed"
    #     # validation check
    #     project_dir = os.path.join(DPP_HOME, "taxonomy", args.project)
    #     if not os.path.exists(project_dir):
    #         raise ValidateFailed

    #     if args.target is not None:
    #         target_dir = args.target
    #     else:
    #         target_dir = os.path.join(
    #             os.getcwd(), "%s_%s_%s" % (args.project, args.no, version)
    #         )
    #     kindness_message("checkout current directory = %s" % target_dir)

    #     if not os.path.exists(target_dir):
    #         os.makedirs(target_dir)

    #     os.chdir(project_dir)
    #     # do checkout
    #     # 1. build docker image
    #     build = f'docker build -t "{args.project}" .'
    #     print(build)
    #     if subprocess.call(build) != 0:
    #         raise AssertFailed("docker is not working properly: ", build)

    #     meta_file_path = os.path.join(project_dir, "meta.hjson")
    #     if not os.path.exists(meta_file_path):
    #         raise AssertFailed("File not exists: ", meta_file_path)

    #     with open(meta_file_path, "r", encoding="utf-8") as meta_file:
    #         meta = hjson.load(meta_file)

    #     action = "checkout"
    #     version_checkout_info = meta["defects"][str(args.no)][version][action]
    #     from_command = meta["from"]
    #     from_command = (
    #         f'docker run -v "{target_dir}":/workspace {args.project} {from_command}'
    #     )
    #     print(from_command)
    #     checkout = checkout_factory(version_checkout_info, args.project, target_dir)

    #     # from
    #     os.chdir(target_dir)
    #     cloned = os.path.exists(os.path.join(target_dir, ".git"))
    #     if not cloned and subprocess.call(from_command) != 0:
    #         raise AssertFailed("Cloning Failed")

    #     succeed = checkout.run()

    #     if not succeed:
    #         raise AssertFailed("Checkout Failed")
    #     else:
    #         kindness_message("Completed")

    # except ValidateFailed:
    #     error_message("invalid arguments, check project name or bug numbers")
    # except AssertFailed as e:
    #     error_message(e)
    # except:
    #     error_message(get_trace_back())


class CheckoutCommandParser:
    pass


class CheckoutCommand(SimpleCommand):
    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
