from __future__ import annotations


def runs_of(s3, bucket: str, survey_id: str) -> list[str]:
    """The run ids with a result under trim-results/<survey_id>/, sorted as text."""
    prefix = f"trim-results/{survey_id}/"
    runs = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            name = obj["Key"][len(prefix):]
            if name.endswith(".json") and "/" not in name:
                runs.append(name.removesuffix(".json"))
    return sorted(runs)
