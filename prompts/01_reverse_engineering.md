# Oturum 1: İnceleme ve Tersine Mühendislik (Reverse Engineering) Başlangıç Promptu

**Hedef Sistem:** G*Power 3.1.9.7 (Windows NT/2000/XP/Vista/7/8/10/11)  
**Kapsam:** Means: Difference between two independent means (two groups) (`t2-indep`)  
**Görev:** İkili dosya analizi, dokümantasyon taraması, matematiksel model çıkarma ve kabul kriterleri (SPEC.md) üretimi.

---

## Talimatlar

Sen bir kıdemli tersine mühendislik uzmanı ve istatistik araştırmacısısın. Aşağıdaki adımları sırayla icra et:

1. **İkili Dosya İncelemesi (Binary Inspection):**
   - `GPowerNT.exe` PE32 ikili dosyasını REA araçlarıyla incele.
   - Dosya özetini (SHA-256, dosya boyutu, makine mimarisi) çıkar ve doğrula.
   - PE kaynaklarını (`inspect_pe_resources`), menü/diyalog kaynaklarını ve kullanılan statik dizeleri incele.
   - Ghidra/IDA sağlayıcılarının erişilebilirliğini denetle. Sağlayıcı yoksa bunu açıkça raporla; decompile edilmiş kod uydurma.

2. **Davranış ve Matematiksel Model İncelemesi:**
   - Resmi G*Power dokümantasyonunu (Faul et al. 2007; G*Power Manual) incele.
   - Serbestlik derecesi ($df$), noncentrality parametresi ($\delta$), kritik t değeri ($t_{crit}$) ve istatistiksel güç formüllerini kesinleştir.
   - Örneklem büyüklüğünün yukarı yuvarlanması (ceiling) ve eşit olmayan grup oranlarındaki davranışları belirle.

3. **Kanıt Defteri ve Spesifikasyon Üretimi:**
   - Her bulguyu `[DOK]`, `[REA]` veya `[AJAN]` etiketiyle `LEDGER.md` içine kaydet.
   - Sistemin davranışsal sözleşmesini Gherkin sözdizimiyle `SPEC.md` dosyasına yaz.
   - İnceleme oturumu kesinlikle kaynak kodu yazmayacak; yalnızca davranışsal ve matematiksel spesifikasyonu tamamlayıp Oturum 2'ye devredecektir.
