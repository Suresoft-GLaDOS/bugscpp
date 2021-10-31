from errors.common.exception import DppError


class DppDockerError(DppError):
    pass


class DppDockerNoClientError(DppDockerError):
    def __init__(self):
        super().__init__(
            "Could not get response from docker. Is your docker-daemon running?"
        )
