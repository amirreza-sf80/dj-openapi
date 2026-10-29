import datetime

from cattrs.preconf.json import make_converter
from cattrs.preconf.pyyaml import make_converter as yaml_converter
from django.utils import formats

json_serializer = make_converter(omit_if_default=True)
yaml_serializer = yaml_converter(omit_if_default=True)


def time_structure(val, _t) -> datetime.time:
    if isinstance(val, datetime.time):
        return val
    for format in formats.get_format_lazy("TIME_INPUT_FORMATS"):
        try:
            return datetime.datetime.strptime(val, format).time()
        except (ValueError, TypeError):
            continue
    raise ValueError("Enter a valid time.")


def time_unstructure_str(val: datetime.time | None) -> str | None:
    if val is None:
        return None
    return val.isoformat()


json_serializer.register_structure_hook(datetime.time, time_structure)
json_serializer.register_unstructure_hook(datetime.time, time_unstructure_str)

yaml_serializer.register_structure_hook(datetime.time, time_structure)
yaml_serializer.register_unstructure_hook(datetime.time, time_unstructure_str)
