# SPEC.md: G*Power t2-indep Davranış Spesifikasyonu

Bu doküman, G*Power 3.1.9.7 programının iki bağımsız örneklem t testi (`t2-indep`) için a priori ve post hoc güç analizi davranışını belirleyen resmi kabul kriterlerini Gherkin biçiminde tanımlar.

Belirtilen kriterler literatür belgeleri ([DOK]), REA statik analiz bulguları ([REA]) ve matematiksel doğrulama temeline dayanır. Orijinal G*Power ikili dosyasında henüz birebir doğrulanmamış kısımlar açıkça `[ADAY KRİTER]` olarak etiketlenmiştir.

---

## Özellik: İki Bağımsız Grup t Testi İçin Güç ve Örneklem Büyüklüğü Analizi (t2-indep)

Kapsam:
- Test Ailesi: t tests
- İstatistiksel Test: Means: Difference between two independent means (two groups)
- Modlar: A priori (`a-priori`), Post hoc (`post-hoc`)
- Matematiksel Model: Eş varyanslı Student t testi, serbestlik derecesi $df = n_1 + n_2 - 2$, noncentrality parametresi $\delta = d / \sqrt{1/n_1 + 1/n_2}$.

---

### Senaryo 1: Geçerli parametrelerle standart iki taraflı A priori analizi
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And kuyruk sayısı (tails) 2
  And etki büyüklüğü (d) 0.5
  And anlamlılık düzeyi (alpha) 0.05
  And hedef istatistiksel güç (power) 0.95
  And grup büyüklüğü tahsis oranı (ratio) 1.0
  When hesaplama motoru çalıştırıldığında
  Then n1 pozitif tam sayı ve 105 olmalıdır
  And n2 pozitif tam sayı ve 105 olmalıdır
  And n_total 210 olmalıdır
  And df 208 olmalıdır
  And ncp değeri yaklaşık 3.6228 olmalıdır (4 basamak toleransla)
  And critical t değeri yaklaşık 1.9714 olmalıdır (4 basamak toleransla)
  And actual_power değeri en az 0.95 olmalı ve yaklaşık 0.9501 olmalıdır
  And sonuç tek satır makine tarafından okunabilir JSON olarak dönmelidir

---

### Senaryo 2: Geçerli parametrelerle tek taraflı A priori analizi
  [DOK] [DOĞRULANMIŞ - G*Power Manual Sayfa 4 Örneği]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And kuyruk sayısı (tails) 1
  And etki büyüklüğü (d) 0.5
  And anlamlılık düzeyi (alpha) 0.05
  And hedef güç (power) 0.95
  And grup büyüklüğü oranı (ratio) 1.0
  When hesaplama motoru çalıştırıldığında
  Then n1 değeri 88 olmalıdır
  And n2 değeri 88 olmalıdır
  And n_total 176 olmalıdır
  And df 174 olmalıdır
  And critical t değeri t.ppf(0.95, 174) ≈ 1.6537 olmalıdır
  And actual_power en az 0.95 olmalı ve yaklaşık 0.9508 olmalıdır

---

### Senaryo 3: Geçerli parametrelerle Post hoc güç analizi
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And analiz modu "post-hoc"
  And kuyruk sayısı (tails) 2
  And etki büyüklüğü (d) 0.5
  And anlamlılık düzeyi (alpha) 0.05
  And n1 örneklem büyüklüğü 105
  And n2 örneklem büyüklüğü 105
  When post-hoc modu çalıştırıldığında
  Then n_total 210 olmalıdır
  And df 208 olmalıdır
  And actual_power 0.9501 olmalıdır
  And ncp 3.6228 olmalıdır
  And critical t 1.9714 olmalıdır

---

### Senaryo 4: Eşit olmayan grup oranı (ratio != 1) ile A priori analizi
  [DOK] [ADAY KRİTER]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And kuyruk sayısı (tails) 2
  And etki büyüklüğü (d) 0.5
  And alpha 0.05
  And hedef güç 0.90
  And grup oranı (ratio = n2/n1) 2.0
  When a-priori modu çalıştırıldığında
  Then n1 tamsayı olmalıdır
  And n2 tamsayı olmalı ve n2 = ceil(ratio * n1) koşulunu sağlamalıdır
  And n_total = n1 + n2 olmalıdır
  And hesaplanan actual_power hedef güce (0.90) eşit veya büyük olmalıdır
  And n1 bir azaltıldığında güç hedef gücün altına düşmelidir (minimal tamsayı N)

---

### Senaryo 5: Çok küçük etki büyüklüğü (Boundary Case: d = 0.05)
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And kuyruk sayısı 2
  And etki büyüklüğü 0.05
  And alpha 0.05
  And hedef güç 0.80
  And grup oranı 1.0
  When a-priori modu çalıştırıldığında
  Then sistem taşma (overflow) veya sonsuz döngüye girmemelidir
  And n1 ve n2 pozitif büyük tamsayılar üretmelidir (n1 ≈ 6280)
  And actual_power >= 0.80 koşulunu sağlamalıdır

