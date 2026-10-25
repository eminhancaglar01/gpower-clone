# HALLUCINATIONS.md: Yanlış Varsayımlar ve Düzeltme Günlüğü

Bu dokümanda, tersine mühendislik ve yeniden gerçekleme sürecinde başlangıçta makul görünen, ancak deneysel veya matematiksel olarak çürütülen/düzeltilen varsayımlar belgelenmiştir.

---

## Kayıt 1: REA Aracının Windows'ta Ek Kurulumsuz Decompile Yapabileceği Varsayımı

- **Başlangıçtaki İddia:** REA (Reverse Engineer Anything) CLI'ı sistemde kurulu olduğundan (`rea 6.5.0`), `GPowerNT.exe` dosyasını doğrudan ayrıştırıp fonksiyon seviyesinde C/C++ sözde koduna (pseudocode) dönüştürebilir.
- **İddianın Neden Makul Göründüğü:** REA zengin bir MCP ve CLI araç kümesine sahiptir (`batch_decompile`, `list_procedures`, `binary_overview`). `open_binary` çağrısı başarıyla PE32 formatını ve dosya özetini tanımıştır.
- **İddiayı Doğrulamak İçin Kullanılan Yöntem:** `call_mcp_tool` üzerinden `open_binary` sonrasında `binary_overview` aracı çalıştırıldı.
- **İddianın Yanlış veya Eksik Olduğunun Nasıl Anlaşıldığı:** REA şu hatayı döndürdü:
  ```json
  {
    "error": {
      "code": "provider_unavailable",
      "candidate_ids": ["ghidra", "hopper", "ida"],
      "rejections": [
        {"provider_id": "ghidra", "reason": "Set GHIDRA_INSTALL_DIR to an extracted Ghidra 12.1.x release directory"},
        {"provider_id": "hopper", "reason": "Hopper integration is not supported on win32"},
        {"provider_id": "ida", "reason": "Set REA_IDA_MCP_CONFIG to an upstream IDA MCP JSON registration"}
      ]
    }
  }
  ```
  Sistemde Ghidra, JDK 21 veya IDA bulunmadığı için REA'nın derin sembolik analiz sağlayıcısının aktif olmadığı anlaşıldı.
- **Bunu Yakalayan Test veya Deney:** REA MCP `binary_overview` çalıştırma deneyi.
- **Sonuç ve Düzeltme:** REA'nın PE kaynaklarını (`inspect_pe_resources`), mimari bilgilerini ve hash değerlerini yerel olarak doğrulayabildiği, ancak derin decompile işlemlerinin ortam kısıtları nedeniyle yapılamadığı `LEDGER.md` ve `README.md` dosyalarına dürüstçe işlendi. Olmayan bir Ghidra decompile kodu repoya asla eklenmedi.

---

## Kayıt 2: Headless Ajan Ortamında GUI Ekran Görüntüsü ve Fare Otomasyonu Varsayımı

- **Başlangıçtaki İddia:** `GPowerNT.exe` Windows ortamında başlatılabildiği için `pywinauto` veya Win32 API ile otomatik olarak form doldurulup Calculate butonuna tıklanarak 30 adet ekran görüntüsü alınabilir.
- **İddianın Neden Makul Göründüğü:** GPowerNT başarıyla arka planda çalıştırılabilmekte (`poll: None`) ve Win32 kontrolleri listelenebilmektedir.
- **İddiayı Doğrulamak İçin Kullanılan Yöntem:** `pywinauto` kütüphanesi kurularak `win.set_focus()` ve `win.capture_as_image()` çağrıldı.
- **İddianın Yanlış veya Eksik Olduğunun Nasıl Anlaşıldığı:** Çalıştırma sırasında şu kritik hata alındı:
  ```
  RuntimeError: There is no active desktop required for moving mouse cursor!
  ```
  Ajanın çalıştığı Windows oturumunun headless / non-interactive (etkileşimsiz masaüstü) oturumu olduğu, fiziksel bir ekran ve fare işaretçisi bulunmadığı için fare hareketlerinin işletim sistemi düzeyinde engellendiği görüldü.
- **Bunu Yakalayan Test veya Deney:** `test_pywinauto_calc.py` otomasyon betiği.
- **Sonuç ve Düzeltme:** Canlı GUI ekran görüntüleri varmış gibi sahte görsel dosyalar üretilmedi. Bunun yerine:
  1. G*Power resmi kılavuzunda (Manual s. 4, s. 52) ve Faul et al. (2007) makalesinde yayımlanmış kesin referans değerler kullanıldı.
  2. Gerçek G*Power arayüzünden alınacak görüntüler için şablon altyapısı ve diferansiyel test koşucusu hazırlandı.
  3. Durum dokümantasyonda şeffaf biçimde açıklandı.

---

## Kayıt 3: İki Taraflı Testte Güç Hesabında Tek Kritik Bölgenin Yeterli Olduğu Varsayımı

- **Başlangıçtaki İddia:** İki taraflı testte pozitif etki büyüklüğü ($d > 0$) için güç hesabında yalnızca üst kritik bölge $P(T > t_{crit})$ hesaplansa yeterlidir; alt kuyruk $P(T < -t_{crit})$ ihmal edilebilir.
- **İddianın Neden Makul Göründüğü:** $ncp \approx 3.6$ gibi büyük değerlerde sol kuyruk olasılığı $10^{-5}$ mertebesinde son derece küçüktür.
- **İddiayı Doğrulamak İçin Kullanılan Yöntem:** $d = 0.1$ ve düşük örneklem ($N = 20$) gibi sınır değerlerde hem iki kuyruklu tam formül $(1 - nct.cdf(t_{crit})) + nct.cdf(-t_{crit})$ hem de sadece üst kuyruk $1 - nct.cdf(t_{crit})$ hesaplanıp karşılaştırıldı.
- **İddianın Yanlış veya Eksik Olduğunun Nasıl Anlaşıldığı:** Küçük etki büyüklüklerinde ve düşük serbestlik derecelerinde sol kuyruk olasılığının gücün 4. ondalık basamağını etkilediği görüldü. Örneğin $ncp \approx 0.5$ durumunda sol kuyruk göz ardı edildiğinde güç 0.005 kadar eksik hesaplanmaktadır.
- **Bunu Yakalayan Test veya Deney:** `test_engine_power_small_effect` birim testi.
- **Sonuç ve Düzeltme:** `src/engine.py` içinde iki taraflı testler için hem sağ hem de sol kuyruk olasılıklarının toplamı tam noncentral t dağılımı üzerinden kodlandı.
