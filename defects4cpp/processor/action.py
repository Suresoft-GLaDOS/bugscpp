from defects4cpp.processor.core.command import RegisterCommand


class Action:
    def __init__(self):
        for command, command_type in RegisterCommand.commands.items():
            # print(f"{command=}: {command_type=}")
            setattr(self, command, command_type())


def run_internal(action):
    pass
    # try:
    #     action_runner = ActionRunner(
    #         "",
    #         action,
    #     )
    #     succeed = action_runner.run()

    #     if not succeed:
    #         raise AssertFailed("Test Failed")
    #     else:
    #         kindness_message("Completed")

    # except ValidateFailed:
    #     error_message("invalid arguments, check project name or bug numbers")
    # except AssertFailed as e:
    #     error_message(e)
    # except SystemExit:
    #     pass
    # except:
    #     error_message(get_trace_back())


def run_internal(action):
    pass
    # try:
    #     action_runner = ActionRunner(
    #         "",
    #         action,
    #     )
    #     succeed = action_runner.run()

    #     if not succeed:
    #         raise AssertFailed("Test Failed")
    #     else:
    #         kindness_message("Completed")

    # except ValidateFailed:
    #     error_message("invalid arguments, check project name or bug numbers")
    # except AssertFailed as e:
    #     error_message(e)
    # except SystemExit:
    #     pass
    # except:
    #     error_message(get_trace_back())
