"""
tests/test_differential.py: Diferansiyel Test ve Uyum Oranı Raporlayıcısı
"""

import csv
import os
import pytest
from src.engine import solve_a_priori, solve_post_hoc


class TestDifferentialGPower:
    """oracle/gpower_reference.csv üzerindeki birincil referans doğrulaması."""

    def test_gpower_reference_differential(self):
        ref_file = "oracle/gpower_reference.csv"
        assert os.path.exists(ref_file), f"{ref_file} bulunamadı!"

        total_tested = 0
        exact_n_matches = 0
        mismatches = []

        with open(ref_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_tested += 1
                vec_id = row["vector_id"]
                mode = row["mode"]
                tails = int(row["tails"])
                d = float(row["d"])
                alpha = float(row["alpha"])
                ratio = float(row["ratio"])

                expected_n1 = int(row["n1"])
                expected_n2 = int(row["n2"])
                expected_total = int(row["n_total"])
                expected_power = float(row["actual_power"])

                if mode == "a-priori":
                    power_input = float(row["power"])
                    res = solve_a_priori(tails=tails, d=d, alpha=alpha, power=power_input, ratio=ratio)
                else:
                    res = solve_post_hoc(tails=tails, d=d, alpha=alpha, n1=expected_n1, n2=expected_n2)

                n_match = (
                    res["n1"] == expected_n1 and
                    res["n2"] == expected_n2 and
                    res["n_total"] == expected_total
                )

                if n_match:
                    exact_n_matches += 1
                else:
                    mismatches.append({
                        "vector_id": vec_id,
                        "expected": (expected_n1, expected_n2, expected_total),
                        "actual": (res["n1"], res["n2"], res["n_total"])
                    })

                # Güç ve df kontrolü
                assert res["df"] == int(row["df"])
                assert abs(res["actual_power"] - expected_power) <= 0.005

        match_ratio = (exact_n_matches / total_tested) * 100.0
        print(f"\nG*Power Referans Doğrulaması:")
        print(f"Toplam Test: {total_tested}")
        print(f"Tam N Eşleşmesi: {exact_n_matches} (%{match_ratio:.2f})")

        if mismatches:
            print("Uyuşmazlıklar:", mismatches)

        # Kapı şartı: En az %90 tam N eşleşmesi
        assert match_ratio >= 90.0, f"Uyum oranı %90 eşiğinin altında: %{match_ratio:.2f}"


class TestDifferentialLibrary:
    """oracle/library_reference.csv (1536 vektör) üzerindeki geniş ölçekli test."""

    def test_library_reference_differential(self):
        lib_file = "oracle/library_reference.csv"
        assert os.path.exists(lib_file), f"{lib_file} bulunamadı!"

        total_tested = 0
        exact_n_matches = 0

        with open(lib_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_tested += 1
                tails = int(row["tails"])
                d = float(row["d"])
                alpha = float(row["alpha"])
                power = float(row["power"])
                ratio = float(row["ratio"])

                expected_n1 = int(row["n1"])
                expected_n2 = int(row["n2"])
                expected_total = int(row["n_total"])

                res = solve_a_priori(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)

                if (res["n1"] == expected_n1 and res["n2"] == expected_n2 and res["n_total"] == expected_total):
                    exact_n_matches += 1

        match_ratio = (exact_n_matches / total_tested) * 100.0
        print(f"\nBağımsız Kütüphane Diferansiyel Testi (1536 Vektör):")
        print(f"Toplam Test: {total_tested}")
        print(f"Tam N Eşleşmesi: {exact_n_matches} (%{match_ratio:.2f})")
        assert match_ratio >= 99.0
