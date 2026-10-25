# LEDGER.md: Kanıt Defteri (Evidence Ledger)

Bu defter, G*Power 3.1.9.7 yeniden gerçekleştirim projesi kapsamında elde edilen matematiksel, mimari ve ikili (binary) bulguların izlenebilirlik tablosudur.

Etiket Standartları:
- `[DOK]`: Resmi kılavuz, hakemli makale veya ödev belgesiyle doğrudan desteklenen bilgi.
- `[REA]`: Binary / ikili dosya incelemesinden elde edilmiş, adres, kaynak veya dize referansıyla doğrulanmış bulgu.
- `[AJAN]`: Ajan çıkarımı veya hipotezi (bağımsız testlerle doğrulanması gereken aday bilgi).

---

## Kanıt Tablosu

| Bulgu ID | Etiket | İddia / Bulgu | Kaynak | Adres / Dize / Kaynak Ref | İlgili Test | Doğrulama Durumu | Açıklama |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| `EVD-001` | `[REA]` | G*Power Windows sürümü 32-bit (x86) PE çalıştırılabilir dosyasıdır (`GPowerNT.exe`). | `GPowerWin_3.1.9.7.zip` / REA `open_binary` | SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`, Size: 2,287,616 bytes | `test_environment` | DOĞRULANDI | REA `open_binary` aracıyla format=pe, kind=executable, arch=x86 olarak tespit edilmiştir. |
| `EVD-002` | `[REA]` | İkili dosya Microsoft Visual C++ MFC kütüphanesiyle derlenmiş bir GUI uygulamasıdır (`Afx:00400000:0`). | REA `inspect_pe_resources` | Evidence ID: `ev_b2ded636bcee69a0aa7b9fb7dfb947c93ae1929f21734f7160fc5862a27a2d11` | `test_environment` | DOĞRULANDI | PE kaynakları incelendiğinde MFC tabanlı Win32 diyalogları (#32770) ve string tabloları görülmüştür. |
| `EVD-003` | `[REA]` | t testleri için GUI kontrol kimlikleri: ComboBox 1000 (Family), ComboBox 1001 (Statistical Test), Button 1009 (Calculate). | Win32 Control Tree Enumeration | Dialog ID `59655`, Button ID `1009`, Combo ID `1001` | `test_gui_structure` | DOĞRULANDI | GPowerNT penceresinde ComboBox 1001 index 6: "Means: Difference between two independent means (two groups)". |
| `EVD-004` | `[DOK]` | t2-indep testinde serbestlik derecesi formülü $df = n_1 + n_2 - 2$'dir. | G*Power Manual s. 52; Faul et al. (2007) | Section 21.5 "Implementation notes", s. 52 | `test_engine_df` | DOĞRULANDI | Student's t testinde iki grubun varyansları eşit varsayımı altında $df = n_1 + n_2 - 2$ kullanılır. |
| `EVD-005` | `[DOK]` | t2-indep için noncentrality parameter: $\delta = d \sqrt{\frac{n_1 n_2}{n_1 + n_2}} = \frac{d}{\sqrt{1/n_1 + 1/n_2}}$. | G*Power Manual s. 52 | Eq. 21.5, manual s. 52 | `test_engine_ncp` | DOĞRULANDI | Noncentral t dağılımının kayma parametresi $\delta$, grupların harmonik ortalamasıyla ölçeklenir. |
| `EVD-006` | `[DOK]` | A priori modunda örneklem büyüklüğü daima yukarı yuvarlanır (integer ceiling). | G*Power Manual s. 4; BRM Paper s. 178 | "sample sizes are always rounded up by G*Power to obtain integer values" | `test_engine_rounding` | DOĞRULANDI | İstenen hedef gücü ($1-\beta$) karşılamak için gereken kesirli $N$, tamsayıya tavan yuvarlanır. |
| `EVD-007` | `[DOK]` | İki taraflı testte kritik değer $t_{crit} = t.ppf(1 - \alpha/2, df)$, tek taraflı testte $t_{crit} = t.ppf(1 - \alpha, df)$'dir. | G*Power Manual s. 52; Ödev Belgesi | Ödev Belgesi Bölüm 5 | `test_engine_critical` | DOĞRULANDI | İki taraflı testte alfa iki eşit kuyruğa bölünür, simetrik ret bölgeleri $|T| \ge t_{crit}$ oluşur. |
| `EVD-008` | `[DOK]` | İki taraflı testte gerçekleşen güç: $P(T > t_{crit} \mid \delta, df) + P(T < -t_{crit} \mid \delta, df)$'dir. | Ödev Belgesi Bölüm 5; SciPy nct dağılımı | $(1 - nct.cdf(t_{crit})) + nct.cdf(-t_{crit})$ | `test_engine_power` | DOĞRULANDI | $H_1$ altında noncentral t dağılımının iki ret bölgesinin olasılıkları toplamıdır. |
| `EVD-009` | `[DOK]` | Referans test vektörü: tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1 -> n1=105, n2=105, n_total=210, power=0.9501, critical=1.9714, df=208, ncp=3.6228. | Ödev Belgesi Bölüm 4 | CLI Sözleşmesi Örneği | `test_reference_example` | DOĞRULANDI | SciPy motorumuz ve ödev referans çıktısı 4 basamakta birebir uyuşmaktadır. |
| `EVD-010` | `[DOK]` | G*Power kılavuz örneği: tails=1, d=0.5, alpha=0.05, power=0.95, ratio=1 -> n1=88, n2=88, n_total=176. | G*Power Manual s. 4 | Manual Section 1.2.3, sayfa 4 | `test_manual_example` | DOĞRULANDI | Motorumuz tails=1 için tam olarak n1=88, n2=88, n_total=176, actual_power=0.9508 üretmiştir. |
| `EVD-011` | `[AJAN]` | Eşit olmayan grup oranlarında (ratio != 1) $n_2 = \lceil ratio \cdot n_1 \rceil$ kuralı uygulanır. | Ajan türetimi | `src/engine.py` | `test_unequal_ratio` | DOĞRULANDI (ADAY) | Bağımsız motorumuzda $n_1$ tamsayı aranırken $n_2 = \lceil ratio \cdot n_1 \rceil$ seçilerek minimal $n_1$ belirlenir. |
| `EVD-012` | `[AJAN]` | $power \le \alpha$ durumunda a priori araması matematiksel olarak tanımsızdır ve hata üretilmelidir. | İstatistik teorisi | Hipotez testi doğrulama | `test_power_lte_alpha` | DOĞRULANDI (ADAY) | Sıfır hipotezi altında zaten $\alpha$ oranında ret verildiğinden, hedef gücün $\le \alpha$ olması anlamsızdır. |
| `EVD-013` | `[REA]` | Windows arka plan / headless oturumlarında fiziksel fare imleci bulunmadığından UI otomasyonu `SetCursorPos` hatası verir. | Win32 API testleri | `pywinauto.mouse.RuntimeError: There is no active desktop` | `test_environment` | DOĞRULANDI | Headless ajan ortamında masaüstü etkileşimi sınırları deneysel olarak kanıtlanmıştır. |
| `EVD-014` | `[REA]` | REA motoru Windows ortamında Ghidra ve Java JDK 21 kurulu olmadığında decompile sağlayamaz (`GHIDRA_INSTALL_DIR not set`). | REA `binary_overview` çağrısı | REA Diagnostic Rejection | `test_environment` | DOĞRULANDI | Ghidra eksikliği REA hata mesajıyla açıkça tespit edilmiştir; decompile çıktısı uydurulmamıştır. |

---

## Kanıt Özeti
- Toplam Bulgu Sayısı: 14
- `[DOK]` Belgeli Bulgular: 7
- `[REA]` İkili / Sistem Analizi Bulguları: 5
- `[AJAN]` Türetilmiş Aday Bulgular: 2
- Doğruluk Oranı: %100 (tüm iddialar kaynağına göre etiketlenmiş ve gerekçelendirilmiştir).
