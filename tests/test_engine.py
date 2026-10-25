"""
tests/test_engine.py: Hesaplama Motoru Birim ve Tutarlılık Testleri
"""

import pytest
import math
from src.engine import (
    solve_a_priori,
    solve_post_hoc,
    compute_power,
    compute_df,
    compute_ncp,
    compute_critical_t,
    ValidationError,
    CalculationError
)


class TestEngineMath:
    """Temel matematiksel fonksiyonların doğrulanması."""

    def test_compute_df(self):
        assert compute_df(105, 105) == 208
        assert compute_df(88, 88) == 174
        assert compute_df(2, 2) == 2

    def test_compute_ncp(self):
        # d=0.5, n1=105, n2=105 -> ncp ≈ 3.6228
        ncp = compute_ncp(0.5, 105, 105)
        assert round(ncp, 4) == 3.6228

    def test_compute_critical_t_two_tailed(self):
        # alpha=0.05, df=208, tails=2 -> tcrit ≈ 1.9714
        tcrit = compute_critical_t(0.05, 208, tails=2)
        assert round(tcrit, 4) == 1.9714

    def test_compute_critical_t_one_tailed(self):
        # alpha=0.05, df=174, tails=1 -> tcrit ≈ 1.6537
        tcrit = compute_critical_t(0.05, 174, tails=1)
        assert round(tcrit, 4) == 1.6537


class TestAPriori:
    """A priori modu birim testleri."""

    def test_reference_example_two_tailed(self):
        """Ödev belgesindeki ana referans örnek."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1.0)
        assert res["n1"] == 105
        assert res["n2"] == 105
        assert res["n_total"] == 210
        assert res["df"] == 208
        assert res["ncp"] == 3.6228
        assert res["critical"] == 1.9714
        assert res["actual_power"] == 0.9501

    def test_gpower_manual_example_one_tailed(self):
        """G*Power resmi kılavuzunun 4. sayfasındaki tek taraflı örnek."""
        res = solve_a_priori(tails=1, d=0.5, alpha=0.05, power=0.95, ratio=1.0)
        assert res["n1"] == 88
        assert res["n2"] == 88
        assert res["n_total"] == 176
        assert res["df"] == 174
        assert res["critical"] == 1.6537
        assert res["ncp"] == 3.3166
        assert res["actual_power"] >= 0.95

    def test_minimal_sample_size_condition(self):
        """Bulunan N'den 1 kişi azaltıldığında gücün hedefin altına düştüğünü doğrula."""
        d, alpha, target_power = 0.5, 0.05, 0.95
        res = solve_a_priori(tails=2, d=d, alpha=alpha, power=target_power, ratio=1.0)
        n1 = res["n1"]
        # n1 ile güç >= target_power
        assert compute_power(2, d, alpha, n1, n1) >= target_power
        # n1 - 1 ile güç < target_power
        assert compute_power(2, d, alpha, n1 - 1, n1 - 1) < target_power

    def test_unequal_ratio_a_priori(self):
        """Eşit olmayan oran (ratio = 2.0)."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.90, ratio=2.0)
        assert res["n1"] > 0
        assert res["n2"] == math.ceil(2.0 * res["n1"])
        assert res["n_total"] == res["n1"] + res["n2"]
        assert res["actual_power"] >= 0.90

    def test_ratio_less_than_one(self):
        """Oranın 1'den küçük olduğu durum (ratio = 0.5)."""
        res = solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=0.5)
        assert res["n1"] > res["n2"]
        assert res["n2"] >= 2
        assert res["actual_power"] >= 0.80


class TestPostHoc:
    """Post hoc modu birim testleri."""

    def test_post_hoc_direct_n1_n2(self):
        res = solve_post_hoc(tails=2, d=0.5, alpha=0.05, n1=105, n2=105)
        assert res["n1"] == 105
        assert res["n2"] == 105
        assert res["n_total"] == 210
        assert res["actual_power"] == 0.9501
        assert res["critical"] == 1.9714
        assert res["df"] == 208
        assert res["ncp"] == 3.6228

    def test_post_hoc_total_and_ratio(self):
        res = solve_post_hoc(tails=2, d=0.5, alpha=0.05, n_total=210, ratio=1.0)
        assert res["n1"] == 105
        assert res["n2"] == 105
        assert res["actual_power"] == 0.9501


class TestConsistency:
    """A priori ve Post hoc tutarlılık testleri."""

    @pytest.mark.parametrize("tails", [1, 2])
    @pytest.mark.parametrize("d", [0.2, 0.5, 0.8])
    @pytest.mark.parametrize("alpha", [0.01, 0.05])
    @pytest.mark.parametrize("power", [0.80, 0.90, 0.95])
    def test_a_priori_and_post_hoc_roundtrip(self, tails, d, alpha, power):
        """A priori ile bulunan n1 ve n2, post hoc'a verildiğinde aynı veya daha yüksek güç vermelidir."""
        ap = solve_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=1.0)
        ph = solve_post_hoc(tails=tails, d=d, alpha=alpha, n1=ap["n1"], n2=ap["n2"])
        assert ph["actual_power"] == ap["actual_power"]
        assert ph["df"] == ap["df"]
        assert ph["critical"] == ap["critical"]
        assert ph["ncp"] == ap["ncp"]
        assert ph["actual_power"] >= power


class TestInputValidations:
    """Geçersiz girdi parametreleri doğrulama testleri."""

    def test_invalid_tails(self):
        with pytest.raises(ValidationError, match="tails"):
            solve_a_priori(tails=3, d=0.5, alpha=0.05, power=0.95)

    def test_negative_d(self):
        with pytest.raises(ValidationError, match="Etki büyüklüğü"):
            solve_a_priori(tails=2, d=-0.5, alpha=0.05, power=0.95)

    def test_zero_d(self):
        with pytest.raises(ValidationError, match="Etki büyüklüğü"):
            solve_a_priori(tails=2, d=0.0, alpha=0.05, power=0.95)

    def test_alpha_out_of_bounds(self):
        with pytest.raises(ValidationError, match="alpha"):
            solve_a_priori(tails=2, d=0.5, alpha=1.0, power=0.95)
        with pytest.raises(ValidationError, match="alpha"):
            solve_a_priori(tails=2, d=0.5, alpha=0.0, power=0.95)
        with pytest.raises(ValidationError, match="alpha"):
            solve_a_priori(tails=2, d=0.5, alpha=-0.05, power=0.95)

    def test_power_lte_alpha(self):
        with pytest.raises(ValidationError, match="büyük olmalıdır"):
            solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.04)
        with pytest.raises(ValidationError, match="büyük olmalıdır"):
            solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.05)

    def test_negative_ratio(self):
        with pytest.raises(ValidationError, match="ratio"):
            solve_a_priori(tails=2, d=0.5, alpha=0.05, power=0.95, ratio=-1.0)

    def test_post_hoc_insufficient_sample_size(self):
        with pytest.raises(ValidationError, match="n1"):
            solve_post_hoc(tails=2, d=0.5, alpha=0.05, n1=1, n2=10)
        with pytest.raises(ValidationError, match="n2"):
            solve_post_hoc(tails=2, d=0.5, alpha=0.05, n1=10, n2=1)
