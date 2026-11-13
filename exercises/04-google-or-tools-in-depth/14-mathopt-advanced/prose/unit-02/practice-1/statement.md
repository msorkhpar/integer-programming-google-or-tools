A hospital builds next month's nurse rota with a MIP. The ward manager ranks three goals, strictly:

1. leave as few shifts uncovered as possible;
2. among rotas that do that, use as few overtime hours as possible;
3. among those, honor as many of the nurses' shift preferences as possible.

The model in `rota.py` already has the three goals as linear expressions, `uncovered`, `overtime`
and `preferences`. Write `set_objectives(model, uncovered, overtime, preferences)` so the model
holds the ranking as MathOpt's prioritized objectives:

```math
\begin{aligned}
&\text{priority 0 (primary):} && \min \; \text{uncovered} \\
&\text{priority 1:} && \min \; \text{overtime} && \text{(name: overtime)} \\
&\text{priority 2:} && \max \; \text{preferences} && \text{(name: preferences)}
\end{aligned}
```

Nothing is solved: no solver in the course's runner accepts auxiliary objectives (lesson 4.3.2). The
tests read the objectives back from the model, both auxiliary ones included, so mind what lesson
4.3.2 found about adding a second auxiliary objective in OR-Tools 9.15. About eight lines.
