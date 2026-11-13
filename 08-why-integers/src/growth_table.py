"""Polynomial against exponential growth: n^2, n^3 and 2^n for growing n."""

if __name__ == "__main__":
    print(f"{'n':>5}{'n^2':>12}{'n^3':>12}{'2^n':>12}")
    for n in (10, 20, 40, 100, 400):
        print(f"{n:>5}{n ** 2:>12.2e}{n ** 3:>12.2e}{2 ** n:>12.2e}")
