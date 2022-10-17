import argparse
import json
import re
from pathlib import Path

from config import config
from processor.core.data import Worktree
from taxonomy import Taxonomy

PATH_TO_TEMPLATE = Path(__file__).parent / "vulcan.yml.template"


class Vulcan:
    name: str
    time_out: str
    test_build_command: str
    coverage_build_command: str
    test_list: str
    test_command: str
    test_coverage_command: str

    def __init__(self, worktree, name="", time_out="10", test_command="@testcase@", test_coverage_command="@testcase@"):
        self.worktree = worktree
        self.name = name if name else f"{worktree.project_name}_{worktree.suffix}"
        self.time_out = "10" if time_out is None else time_out
        self.taxonomy = Taxonomy()[worktree.project_name]
        self.test_build_command = self.get_build_command()
        self.coverage_build_command = self.get_coverage_build_command()
        self.test_list = self.get_test_list()
        self.test_command = test_command
        self.test_coverage_command = test_coverage_command

    def get_build_command(self):
        return "\n".join(self.taxonomy.common.build_command[0].lines)

    def get_coverage_build_command(self):
        return "\n".join(self.taxonomy.common.build_coverage_command[0].lines)

    def get_test_list(self):
        test_list = []
        for i in range(1, self.taxonomy.defects[self.worktree.index - 1].num_cases + 1):
            test_list.append(
                re.sub(r"\$\(cat .*DPP_TEST_INDEX\)", str(i), ";".join(self.taxonomy.common.test_command[0].lines)))
        for extra_test in self.taxonomy.defects[self.worktree.index - 1].extra_tests:
            test_list.append(";".join(extra_test[0].lines))
        return "\n".join(test_list)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="path to project")
    parser.add_argument("-n", "--name", type=str, default="")
    parser.add_argument("-o", "--output", type=str, default="",
                        help="path to output. automatically set to PATH_TO_PROJECT/vulcan.yml if not set")
    parser.add_argument("-j", "--jobs", type=int, help="number of jobs")
    return parser.parse_args()


def write_vulcan_yml(vulcan: Vulcan, output_path: Path):
    if not output_path:
        output_path = Path(vulcan.worktree.host) / "vulcan.yml"
    with open(PATH_TO_TEMPLATE, "r") as fp:
        template = fp.read()
    with open(output_path, "w") as fp:
        fp.write(template.format(**vulcan.__dict__))


if __name__ == "__main__":
    args = parse_args()
    config.DPP_PARALLEL_BUILD = str(args.jobs)
    dpp_config_path = Path(args.path) / ".defects4cpp.json"

    assert dpp_config_path.exists(), f"{dpp_config_path} does not exist. Did you checkout the project first?"

    with open(dpp_config_path, "r") as fp:
        data = json.load(fp)

    vulcan = Vulcan(Worktree(**data), name=args.name)

    write_vulcan_yml(vulcan, args.output)

    print(
        f"Vulcan yml file is generated at {args.output if args.output else Path(vulcan.worktree.host) / 'vulcan.yml'}"
    )
