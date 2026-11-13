from dockerfile_review import review

GOOD = """
FROM python:3.14.7-slim AS build
RUN pip install --prefix=/install -r requirements.txt
FROM python:3.14.7-slim
COPY --from=build /install /usr/local
USER solver
CMD ["python", "-m", "roster"]
"""

BAD = """
FROM python
ENV API_TOKEN=abc123
CMD python -m roster
"""


def test_a_clean_file_has_no_findings_and_a_bad_one_has_all_four():
    assert review(GOOD) == []
    assert review(BAD) == ["base-not-pinned", "runs-as-root", "secret-in-env", "shell-form-cmd"]


def test_latest_is_not_a_pin_but_a_digest_is():
    assert review(GOOD.replace("FROM python:3.14.7-slim\n", "FROM python:latest\n")) == ["base-not-pinned"]
    pinned = "FROM python@sha256:" + "ab" * 32 + "\n"
    assert review(GOOD.replace("FROM python:3.14.7-slim\n", pinned)) == []


def test_a_registry_port_is_not_a_tag():
    image = "FROM registry.example.invalid:5000/python\n"
    assert review(GOOD.replace("FROM python:3.14.7-slim\n", image)) == ["base-not-pinned"]


def test_scratch_is_the_empty_image_not_an_unpinned_base():
    text = GOOD.replace("FROM python:3.14.7-slim\n", "FROM scratch\n")
    assert review(text.replace("USER solver\n", "")) == ["runs-as-root"]
    assert review(text) == []


def test_a_user_in_an_earlier_stage_does_not_carry_over():
    text = GOOD.replace("USER solver\n", "").replace("RUN pip", "USER builder\nRUN pip")
    assert review(text) == ["runs-as-root"]


def test_user_root_or_0_still_runs_as_root():
    assert review(GOOD.replace("USER solver", "USER 0")) == ["runs-as-root"]
    assert review(GOOD.replace("USER solver", "USER root:root")) == ["runs-as-root"]


def test_a_secret_hidden_among_other_variables_is_found():
    text = GOOD.replace("USER solver", "ENV MODE=prod db_password=x LEVEL=2\nUSER solver")
    assert review(text) == ["secret-in-env"]


def test_lowercase_instructions_and_entrypoint_count():
    text = GOOD.replace('CMD ["python", "-m", "roster"]', "entrypoint python -m roster")
    assert review(text) == ["shell-form-cmd"]
