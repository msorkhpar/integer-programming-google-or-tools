A gas utility chooses which leak sensors to install from a short list of at most twenty, and breaks
ties between equally good choices with a small bonus $`\varepsilon \sum_i w_i x_i`$. For the bonus
to pick exactly one choice, no two different selections may have the same total weight; and for the
choice to repeat, the weights must be the same in every run.

Write `separating_weights(ids)`. It returns a dict giving each sensor id a positive integer weight
such that every two different selections of ids have different totals. The weights must not depend
on the order of `ids` or on the Python process. Use the powers of two the lesson describes, in
sorted id order: the first id gets 1, the next 2, then 4, and so on up to $`2^{n-1}`$ for $`n`$ ids.
(Other separating weights exist, some with a smaller largest weight, such as 3, 5, 6 and 7 for four
ids; the tests accept any that separate every selection and keep the largest weight at most
$`2^{n-1}`$.)

About two lines.
