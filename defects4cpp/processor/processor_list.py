import processor

COMMAND_LIST = {
    # basic
    "help": {
        "function": processor.run_help,
        "group": "v1",
        "help": "Display help messages",
    },
    "show": {
        "function": processor.run_show,
        "group": "v1",
        "help": "Display defect taxonomies status",
    },
    "checkout": {
        "function": processor.run_checkout,
        "group": "v1",
        "help": "Get a specific defect snapshot",
    },
    "build": {
        "function": processor.run_build,
        "group": "v1",
        "help": "Build local with a build tool from docker",
    },
    "build-cov": {
        "function": processor.run_cov_build,
        "group": "v1",
        "help": "Coverage build local with a build tool from docker",
    },
    "test": {
        "function": processor.run_test,
        "group": "v1",
        "help": "Do test without coverage",
    },
    "test-cov": {
        "function": processor.run_cov_test,
        "group": "v1",
        "help": "Do test with coverage result",
    },
}
