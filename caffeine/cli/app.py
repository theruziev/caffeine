import click


class CliApp(click.Group):
    def __init__(self):
        super(CliApp, self).__init__()

    def list_commands(self, ctx):
        return super().list_commands(ctx)
