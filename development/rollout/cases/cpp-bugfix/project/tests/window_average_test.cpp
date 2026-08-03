#include "window_average.hpp"

#include <cmath>
#include <iostream>
#include <vector>

int main() {
    if (std::abs(mean_or_zero({2.0, 4.0, 6.0}) - 4.0) > 1e-12) {
        std::cerr << "non-empty mean is incorrect\n";
        return 1;
    }
    if (mean_or_zero({}) != 0.0) {
        std::cerr << "empty input must return zero\n";
        return 1;
    }
    return 0;
}