---

### Senaryo 6: Çok büyük etki büyüklüğü (Boundary Case: d = 2.5)
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And kuyruk sayısı 2
  And etki büyüklüğü 2.5
  And alpha 0.05
  And hedef güç 0.95
  And grup oranı 1.0
  When a-priori modu çalıştırıldığında
  Then n1 ve n2 en az 2 olmalıdır (df >= 1 koşulunu koruyarak)
  And n_total = n1 + n2 olmalıdır
  And actual_power hedef gücü rahatlıkla karşılamalıdır

---

### Senaryo 7: Hedef gücün alfa değerine eşit veya ondan küçük olması
  [DOK] [ADAY KRİTER]
  Given test ailesi "t2-indep"
  And analiz modu "a-priori"
  And alpha 0.05
  And hedef güç 0.04 (hedef güç <= alpha)
  When a-priori modu çalıştırıldığında
  Then sistem bir doğrulama hatası (ValidationError) fırlatmalıdır
  And hata mesajı "Hedef güç (power), anlamlılık düzeyi (alpha)'dan büyük olmalıdır" uyarısını içermelidir
  And standart çıktıya `{"error":"..."}` formatında JSON yazılmalıdır
  And işlem sıfırdan farklı bir çıkış koduyla (exit code != 0) sonlanmalıdır

---

### Senaryo 8: Geçersiz alfa değeri (alpha <= 0 veya alpha >= 1)
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And alpha -0.05 veya 1.0 veya 0.0
  When motor veya CLI çalıştırıldığında
  Then sistem işlemi reddetmelidir
  And `{"error":"..."}` şeklinde tek satır JSON döndürmelidir
  And çıkış kodu 1 olmalıdır

---

### Senaryo 9: Geçersiz hedef güç değeri (power <= 0 veya power >= 1)
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And power 1.2 veya 0.0 veya -0.1
  When motor veya CLI çalıştırıldığında
  Then işlem reddedilmeli ve açıklayıcı hata JSON'ı üretilmelidir
  And çıkış kodu 0 olmamalıdır

---

### Senaryo 10: Geçersiz kuyruk değeri (tails != 1 ve tails != 2)
  [DOK] [DOĞRULANMIŞ]
  Given tails parametresi 3 veya 0 veya "iki"
  When CLI çağrıldığında
  Then sistem hata vermeli, parametreyi sessizce 2'ye düzeltmemelidir
  And standart çıktıya `{"error":"tails parametresi yalnızca 1 veya 2 olabilir"}` yazılmalıdır

---

### Senaryo 11: Geçersiz veya negatif grup tahsis oranı (ratio <= 0)
  [DOK] [DOĞRULANMIŞ]
  Given ratio parametresi -1 veya 0
  When CLI veya motor çalıştırıldığında
  Then işlem reddedilmeli ve açık bir hata mesajı döndürülmelidir

---

### Senaryo 12: Post hoc modunda yetersiz örneklem büyüklüğü (n < 2)
  [DOK] [DOĞRULANMIŞ]
  Given test ailesi "t2-indep"
  And analiz modu "post-hoc"
  And n1 = 1 veya n2 = 1 (serbestlik derecesi df = 1 + 1 - 2 = 0)
  When motor çalıştırıldığında
  Then sistem t dağılımı serbestlik derecesinin en az 1 olması gerektiğini belirterek hata vermelidir

---

### Senaryo 13: Eksik zorunlu parametreler
  [DOK] [DOĞRULANMIŞ]
  Given `gpower-clone --test t2-indep --mode a-priori` komutu çağrıldığında (d, alpha, power eksik)
  When komut satırı argümanları ayrıştırıldığında
  Then CLI eksik parametreleri bildiren tek satır `{"error":"..."}` JSON çıktısı üretmelidir
  And işlem sıfırdan farklı çıkış kodu ile sonlanmalıdır

---

### Senaryo 14: Desteklenmeyen veya beklenmeyen parametre/test ailesi
  [DOK] [DOĞRULANMIŞ]
  Given `--test anova-oneway` veya `--test chi2` çağrıldığında
  When CLI çalıştırıldığında
  Then sistem desteklenmeyen test ailesi olduğunu belirten `{"error":"..."}` yanıtı üretmelidir
  And başarı taklidi yapılmamalıdır

---

### Senaryo 15: CLI JSON sözleşmesi ve sessiz düzeltme yapılmaması
  [DOK] [DOĞRULANMIŞ]
  Given geçerli veya geçersiz herhangi bir komut satırı çağrısı
  When işlem tamamlandığında
  Then standart çıktıya ASLA log, karşılama mesajı, debug çıktısı veya banner basılmamalıdır
  And standart çıktı daima tam olarak 1 satırlık geçerli bir JSON nesnesi olmalıdır
  And hatalı girdiler (örn. `--power 95` girilip `0.95` kastedilmesi) sessizce düzeltilmemeli, net hata üretilmelidir
