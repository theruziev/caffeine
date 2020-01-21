import click

from caffeine.cli.commands.email import send_email

COMMANDS = [send_email]


class CLIApp(click.Group):
    AVAILABLE_COMMANDS = COMMANDS

    def __init__(self):
        super(CLIApp, self).__init__()
        for cmd in self.AVAILABLE_COMMANDS:
            self.add_command(cmd)
