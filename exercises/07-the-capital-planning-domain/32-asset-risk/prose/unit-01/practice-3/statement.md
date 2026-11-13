A transmission company is fitting a Weibull curve to the history of one kind of transformer
bushing. For each bushing that failed it knows the age at failure; for each bushing still in
service it knows only its age today. The fitting routine maximizes a log-likelihood over
`beta` and `eta`, and you are writing that function.

Write `log_likelihood(beta, eta, failed, working)` in `likelihood.py`: `failed` is the list of
failure ages, `working` the list of current ages of the bushings still in service, all in years.

Write the formula in the lesson's notation first, a sum over failed units and a sum over units
still working, then expand $`\ln f(t)`$ and $`\ln R(c)`$ for the Weibull so that you need only
`math.log` and powers. The tests compare your value with `scipy.stats.weibull_min`'s `logpdf` and
`logsf`. About six lines.
