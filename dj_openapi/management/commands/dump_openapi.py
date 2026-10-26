from django.core.management import CommandError
from django.core.management.base import BaseCommand

from dj_openapi.attrs.structure import json_serializer, yaml_serializer
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
            if not json_serializer:
                raise CommandError(
                    "json serializer is not configured, please set DJANGO_OPENAPI_JSON_SERIALIZER"
                )

            json_dump = json_serializer.dumps(make_openapi_spec())
            with open(JSON_DUMP_PATH, "w") as f:
                f.write(json_dump)

        if yaml_format:
            if not yaml_serializer:
                raise CommandError(
                    "yaml serializer is not configured, please set DJANGO_OPENAPI_YAML_SERIALIZER"
                )
            yaml_dump = yaml_serializer.dumps(make_openapi_spec())
            with open(YAML_DUMP_PATH, "w") as f:
                f.write(yaml_dump)
