from processor.core.argparser import TaxonomyParser
from processor.core.command import DockerCommand


class TestCommandParser(TaxonomyParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [checkout directory]"
        )


class TestCommand(DockerCommand):
    def __init__(self):
        pass

    @property
    def help(self) -> str:
        return "Do test without coverage"
