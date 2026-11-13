"""The Valley inspection instance: its sites and the drive-time matrix the routing model reads.

The coordinates are invented from a seed (GridCap has none), so the matrix is fictional too.
"""

from valley import clock, drive_minutes, sites

places = sites(urgent_only=True)
print(f"{'node':>4}  {'site':6} {'x km':>5} {'y km':>5}  {'service':>7}  {'kits':>4}  window       cof $k")
for node, s in enumerate(places):
    print(f"{node:>4}  {s.name:6} {s.x:5.1f} {s.y:5.1f}  {s.service:>5} m  {s.kits:>4}  "
          f"{clock(s.window[0])}-{clock(s.window[1])}  {s.cof:>6}")

minutes = drive_minutes(places)
print()
print("drive minutes, row = from, column = to")
print("      " + "".join(f"{j:>4}" for j in range(len(places))))
for i, row in enumerate(minutes):
    print(f"  {i:>2}  " + "".join(f"{m:>4}" for m in row))
everything = sites()
print()
print(f"all Valley sites: {len(everything) - 1}, urgent: {sum(s.urgent for s in everything[1:])}, "
      f"kits needed: {sum(s.kits for s in everything)}, service minutes: {sum(s.service for s in everything)}")
