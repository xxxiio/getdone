#pragma once

#include <numeric>
#include <vector>

inline double mean_or_zero(const std::vector<double>& values) {
    if (values.empty()) {
        return 0.0;
    }
    const double total = std::accumulate(values.begin(), values.end(), 0.0);
    return total / static_cast<double>(values.size());
}
