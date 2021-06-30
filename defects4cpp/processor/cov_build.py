from processor.core.argparser import TaxonomyParser
from processor.core.command import DockerCommand


class CoverageBuildCommandParser(TaxonomyParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )


class CoverageBuildCommand(DockerCommand):
    def __init__(self):
        # action: "builder-cov",
        pass

    @property
    def help(self) -> str:
        return "Coverage build local with a build tool from docker"
