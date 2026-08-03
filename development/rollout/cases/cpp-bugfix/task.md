# Task

Fix the regression in `mean_or_zero`: an empty input must return `0.0` without producing a
NaN or undefined downstream behaviour. Add no dependency and preserve non-empty results.
