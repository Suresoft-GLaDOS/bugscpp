from typing import List

from processor.core.argparser import TaxonomyArguments, TaxonomyParser
from processor.core.command import DockerCommand, DockerCommandArguments
from taxonomy import MetaData


class BuildCommandParser(TaxonomyParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )


class BuildCommand(DockerCommand):
    parser = BuildCommandParser()

    def __init__(self):
        pass

    def run(
        self, metadata: MetaData, index: int, buggy: bool
    ) -> DockerCommandArguments:
        try:
            defect = metadata.defects[index]
        except IndexError:
            # TODO: exception handling is required
            return DockerCommandArguments([])
        if buggy:
            pass

        return DockerCommandArguments([])

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"

    #     if buggy:
    #         defect.buggy_checkout_command
    #         defect.buggy_checkout_generator
    #     else:
    #         defect.fixed_checkout_command
    #         defect.fixed_checkout_generator

    #     # if self.action_name in meta["defects"][str(args.no)][version]:
    #     #     actions = meta["defects"][str(args.no)][version][self.action_name]
    #     #     kindness_message("%s procedure [DEFECT]" % self.action_name)
    #     # else:
    #     #     actions = meta["common"][self.action_name]
    #     #     kindness_message("%s procedure [COMMON]" % self.action_name)

    #     # builder = tester_factory(actions, args.project, args.checkout)
    #     # for c in self._commands:
    #     #     pass
    #     #     print("RUN: ", c)
    #     #     if subprocess.call(c) != 0:
    #     #         return False
    #     return True


def tester_factory(actions, build_tool_name, checkout_dir):
    if actions["generator"] == "command":
        # build_tool_name, checkout_dir
        commands = []
        for c in actions["command"]:
            commands.append(
                f'docker run -v "{checkout_dir}":/workspace {build_tool_name} {c}'
            )
        return SimpleCommand(commands)
    else:
        return None
