from processor.core.argparser import TaxonomyParser
from processor.core.command import DockerCommand


class CoverageTestCommandParser(TaxonomyParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [checkout directory]"
        )


class CoverageTestCommand(DockerCommand):
    def __init__(self):
        # action: "tester-cov"
        pass

    @property
    def help(self) -> str:
        return "Do test with coverage result"
