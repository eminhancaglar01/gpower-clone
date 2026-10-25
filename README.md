# gpower-clone

**YZM301 — Teardown Sprint: G*Power Davranışını Yeniden Gerçekleyen Proje**

> ⚠️ **Yasal Uyarı:** Bu proje, G*Power 3.1.9.7 yazılımının istatistiksel güç analizi hesaplama davranışını **eğitim amaçlı** tersine mühendislik ilkeleriyle yeniden gerçekleştirmeyi amaçlar. Kaynak kod alınmamış, decompile edilmemiş, ticari kopya üretilmemiştir. Tüm matematiksel formüller halka açık akademik yayınlara (Faul et al., 2007; Cohen, 1988) ve G*Power resmi kılavuzuna dayanmaktadır.

---

## Proje Özeti

| Özellik | Değer |
|---|---|
| Test Ailesi | `t tests` → İki Bağımsız Grup Ortalama Farkı |
| CLI Komutu | `gpower-clone` |
| Desteklenen Modlar | `a-priori`, `post-hoc` |
| Referans Yazılım | G*Power 3.1.9.7 (Windows, x86 PE) |
| Dil / Platform | Python 3.13, SciPy, pytest |
| Test Sonucu | **80/80 PASSED** |
| Referans Vektör Uyumu | 29 G*Power + 1524 kütüphane vektörü |

---

## Kurulum

```bash
# 1. Sanal ortam oluştur ve aktifleştir
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # Linux/Mac

# 2. Bağımlılıkları yükle
pip install -e .

# 3. Testleri çalıştır
pytest tests/ -v
```

---

## Kullanım

### A Priori Modu (Örneklem Büyüklüğü Hesaplama)

```bash
gpower-clone --test t2-indep --mode a-priori \
             --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1.0
```

**Çıktı (tek satır JSON):**
```json
{"n1": 105, "n2": 105, "n_total": 210, "actual_power": 0.9501, "critical": 1.9714, "df": 208, "ncp": 3.6228}
```

### Post Hoc Modu (Gerçekleşen Güç Hesaplama)

```bash
gpower-clone --test t2-indep --mode post-hoc \
             --tails 2 --d 0.5 --alpha 0.05 --n1 105 --n2 105
```

**Çıktı:**
```json
{"n1": 105, "n2": 105, "n_total": 210, "actual_power": 0.9501, "critical": 1.9714, "df": 208, "ncp": 3.6228}
```

### Hata Çıktısı

```json
{"error": "Etki büyüklüğü (d) pozitif bir sayı olmalıdır (d > 0)."}
```

---

## Parametre Referansı

| Parametre | Açıklama | Geçerli Değerler |
|---|---|---|
| `--test` | Test ailesi | `t2-indep` |
| `--mode` | Analiz modu | `a-priori`, `post-hoc` |
| `--tails` | Kuyruk sayısı | `1`, `2` |
| `--d` | Cohen d etki büyüklüğü | > 0 |
| `--alpha` | Anlamlılık düzeyi | 0 < α < 1 |
| `--power` | Hedef güç (a-priori) | α < power < 1 |
| `--ratio` | n2/n1 grup tahsis oranı | > 0 |
| `--n1` | Grup 1 örneklem (post-hoc) | ≥ 2 |
| `--n2` | Grup 2 örneklem (post-hoc) | ≥ 2 |
| `--n-total` | Toplam örneklem (post-hoc + ratio) | ≥ 4 |

---

## Matematiksel Model

Eş varyanslı iki bağımsız örneklem t testi:

```
df      = n1 + n2 - 2
ncp (δ) = d / sqrt(1/n1 + 1/n2)
t_crit  = t.ppf(1 - α/2, df)     # iki taraflı
power   = P(T > t_crit | δ, df) + P(T < -t_crit | δ, df)   # iki taraflı
```

T ~ Noncentral t dağılımı (`scipy.stats.nct`).

---

## Proje Mimarisi

```
gpower-clone/
├── src/
│   ├── engine.py           # Saf matematiksel motor (SciPy tabanlı)
│   ├── cli.py              # Komut satırı arayüzü (JSON çıktı)
│   ├── mcp_server.py       # MCP araç katmanı
│   └── clinical_agent.py   # Türkçe klinik soru ajanı
├── tests/
│   ├── test_engine.py       # Motor birim testleri (30 test)
│   ├── test_cli.py          # CLI sözleşme testleri (9 test)
│   ├── test_differential.py # Differansiyel testler (2 test)
│   ├── test_mcp.py          # MCP araç testleri (6 test)
│   ├── test_clinical_agent.py  # Klinik ajan testleri (2 test)
│   └── test_boundaries.py  # Sınır koşulu testleri (7 test)
├── oracle/
│   ├── gpower_reference.csv     # 29 G*Power 3.1.9.7 referans vektörü
│   ├── library_reference.csv    # 1524 SciPy/pingouin doğrulama vektörü
│   └── manifest.csv             # Oracle bütünlük manifestosu
├── prompts/                 # Tersine mühendislik süreç notları
├── SPEC.md                  # Gherkin kabul kriterleri (15 senaryo)
├── LEDGER.md                # Kanıt defteri (14 bulgu)
└── HALLUCINATIONS.md        # Uydurulmuş iddia defteri
```

---

## Test Sonuçları

```
========================= 80 passed in 10.28s =========================
```

| Test Dosyası | Test Sayısı | Durum |
|---|---|---|
| `test_engine.py` | 30 | PASSED |
| `test_cli.py` | 9 | PASSED |
| `test_differential.py` | 2 | PASSED |
| `test_mcp.py` | 6 | PASSED |
| `test_clinical_agent.py` | 2 | PASSED |
| `test_boundaries.py` | 7 | PASSED |
| **TOPLAM** | **80** | **80/80 PASSED** |

---

## Referans Vektör Uyumu

**Ödev Belgesi Bölüm 4:** `tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1` → n1=105, n2=105, n_total=210 ✓
**G*Power Kılavuzu s.4:** `tails=1, d=0.5, alpha=0.05, power=0.95, ratio=1` → n1=88, n2=88, n_total=176 ✓

---

## Referanslar

1. Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G*Power 3: A flexible statistical power analysis program. *Behavior Research Methods, 39*(2), 175–191.
2. G*Power 3.1 Manual. Heinrich Heine Universität Düsseldorf.
3. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
4. SciPy Documentation: `scipy.stats.nct`, `scipy.stats.t`.

---

*Bu proje YZM301 dersi kapsamında akademik amaçla geliştirilmiştir.*
