"""
src/mcp_server.py: gpower-clone Model Context Protocol (MCP) Sunucusu

Yapay zeka ajanlarının ve LLM'lerin G*Power hesaplama motorunu
standart araç çağrıları (Tool Call) üzerinden kullanabilmesini sağlar.
Hesaplama mantığını tekrar etmez; doğrudan src.engine modülünü çağırır.
"""

from typing import Optional, Dict, Any
from mcp.server.mcpserver import MCPServer
from .engine import solve_a_priori, solve_post_hoc, ValidationError, CalculationError

# MCP Sunucu örneği
mcp_server = MCPServer(
    name="gpower-clone-mcp",
    version="1.0.0",
    description="G*Power İki Bağımsız Grup t Testi (t2-indep) Güç Analizi MCP Sunucusu"
)


@mcp_server.tool(name="t2_indep_a_priori")
def t2_indep_a_priori_tool(
    tails: int,
    d: float,
    alpha: float,
    power: float,
    ratio: float = 1.0
) -> Dict[str, Any]:
    """
    İki bağımsız grup t testi (t2-indep) için A priori örneklem büyüklüğü hesabı.
    
    Args:
        tails: Kuyruk sayısı (1: tek taraflı, 2: iki taraflı)
        d: Cohen's d etki büyüklüğü (d > 0)
        alpha: I. tip hata payı (örn. 0.05)
        power: Hedef istatistiksel güç (örn. 0.95)
        ratio: İkinci grubun birinci gruba oranı N2/N1 (varsayılan: 1.0)
        
    Returns:
        dict: n1, n2, n_total, actual_power, critical, df, ncp
    """
    try:
        return solve_a_priori(
            tails=tails,
            d=d,
            alpha=alpha,
            power=power,
            ratio=ratio
        )
    except (ValidationError, CalculationError) as err:
        return {"error": str(err)}


@mcp_server.tool(name="t2_indep_post_hoc")
def t2_indep_post_hoc_tool(
    tails: int,
    d: float,
    alpha: float,
    n1: Optional[int] = None,
    n2: Optional[int] = None,
    ratio: Optional[float] = None,
    n_total: Optional[int] = None
) -> Dict[str, Any]:
    """
    İki bağımsız grup t testi (t2-indep) için Post hoc gerçekleşen güç hesabı.
    
    Args:
        tails: Kuyruk sayısı (1: tek taraflı, 2: iki taraflı)
        d: Cohen's d etki büyüklüğü (d > 0)
        alpha: I. tip hata payı (örn. 0.05)
        n1: 1. grup örneklem büyüklüğü (isteğe bağlı)
        n2: 2. grup örneklem büyüklüğü (isteğe bağlı)
        ratio: N2/N1 oranı (n_total kullanılıyorsa)
        n_total: Toplam örneklem büyüklüğü (n1 ve n2 yerine kullanılabilir)
        
    Returns:
        dict: n1, n2, n_total, actual_power, critical, df, ncp
    """
    try:
        return solve_post_hoc(
            tails=tails,
            d=d,
            alpha=alpha,
            n1=n1,
            n2=n2,
            ratio=ratio,
            n_total=n_total
        )
    except (ValidationError, CalculationError) as err:
        return {"error": str(err)}


@mcp_server.tool(name="calculate_power")
def calculate_power_tool(
    test: str,
    mode: str,
    tails: int,
    d: float,
    alpha: float,
    power: Optional[float] = None,
    ratio: float = 1.0,
    n1: Optional[int] = None,
    n2: Optional[int] = None,
    n_total: Optional[int] = None
) -> Dict[str, Any]:
    """
    CLI ile birebir aynı parametre şemasına sahip birleşik güç analizi aracı.
    
    Args:
        test: 't2-indep'
        mode: 'a-priori' veya 'post-hoc'
        tails: 1 veya 2
        d: Cohen's d (> 0)
        alpha: Anlamlılık düzeyi (0 < alpha < 1)
        power: Hedef güç (a-priori için)
        ratio: N2/N1 oranı (varsayılan: 1.0)
        n1: Grup 1 büyüklüğü (post-hoc için)
        n2: Grup 2 büyüklüğü (post-hoc için)
        n_total: Toplam büyüklük (post-hoc için)
    """
    if test != "t2-indep":
        return {"error": f"Desteklenmeyen test ailesi: '{test}'. Yalnızca 't2-indep' desteklenmektedir."}

    mode_clean = mode.lower()
    if mode_clean == "a-priori":
        if power is None:
            return {"error": "A priori modu için power parametresi zorunludur."}
        return t2_indep_a_priori_tool(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)
    elif mode_clean == "post-hoc":
        return t2_indep_post_hoc_tool(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2, ratio=ratio, n_total=n_total)
    else:
        return {"error": f"Geçersiz mod: '{mode}'. Yalnızca 'a-priori' veya 'post-hoc' desteklenmektedir."}


def main():
    """MCP sunucusunu stdio taşıyıcısıyla başlatır."""
    import sys
    mcp_server.run()


if __name__ == "__main__":
    main()
