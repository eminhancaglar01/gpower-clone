"""
tests/test_mcp.py: MCP Sunucusu ve CLI Çıktı Eşdeğerlik Testleri
"""

import json
import pytest
import asyncio
from src.mcp_server import mcp_server, t2_indep_a_priori_tool, t2_indep_post_hoc_tool, calculate_power_tool
from src.cli import run_cli


@pytest.mark.asyncio
async def test_mcp_tool_listing():
    """MCP sunucusunun araçları doğru şema ile listelediğini doğrular."""
    tools = await mcp_server.list_tools()
    tool_names = [t.name for t in tools]
    assert "t2_indep_a_priori" in tool_names
    assert "t2_indep_post_hoc" in tool_names
    assert "calculate_power" in tool_names


@pytest.mark.parametrize("tails,d,alpha,power,ratio", [
    (2, 0.5, 0.05, 0.95, 1.0),
    (1, 0.5, 0.05, 0.95, 1.0),
    (2, 0.2, 0.05, 0.80, 1.0),
    (2, 0.8, 0.01, 0.95, 2.0),
])
def test_mcp_and_cli_parity_a_priori(tails, d, alpha, power, ratio, monkeypatch, capsys):
    """CLI ile MCP'nin aynı a priori girdisinde aynı JSON çıktısını ürettiğini doğrular."""
    # 1. MCP üzerinden çağrı
    mcp_res = calculate_power_tool(
        test="t2-indep",
        mode="a-priori",
        tails=tails,
        d=d,
        alpha=alpha,
        power=power,
        ratio=ratio
    )

    # 2. CLI üzerinden çağrı
    args = [
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", str(tails),
        "--d", str(d),
        "--alpha", str(alpha),
        "--power", str(power),
        "--ratio", str(ratio)
    ]
    exit_code = run_cli(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    cli_res = json.loads(captured.out.strip())

    # Değerlerin birebir eşleşmesi
    assert mcp_res["n1"] == cli_res["n1"]
    assert mcp_res["n2"] == cli_res["n2"]
    assert mcp_res["n_total"] == cli_res["n_total"]
    assert mcp_res["actual_power"] == cli_res["actual_power"]
    assert mcp_res["critical"] == cli_res["critical"]
    assert mcp_res["df"] == cli_res["df"]
    assert mcp_res["ncp"] == cli_res["ncp"]


def test_mcp_error_propagation():
    """Hatalı girdilerin MCP katmanında açıkça hata olarak aktarılması."""
    # Desteklenmeyen test
    res = calculate_power_tool(test="anova", mode="a-priori", tails=2, d=0.5, alpha=0.05, power=0.95)
    assert "error" in res
    assert "Desteklenmeyen test" in res["error"]

    # Power <= alpha
    res2 = t2_indep_a_priori_tool(tails=2, d=0.5, alpha=0.05, power=0.04)
    assert "error" in res2
    assert "büyük olmalıdır" in res2["error"]
