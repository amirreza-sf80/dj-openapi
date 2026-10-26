from django.core.management.base import BaseCommand

from dj_openapi.attrs.structure import json_converter, yaml_converter
from dj_openapi.discover import make_openapi_spec
from dj_openapi.settings import JSON_DUMP_PATH, YAML_DUMP_PATH


class Command(BaseCommand):
    help = "Dumps projects OpenAPI docs to a file."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", help="output as json")
        parser.add_argument("--yaml", action="store_true", help="output as yaml")

    def handle(self, *args, **kwargs):
        yaml_format = kwargs.get("yaml", False)
        json_format = kwargs.get("json", False) or not yaml_format

        if json_format:
            json_dump = json_converter.dumps(make_openapi_spec())
            with open(JSON_DUMP_PATH, "w") as f:
                f.write(json_dump)

        if yaml_format:
            yaml_dump = yaml_converter.dumps(
                yaml_converter.unstructure(make_openapi_spec())
            )
            with open(YAML_DUMP_PATH, "w") as f:
                f.write(yaml_dump)
