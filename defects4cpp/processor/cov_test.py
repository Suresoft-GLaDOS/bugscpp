from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand


class CoverageTestCommand(DockerCommand):
    def __init__(self):
        # action: "tester-cov"
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [checkout directory]"
        )

    @property
    def help(self) -> str:
        return "Do test with coverage result"
