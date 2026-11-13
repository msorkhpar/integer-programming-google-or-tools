A distribution company prices the failure of each feeder before it ranks renewals. A failure
interrupts every customer on the feeder. Crews then switch a share `switch_share` of them to a
neighbouring feeder after `switch_hours`; the rest wait for the repair, `repair_hours`. The
switched share is the same for both customer classes. Customers come in two classes: `residential`
customers cost `residential_cost` ($k per customer-hour) and `critical` ones (clinics, water
pumping) cost `critical_cost`. The crew and parts cost `repair_cost` ($k).

Write two functions in `feeders.py`:

- `consequence(f)`: the cost of one failure of feeder `f`, in $k;
- `saidi_minutes(f, customers_served)`: how many minutes one failure adds to the company's SAIDI,
  where `customers_served` is every customer of the company.

Write each as a formula first: the average hours a customer of this feeder is out, then the
interruption cost of each class, then the sum. With $`s`$ the switched share, the average hours out
are $`s \cdot \text{switch\_hours} + (1 - s) \cdot \text{repair\_hours}`$: the switched customers
wait for the switching, the others for the repair. Lesson 7.3.3 has the one-class, one-step version.
About eight lines.
