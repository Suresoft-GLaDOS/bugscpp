import subprocess
from abc import ABCMeta, abstractmethod, abstractproperty
from typing import List

from defects4cpp.processor.core.argparser import BuildParser, ParserBase
from defects4cpp.taxonomy import MetaData


class RegisterCommand(type):
    commands = {}

    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)
        m = attrs["__module__"]
        if m != __name__:
            RegisterCommand.commands[m.split(".")[-1]] = new_class
        return new_class


class CommandMeta(RegisterCommand, ABCMeta):
    pass


class Command(metaclass=CommandMeta):
    @abstractproperty
    def group(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def help(self) -> str:
        raise NotImplementedError


class SimpleCommand(Command):
    @property
    def group(self) -> str:
        return "v1"

    @abstractmethod
    def run(self) -> bool:
        raise NotImplementedError

    def __call__(self) -> bool:
        return self.run()


class SimpleBuildCommand(Command):
    # def __init__(self, action_name, parser: ParserBase):
    #     self.action_name = action_name
    #     self.parser = parser
    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        return self.run(*self.parser(argv))

    @abstractmethod
    def run(self, metadata: MetaData, index: int, buggy=True) -> bool:
        raise NotImplementedError

    @abstractproperty
    def parser(self) -> BuildParser:
        raise NotImplementedError

    # def run(self, metadata: MetaData, index: int, buggy=True):
    #     try:
    #         defect = metadata.defects[index]
    #     except IndexError:
    #         # TODO:
    #         raise IndexError("")

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
