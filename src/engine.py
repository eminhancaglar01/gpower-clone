"""
src/engine.py: İstatistiksel Hesaplama Motoru (Statistical Power Engine)

G*Power 3.1.9.7 programının iki bağımsız grup t testi (t2-indep) davranışını
bağımsız ve temiz oda prensipleriyle yeniden gerçekleştiren matematiksel motor.

Test Ailesi: t tests -> Means: Difference between two independent means (two groups)
"""

import math
from typing import Dict, Any, Optional
import scipy.stats as stats


class ValidationError(ValueError):
    """Girdi parametresi doğrulama hatası."""
    pass


class CalculationError(RuntimeError):
    """Sayısal hesaplama ve yakınsama hatası."""
    pass


def validate_parameters(
    tails: int,
    d: float,
    alpha: float,
    power: Optional[float] = None,
    ratio: Optional[float] = None,
    n1: Optional[int] = None,
    n2: Optional[int] = None,
    mode: str = "a-priori"
) -> None:
    """
    Hesaplama motoru girdi parametrelerini doğrular.
    Geçersiz durumlarda açıklayıcı ValidationError fırlatır.
    """
    # Tails doğrulama
    if tails not in (1, 2):
        raise ValidationError("tails parametresi yalnızca 1 veya 2 olabilir.")

    # Etki büyüklüğü (d)
    if not isinstance(d, (int, float)) or math.isnan(d) or math.isinf(d) or d <= 0:
        raise ValidationError("Etki büyüklüğü (d) pozitif bir sayı olmalıdır (d > 0).")

    # Anlamlılık düzeyi (alpha)
    if not isinstance(alpha, (int, float)) or math.isnan(alpha) or math.isinf(alpha) or alpha <= 0 or alpha >= 1:
        raise ValidationError("Anlamlılık düzeyi (alpha) 0 ile 1 arasında olmalıdır (0 < alpha < 1).")

    if mode == "a-priori":
        if power is None or not isinstance(power, (int, float)) or math.isnan(power) or math.isinf(power) or power <= 0 or power >= 1:
            raise ValidationError("Hedef güç (power) 0 ile 1 arasında olmalıdır (0 < power < 1).")
        
        if power <= alpha:
            raise ValidationError(
                f"Hedef güç ({power}), anlamlılık düzeyi ({alpha})'dan büyük olmalıdır (power > alpha)."
            )

        if ratio is None or not isinstance(ratio, (int, float)) or math.isnan(ratio) or math.isinf(ratio) or ratio <= 0:
            raise ValidationError("Grup oranı (ratio = n2/n1) pozitif bir sayı olmalıdır (ratio > 0).")

    elif mode == "post-hoc":
        if n1 is None or not isinstance(n1, int) or n1 < 2:
            raise ValidationError("Post hoc analizi için n1 en az 2 olmalıdır (n1 >= 2).")
        if n2 is None or not isinstance(n2, int) or n2 < 2:
            raise ValidationError("Post hoc analizi için n2 en az 2 olmalıdır (n2 >= 2).")
    else:
        raise ValidationError(f"Desteklenmeyen mod: '{mode}'. Yalnızca 'a-priori' veya 'post-hoc' desteklenir.")


def compute_df(n1: int, n2: int) -> int:
    """
    İki bağımsız grup t testi için serbestlik derecesi (degrees of freedom).
    df = n1 + n2 - 2
    """
    return int(n1 + n2 - 2)


def compute_ncp(d: float, n1: int, n2: int) -> float:
    """
    Noncentrality parameter (ncp, delta):
    delta = d / sqrt(1/n1 + 1/n2) = d * sqrt((n1 * n2) / (n1 + n2))
    """
    if n1 <= 0 or n2 <= 0:
        raise ValidationError("Örneklem büyüklükleri n1 ve n2 pozitif olmalıdır.")
    harmonic_factor = math.sqrt((n1 * n2) / (n1 + n2))
    return float(d * harmonic_factor)


def compute_critical_t(alpha: float, df: int, tails: int) -> float:
    """
    Verilen alfa, serbestlik derecesi ve kuyruk sayısına göre kritik t değeri.
    - tails = 2: t.ppf(1 - alpha/2, df)
    - tails = 1: t.ppf(1 - alpha, df)
    """
    if df < 1:
        raise ValidationError(f"Serbestlik derecesi (df) en az 1 olmalıdır, alınan: {df}")

    if tails == 2:
        return float(stats.t.ppf(1.0 - alpha / 2.0, df))
    elif tails == 1:
        return float(stats.t.ppf(1.0 - alpha, df))
    else:
        raise ValidationError("tails parametresi yalnızca 1 veya 2 olabilir.")


def compute_power(tails: int, d: float, alpha: float, n1: int, n2: int) -> float:
    """
    Verilen parametreler ve grup büyüklükleri altında gerçekleşen istatistiksel güç (actual power).
    Noncentral Student t dağılımı kullanılarak hesaplanır.
    """
    df = compute_df(n1, n2)
    ncp = compute_ncp(d, n1, n2)
    tcrit = compute_critical_t(alpha, df, tails)

    if tails == 2:
        # İki taraflı: Sağ kuyruk P(T > tcrit) + Sol kuyruk P(T < -tcrit)
        power_upper = 1.0 - stats.nct.cdf(tcrit, df, ncp)
        power_lower = stats.nct.cdf(-tcrit, df, ncp)
        calc_power = float(power_upper + power_lower)
    else:
        # Tek taraflı (üst kuyruk / beklenen yönde d > 0): P(T > tcrit)
        calc_power = float(1.0 - stats.nct.cdf(tcrit, df, ncp))

    # Sayısal sınır kontrolü [0.0, 1.0]
    return max(0.0, min(1.0, calc_power))


