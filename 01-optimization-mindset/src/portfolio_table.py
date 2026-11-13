"""Print the tiny GridCap portfolio: the eight projects a planner chooses from."""

from gridcap import Portfolio, generate


def rules_of(project) -> str:
    rules = []
    if project.must_do:
        rules.append("must-do")
    if project.parent:
        rules.append(f"needs {project.parent}")
    if project.alt_group:
        rules.append(f"alternative in {project.alt_group}")
    return ", ".join(rules)


def show(portfolio: Portfolio) -> None:
    print(f"capital budget: ${portfolio.capital_budget:,}k")
    print(f"{'id':5} {'program':13} {'capex $k':>9} {'NPV $k':>7}  rules")
    for p in portfolio.projects:
        print(f"{p.project_id:5} {p.program:13} {p.capex:>9,} {p.value:>7,}  {rules_of(p)}")
    print(f"all eight: ${sum(p.capex for p in portfolio.projects):,}k")


if __name__ == "__main__":
    show(generate("tiny"))
