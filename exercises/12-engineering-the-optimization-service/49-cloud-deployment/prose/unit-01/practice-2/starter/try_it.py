"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from dockerfile_review import review

tidy = """
FROM python:3.13.2-slim AS deps
RUN pip install --prefix=/deps -r requirements.txt
FROM python:3.13.2-slim
COPY --from=deps /deps /usr/local
USER planner
ENTRYPOINT ["python", "-m", "scheduler"]
"""
sloppy = """
FROM ubuntu:latest
ARG DB_PASSWORD=hunter2
USER planner
ENTRYPOINT python -m scheduler
"""

print("tidy file:", review(tidy))
print("sloppy file:", review(sloppy))
print("tidy file without USER:", review(tidy.replace("USER planner\n", "")))
