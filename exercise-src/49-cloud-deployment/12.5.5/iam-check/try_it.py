"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from iam_check import allowed

BUCKET = "arn:aws:s3:::depot-plans-example"
policy = {
    "Statement": [
        {"Effect": "Allow", "Action": "s3:GetObject", "Resource": f"{BUCKET}/inputs/*"},
        {"Effect": "Allow", "Action": ["s3:PutObject"], "Resource": [f"{BUCKET}/plans/R-??/*"]},
        {"Effect": "Deny", "Action": "s3:Put*", "Resource": f"{BUCKET}/plans/R-00/*"},
    ],
}

print("GetObject inputs/day1.csv:", allowed(policy, "s3:GetObject", f"{BUCKET}/inputs/day1.csv"))
print("s3:getobject inputs/day1.csv:", allowed(policy, "s3:getobject", f"{BUCKET}/inputs/day1.csv"))
print("GetObject Inputs/day1.csv:", allowed(policy, "s3:GetObject", f"{BUCKET}/Inputs/day1.csv"))
print("PutObject plans/R-12/p.json:", allowed(policy, "s3:PutObject", f"{BUCKET}/plans/R-12/p.json"))
print("PutObject plans/R-123/p.json:", allowed(policy, "s3:PutObject", f"{BUCKET}/plans/R-123/p.json"))
print("PutObject plans/R-00/p.json:", allowed(policy, "s3:PutObject", f"{BUCKET}/plans/R-00/p.json"))
