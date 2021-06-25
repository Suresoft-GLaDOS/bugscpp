from defects4cpp.processor.core.argparser import BuildParser
from defects4cpp.processor.core.command import SimpleBuildCommand


class CoverageBuildCommandParser(BuildParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )


class CoverageBuildCommand(SimpleBuildCommand):
    def __init__(self):
        # action: "builder-cov",
        pass

    @property
    def help(self) -> str:
        return "Coverage build local with a build tool from docker"