def solve_a_priori(
    tails: int,
    d: float,
    alpha: float,
    power: float,
    ratio: float = 1.0
) -> Dict[str, Any]:
    """
    A priori güç analizi:
    Belirlenen hedef güç, alfa, etki büyüklüğü ve grup oranına göre
    gerekli en küçük tamsayı örneklem büyüklüğünü (n1, n2, n_total) hesaplar.
    
    Dönüş sözlüğü:
    {
        "n1": int,
        "n2": int,
        "n_total": int,
        "actual_power": float,
        "critical": float,
        "df": int,
        "ncp": float
    }
    """
    validate_parameters(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio, mode="a-priori")

    # Grup tahsis fonksiyonu: n1 bilindiğinde n2'yi belirler
    def get_n2(n_1: int) -> int:
        return max(2, math.ceil(ratio * n_1))

    # 1. Aşama: Üst sınır belirleme (Eksponansiyel arama)
    low_n1 = 2
    high_n1 = 4
    while True:
        n2_test = get_n2(high_n1)
        curr_power = compute_power(tails, d, alpha, high_n1, n2_test)
        if curr_power >= power:
            break
        low_n1 = high_n1
        high_n1 *= 2
        if high_n1 > 10_000_000:
            raise CalculationError("Örneklem büyüklüğü araması sınır değerleri aştı (N > 10,000,000).")

    # 2. Aşama: İkili arama (Binary search) ile minimal n1 aralığını daraltma
    ans_n1 = high_n1
    while low_n1 <= high_n1:
        mid_n1 = (low_n1 + high_n1) // 2
        mid_n2 = get_n2(mid_n1)
        mid_power = compute_power(tails, d, alpha, mid_n1, mid_n2)
        if mid_power >= power:
            ans_n1 = mid_n1
            high_n1 = mid_n1 - 1
        else:
            low_n1 = mid_n1 + 1

    # 3. Aşama: Doğrulama ve minimal tamsayı kontrolü
    final_n1 = ans_n1
    final_n2 = get_n2(final_n1)
    actual_power = compute_power(tails, d, alpha, final_n1, final_n2)

    # Bir kişi azaltıldığında hedef gücün karşılanmadığını doğrula
    if final_n1 > 2:
        prev_n1 = final_n1 - 1
        prev_n2 = get_n2(prev_n1)
        prev_power = compute_power(tails, d, alpha, prev_n1, prev_n2)
        if prev_power >= power:
            # Tolerans güvenliği için n1'i bir basamak geri çek
            final_n1 = prev_n1
            final_n2 = prev_n2
            actual_power = prev_power

    df = compute_df(final_n1, final_n2)
    ncp = compute_ncp(d, final_n1, final_n2)
    critical_t = compute_critical_t(alpha, df, tails)

    return {
        "n1": int(final_n1),
        "n2": int(final_n2),
        "n_total": int(final_n1 + final_n2),
        "actual_power": round(actual_power, 4),
        "critical": round(critical_t, 4),
        "df": int(df),
        "ncp": round(ncp, 4)
    }


def solve_post_hoc(
    tails: int,
    d: float,
    alpha: float,
    n1: Optional[int] = None,
    n2: Optional[int] = None,
    ratio: Optional[float] = None,
    n_total: Optional[int] = None
) -> Dict[str, Any]:
    """
    Post hoc güç analizi:
    Verilen örneklem büyüklüğü, alfa, etki büyüklüğü ve grup oranına göre
    gerçekleşen istatistiksel gücü (actual power) hesaplar.
    
    Parametre seçenekleri:
    - n1 ve n2 doğrudan verilebilir.
    - Ya da n_total ve ratio verilebilir (n1 = round(n_total / (1 + ratio)), n2 = n_total - n1).
    """
    if n1 is None or n2 is None:
        if n_total is not None and ratio is not None:
            if n_total < 4:
                raise ValidationError("Post hoc analizi için n_total en az 4 olmalıdır.")
            if ratio <= 0:
                raise ValidationError("Grup oranı (ratio) pozitif olmalıdır.")
            calc_n1 = max(2, round(n_total / (1.0 + ratio)))
            calc_n2 = n_total - calc_n1
            if calc_n2 < 2:
                calc_n2 = 2
                calc_n1 = n_total - 2
            n1 = calc_n1
            n2 = calc_n2
        else:
            raise ValidationError(
                "Post hoc analizi için ya (n1 ve n2) ya da (n_total ve ratio) parametreleri verilmelidir."
            )

    validate_parameters(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2, mode="post-hoc")

    df = compute_df(n1, n2)
    ncp = compute_ncp(d, n1, n2)
    critical_t = compute_critical_t(alpha, df, tails)
    actual_power = compute_power(tails, d, alpha, n1, n2)

    return {
        "n1": int(n1),
        "n2": int(n2),
        "n_total": int(n1 + n2),
        "actual_power": round(actual_power, 4),
        "critical": round(critical_t, 4),
        "df": int(df),
        "ncp": round(ncp, 4)
    }
