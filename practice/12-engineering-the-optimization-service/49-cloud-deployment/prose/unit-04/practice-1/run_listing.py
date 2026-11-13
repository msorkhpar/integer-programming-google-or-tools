from __future__ import annotations


def runs_of(s3, bucket: str, survey_id: str) -> list[str]:
    """The run ids with a result under trim-results/<survey_id>/, sorted as text."""
    # TODO: list every key under the survey's prefix, on every page, and keep the run ids.
    return []
