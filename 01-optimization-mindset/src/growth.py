"""How long brute force takes as the portfolio grows, at a million plans a second."""


def brute_force_years(n: int, plans_per_second: float = 1e6) -> float:
    return 2 ** n / plans_per_second / (365 * 24 * 3600)


if __name__ == "__main__":
    for n in (8, 20, 40, 60, 400):
        print(f"{n:>3} projects: {2 ** n:.2e} plans, {brute_force_years(n):.2e} years")
