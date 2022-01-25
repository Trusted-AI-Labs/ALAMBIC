from typing import List, Any, Dict

from alambic_app.models.results import Result


def get_results() -> List[Dict[str, Any]]:
    return list(Result.objects.values())

# check charts amcharts4
