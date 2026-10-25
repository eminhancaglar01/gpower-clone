"""
tests/test_cli.py: gpower-clone Komut Satırı Arayüzü (CLI) Entegrasyon Testleri
"""

import json
import subprocess
import sys
import pytest
from src.cli import run_cli


def run_cli_subprocess(args):
    """Subprocess ile CLI'yi doğrudan çalıştırır."""
    cmd = [sys.executable, "-m", "src.cli"] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()


class TestCLIContract:
    """CLI sözleşmesi ve JSON çıktı testleri."""

    def test_mandatory_reference_call(self):
        """Ödev belgesinde zorunlu tutulan örnek çağrı."""
        args = [
            "--test", "t2-indep",
            "--mode", "a-priori",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--power", "0.95",
            "--ratio", "1"
        ]
        ret, stdout, stderr = run_cli_subprocess(args)
        assert ret == 0
        assert stderr == ""
        # Çıktı tam tek satır olmalı
        assert "\n" not in stdout
        data = json.loads(stdout)
        assert data["n1"] == 105
        assert data["n2"] == 105
        assert data["n_total"] == 210
        assert data["actual_power"] == 0.9501
        assert data["critical"] == 1.9714
        assert data["df"] == 208
        assert data["ncp"] == 3.6228

    def test_post_hoc_cli_call(self):
        """Post hoc modu CLI çağrısı."""
        args = [
            "--test", "t2-indep",
            "--mode", "post-hoc",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--n1", "105",
            "--n2", "105"
        ]
        ret, stdout, stderr = run_cli_subprocess(args)
        assert ret == 0
        data = json.loads(stdout)
        assert data["actual_power"] == 0.9501
        assert data["n_total"] == 210

    def test_post_hoc_total_and_ratio_cli(self):
        """Post hoc modunda n-total ve ratio kullanımı."""
        args = [
            "--test", "t2-indep",
            "--mode", "post-hoc",
            "--tails", "2",
            "--d", "0.5",
            "--alpha", "0.05",
            "--n-total", "210",
            "--ratio", "1"
        ]
        ret, stdout, stderr = run_cli_subprocess(args)
        assert ret == 0
        data = json.loads(stdout)
        assert data["n1"] == 105
        assert data["n2"] == 105
        assert data["actual_power"] == 0.9501


class TestCLIErrors:
    """Geçersiz veya hatalı çağrılarda hata sözleşmesi testleri."""

    def test_missing_test_parameter(self):
        args = ["--mode", "a-priori", "--tails", "2", "--d", "0.5", "--alpha", "0.05", "--power", "0.95"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret != 0
        data = json.loads(stdout)
        assert "error" in data
        assert "Eksik parametre" in data["error"]

    def test_unsupported_test_family(self):
        args = ["--test", "anova-oneway", "--mode", "a-priori", "--tails", "2", "--d", "0.5", "--alpha", "0.05", "--power", "0.95"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret != 0
        data = json.loads(stdout)
        assert "error" in data
        assert "Desteklenmeyen test ailesi" in data["error"]

    def test_missing_power_in_a_priori(self):
        args = ["--test", "t2-indep", "--mode", "a-priori", "--tails", "2", "--d", "0.5", "--alpha", "0.05"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret != 0
        data = json.loads(stdout)
        assert "error" in data
        assert "--power" in data["error"]

    def test_invalid_tails_value(self):
        args = ["--test", "t2-indep", "--mode", "a-priori", "--tails", "3", "--d", "0.5", "--alpha", "0.05", "--power", "0.95"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret != 0
        data = json.loads(stdout)
        assert "error" in data
        assert "tails" in data["error"]

    def test_unexpected_flags(self):
        args = ["--test", "t2-indep", "--mode", "a-priori", "--tails", "2", "--d", "0.5", "--alpha", "0.05", "--power", "0.95", "--foo", "bar"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret != 0
        data = json.loads(stdout)
        assert "error" in data
        assert "Bilinmeyen" in data["error"]

    def test_help_flag_json(self):
        args = ["--help"]
        ret, stdout, _ = run_cli_subprocess(args)
        assert ret == 0
        data = json.loads(stdout)
        assert data["name"] == "gpower-clone"
        assert "supported_tests" in data
