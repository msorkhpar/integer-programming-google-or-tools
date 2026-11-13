"""Tune on a few instances, then test on instances the tuner never saw: how much of the gain survives?"""

from grb_runs import quiet_env
from tuner import SHIFT, Tunable, configurations, label, pick, score, tuning_set

env = quiet_env()
plans = {pf.name: Tunable(env, pf) for pf in tuning_set()}
configs = configurations()
names = list(plans)
train = [n for n in names if n.endswith("-2027")]                  # one portfolio's four regions
test = [n for n in names if n not in train]
print(f"{len(configs)} configurations x {len(names)} regional plans; train on {len(train)} ({', '.join(train)}),")
print(f"test on the other {len(test)}")

table = {(n, 1, label(c)): plans[n].work(1, c) for n in names for c in configs}
default: dict = {}


def ratio(config: dict, where: list[str], seed: int = 1) -> float:
    return score(table, where, config, seed) / score(table, where, default, seed)


chosen = pick(table, train, configs)
ranked = sorted(configs, key=lambda c: score(table, train, c))
print("\nbest five on the training set (SGM of work to proof, as a ratio to the default):")
for c in ranked[:5]:
    print(f"  {label(c):<36} train {ratio(c, train):.2f}   test {ratio(c, test):.2f}")

on_test = sorted(configs, key=lambda c: score(table, test, c))
print(f"\nthe tuner's choice, {label(chosen)}: train {ratio(chosen, train):.2f}, test {ratio(chosen, test):.2f}, "
      f"rank {on_test.index(chosen) + 1} of {len(configs)} on the test set")
print(f"the best on the test set, in hindsight: {label(on_test[0])}, test {ratio(on_test[0], test):.2f}")
wins = sum(table[n, 1, label(chosen)] < table[n, 1, "default"] for n in test)
losses = sum(table[n, 1, label(chosen)] > table[n, 1, "default"] for n in test)
print(f"on the {len(test)} test plans the choice needs less work than the default on {wins}, more on {losses}")

print("\ntuned on one training plan alone:")
for n in train:
    alone = pick(table, [n], configs)
    print(f"  {n:<12} {label(alone):<36} that plan {ratio(alone, [n]):.2f}   test {ratio(alone, test):.2f}")

for seed in (2, 3):
    for c in (default, chosen):
        for n in train:
            table[n, seed, label(c)] = plans[n].work(seed, c)
print("\nthe choice re-measured on the training plans with other seeds:")
for seed in (1, 2, 3):
    print(f"  seed {seed}: train {ratio(chosen, train, seed):.2f}" + ("   (the seed it was tuned with)" if seed == 1 else ""))
print(f"(shift {SHIFT:g}, work in thousandths of a Gurobi work unit; below 1 is less work than the default)")
