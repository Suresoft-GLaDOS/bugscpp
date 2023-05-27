from errors.common.exception import DppError


class DppDockerError(DppError):
    pass


class DppDockerBuildError(DppError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(
            f"{self.msg}\n"
            "Could not build image. Please open an issue at "
            "https://github.com/Suresoft-GLaDOS/bugscpp/issues\n"
        )


class DppDockerBuildClientError(DppError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(
            f"{self.msg}\n"
            "Could not build image (client error). Please open an issue at "
            "https://github.com/Suresoft-GLaDOS/bugscpp/issues\n"
        )


class DppDockerBuildServerError(DppError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(
            f"{self.msg}\n"
            "Could not build image (server error). Please open an issue at "
            "https://github.com/Suresoft-GLaDOS/bugscpp/issues\n"
        )


class DppDockerNoClientError(DppDockerError):
    def __init__(self):
        super().__init__(
            "Could not get response from docker. Is your docker-daemon running?"
        )
