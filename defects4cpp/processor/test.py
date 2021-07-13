import argparse
from typing import List, Optional, Set

import message
import taxonomy
from processor.core.command import DockerCommand, DockerCommandArguments, TestCommandMixin


class ValidateCase(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        case == INCLUDE[:EXCLUDE]
          INCLUDE | EXCLUDE
          * select: ','
          * range:  '-'
        e.g.
          1-100:3,6,7 (to 100 from 1 except 3, 6 and 7)
          20-30,40-88:47-52 (to 30 from 20 and to 88 from 40 except to 62 from 47)
        """

        def select_cases(expr: str) -> Set[int]:
            if not expr:
                return set()
            cases: Set[int] = set()
            partitions = expr.split(",")
            for partition in partitions:
                tokens = partition.split("-")
                if len(tokens) == 1:
                    cases.add(int(tokens[0]))
                else:
                    cases.update(range(int(tokens[0]), int(tokens[1]) + 1))
            return cases

        values = values.split(":")
        included_cases = select_cases(values[0])
        excluded_cases = select_cases(values[1]) if len(values) > 1 else set()
        # TODO: the range must be validated by taxonomy lookup.
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class TestCommand(TestCommandMixin, DockerCommand):
    """
    Run test.
    """
    def __init__(self):
        super().__init__()
        self.parser.usage = "d++ test --project=[project_name] --no=[number] --case=[number] [checkout directory]"

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: taxonomy.MetaData = args.metadata

        message.info(f"Running {metadata.name} test")
        return self.generate_test_command(argv)

    def setup(self):
        pass

    def teardown(self):
        pass

    @property
    def help(self) -> str:
        return "Do test without coverage"
