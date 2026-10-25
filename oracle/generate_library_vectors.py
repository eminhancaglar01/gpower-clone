"""
oracle/generate_library_vectors.py: Bağımsız Kütüphane Referans Vektör Üreticisi

R pwr ve Python statsmodels / scipy teorisine dayalı olarak 500'den fazla
büyük ölçekli test vektörü üretir ve oracle/library_reference.csv dosyasına kaydeder.
"""

import csv
import os
import math
import scipy.stats as stats
import statsmodels.stats.power as smp


def generate_library_vectors(output_path: str = "oracle/library_reference.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    tails_list = [1, 2]
    d_list = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20]
    alpha_list = [0.01, 0.025, 0.05, 0.10]
    power_list = [0.80, 0.85, 0.90, 0.95]
    ratio_list = [0.5, 1.0, 1.5, 2.0]
    
    fieldnames = [
        "vector_id", "tails", "d", "alpha", "power", "ratio",
        "n1", "n2", "n_total", "actual_power", "critical", "df", "ncp",
        "library_source"
    ]
    
    rows = []
    vec_idx = 1
    
    for tails in tails_list:
        for d in d_list:
            for alpha in alpha_list:
                for target_power in power_list:
                    for ratio in ratio_list:
                        # n1 arama mantığı (ceiling kuralı)
                        def get_n2(n1_val):
                            return max(2, math.ceil(ratio * n1_val))
                        
                        # İkili arama ile en küçük tamsayı n1
                        low = 2
                        high = 4
                        while True:
                            df_t = high + get_n2(high) - 2
                            ncp_t = d * math.sqrt((high * get_n2(high)) / (high + get_n2(high)))
                            tcrit_t = stats.t.ppf(1 - alpha / (2 if tails == 2 else 1), df_t)
                            if tails == 2:
                                p_t = (1 - stats.nct.cdf(tcrit_t, df_t, ncp_t)) + stats.nct.cdf(-tcrit_t, df_t, ncp_t)
                            else:
                                p_t = 1 - stats.nct.cdf(tcrit_t, df_t, ncp_t)
                            if p_t >= target_power:
                                break
                            high *= 2
                        
                        ans = high
                        while low <= high:
                            mid = (low + high) // 2
                            df_m = mid + get_n2(mid) - 2
                            ncp_m = d * math.sqrt((mid * get_n2(mid)) / (mid + get_n2(mid)))
                            tcrit_m = stats.t.ppf(1 - alpha / (2 if tails == 2 else 1), df_m)
                            if tails == 2:
                                p_m = (1 - stats.nct.cdf(tcrit_m, df_m, ncp_m)) + stats.nct.cdf(-tcrit_m, df_m, ncp_m)
                            else:
                                p_m = 1 - stats.nct.cdf(tcrit_m, df_m, ncp_m)
                            if p_m >= target_power:
                                ans = mid
                                high = mid - 1
                            else:
                                low = mid + 1
                        
                        n1 = ans
                        n2 = get_n2(n1)
                        df = n1 + n2 - 2
                        ncp = d * math.sqrt((n1 * n2) / (n1 + n2))
                        tcrit = stats.t.ppf(1 - alpha / (2 if tails == 2 else 1), df)
                        if tails == 2:
                            act_p = (1 - stats.nct.cdf(tcrit, df, ncp)) + stats.nct.cdf(-tcrit, df, ncp)
                        else:
                            act_p = 1 - stats.nct.cdf(tcrit, df, ncp)
                        
                        rows.append({
                            "vector_id": f"LIB-{vec_idx:04d}",
                            "tails": tails,
                            "d": d,
                            "alpha": alpha,
                            "power": target_power,
                            "ratio": ratio,
                            "n1": n1,
                            "n2": n2,
                            "n_total": n1 + n2,
                            "actual_power": round(act_p, 4),
                            "critical": round(tcrit, 4),
                            "df": df,
                            "ncp": round(ncp, 4),
                            "library_source": "SciPy/Statsmodels Grid Generation"
                        })
                        vec_idx += 1
                        
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Toplam {len(rows)} bağımsız kütüphane vektörü başarıyla yazıldı -> {output_path}")


if __name__ == "__main__":
    generate_library_vectors()
