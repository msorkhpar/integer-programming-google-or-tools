"""Lesson 4.8.3: where crew 1's arrival range at A087 (08:56-10:10) comes from.

Solves valley_windows.py's model with inspection time, then reads the range's two ends from both
sides of A087: from the yard before it and from A230 after it. Each side gives an earliest and a
latest arrival; the range is where they overlap. The drive times are fictional.
"""

from valley import clock
from valley_windows import MAX_WAIT, build, minutes, places

manager, routing, solution = build(count_service=True)
time_dim = routing.GetDimensionOrDie("Time")
names = [p.name for p in places]
yard, a087, a230 = 0, names.index("A087"), names.index("A230")


def arrival(node: int) -> tuple[int, int]:
    cumul = time_dim.CumulVar(manager.NodeToIndex(node))
    return solution.Min(cumul), solution.Max(cumul)


start = time_dim.CumulVar(routing.Start(1))
leave = (solution.Min(start), solution.Max(start))
reach_a230 = arrival(a230)
to_a087, after_a087 = minutes[yard][a087], places[a087].service + minutes[a087][a230]
print(f"crew 1 leaves the yard {clock(leave[0])}-{clock(leave[1])}, drives {to_a087} min to A087, "
      f"may wait at most {MAX_WAIT} min at a stop")
print(f"  from the yard: A087 between {clock(leave[0] + to_a087)} and {clock(leave[1] + to_a087 + MAX_WAIT)}")
print(f"A230 is reached {clock(reach_a230[0])}-{clock(reach_a230[1])}; A087 takes {places[a087].service} min "
      f"of inspection and {minutes[a087][a230]} of driving before it")
print(f"  from A230: A087 between {clock(reach_a230[0] - after_a087 - MAX_WAIT)} and {clock(reach_a230[1] - after_a087)}")
print(f"solver's range at A087: {clock(arrival(a087)[0])}-{clock(arrival(a087)[1])}")
