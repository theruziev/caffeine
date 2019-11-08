from jinja2 import Environment, FileSystemLoader


class Templater:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.env = Environment(
            loader=FileSystemLoader(self.template_path), enable_async=True, autoescape=True
        )

    async def load(self, template_name: str, params: dict) -> str:
        template = self.env.get_template(template_name)
        return await template.render_async(params)
