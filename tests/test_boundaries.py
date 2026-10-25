"""
tests/test_boundaries.py: Sınır Değerler ve Uç Nokta Testleri (Boundary & Edge Cases)
"""

import pytest
from src.engine import solve_a_priori, solve_post_hoc, compute_power, ValidationError


class TestBoundaries:
    """Uç ve sınır değer davranışlarının testi."""

    def test_very_small_effect_size(self):
        """Çok küçük etki büyüklüğü: d = 0.05 (örneklem büyüklüğü çok artmalı, kararlı çalışmalı)."""
        res = solve_a_priori(tails=2, d=0.05, alpha=0.05, power=0.80, ratio=1.0)
        assert res["n1"] > 5000
        assert res["n2"] > 5000
        assert res["actual_power"] >= 0.80
        assert res["df"] == res["n_total"] - 2

    def test_very_large_effect_size(self):
        """Çok büyük etki büyüklüğü: d = 3.0 (örneklem alt sınır df >= 1'e takılmalı)."""
        res = solve_a_priori(tails=2, d=3.0, alpha=0.05, power=0.95, ratio=1.0)
        assert res["n1"] >= 2
        assert res["n2"] >= 2
        assert res["df"] >= 2
        assert res["actual_power"] >= 0.95

    def test_very_small_alpha(self):
        """Çok küçük alfa: alpha = 0.001 (aşırı katı anlamlılık düzeyi)."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.001, power=0.95, ratio=1.0)
        assert res["critical"] > 3.0
        assert res["n1"] > 105
        assert res["actual_power"] >= 0.95

    def test_very_high_power(self):
        """Çok yüksek hedef güç: power = 0.999."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.999, ratio=1.0)
        assert res["n1"] > 150
        assert res["actual_power"] >= 0.999

    def test_extreme_high_allocation_ratio(self):
        """Büyük tahsis oranı: ratio = 5.0 (2. grup 1. grubun 5 katı)."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=5.0)
        assert res["n2"] >= res["n1"] * 5
        assert res["actual_power"] >= 0.80

    def test_extreme_low_allocation_ratio(self):
        """Küçük tahsis oranı: ratio = 0.2 (2. grup 1. grubun beşte biri)."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.2)
        assert res["n1"] > res["n2"]
        assert res["n2"] >= 2
        assert res["actual_power"] >= 0.80

    def test_monotonicity_of_power_with_sample_size(self):
        """Örneklem büyüklüğü arttıkça gücün kesinlikle monoton artması gerekir."""
        powers = []
        for n in range(5, 50, 5):
            p = compute_power(tails=2, d=0.5, alpha=0.05, n1=n, n2=n)
            powers.append(p)
        # Her adım bir öncekinden büyük olmalı
        for i in range(len(powers) - 1):
            assert powers[i + 1] > powers[i]
