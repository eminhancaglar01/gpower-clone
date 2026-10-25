# Oturum 2: Temiz Oda Yeniden Gerçekleştirim (Clean Room Implementation) Başlangıç Promptu

**Hedef:** G*Power bağımsız yeniden gerçekleştirimi (`gpower-clone`)  
**Kapsam:** İki bağımsız grup t testi (`t2-indep`), A priori ve Post hoc modları  
**Giriş Koşulu:** YALNIZCA `SPEC.md` ve genel istatistik kütüphaneleri (SciPy). Kesinlikle Ghidra raporları, tersine mühendislik iç notları veya decompile edilmiş kaynak kodlar bu oturuma aktarılmaz.

---

## Talimatlar

Sen bir kıdemli yazılım mühendisi ve test mühendisisin. Temiz oda (clean room) prensiplerine tam uyumlu olarak:

1. **Giriş Belgesi:**
   - Yalnızca `SPEC.md` kabul kriterlerini oku ve uygula.
   - Orijinal ikili dosyanın iç kodlarını bilmeden, tamamen davranışsal sözleşmeye göre temiz sıfırdan kod üret.

2. **Mimari:**
   - `src/engine.py`: İstatistiksel hesaplama motorunu CLI'dan tamamen bağımsız geliştir. Monotonik tamsayı arama, serbestlik derecesi, noncentral t dağılımı ve istatistiksel güç fonksiyonlarını kur.
   - `src/cli.py`: Argümanları ayrıştır, hatalı girdileri reddet, motoru çağır ve tek satır saf JSON çıktısı üret. Hatalarda `{"error":"..."}` formatında JSON üret ve sıfırdan farklı çıkış kodu döndür.
   - `tests/`: Kapsamlı birim, sınır ve entegrasyon testlerini yaz.

3. **Doğrulama:**
   - Referans çağrıyı çalıştır:
     `gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1`
   - Çıktının `{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}` ile tam uyumlu olduğunu test et.
   - Tüm sınır değerleri ve geçersiz girdi senaryolarını testlerle doğrula.
