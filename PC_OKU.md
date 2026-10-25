# Dual LiDAR S3 — Windows masaüstü sürümü

Tarama uygulamasının mevcut kaynak dosyaları değiştirilmemiştir. Masaüstü
penceresi aynı Viser arayüzünü Edge WebView2 ile gösterir. İki sensör, filtre,
RANSAC, RMSE, kamera, kalibrasyon ve PLY indirme kontrolleri aynı uygulamadadır.
Normal `BASLAT.bat` ile tarayıcıdan açma yöntemi de korunur.

## İlk hazırlık

1. ZIP'i Windows bilgisayarında yeni, yazılabilir bir klasöre çıkarın.
2. Eski uygulamada `Save Calibration` ile kaydettiğiniz ayarlar varsa eski
   **layout.json** dosyanızı bu yeni klasördeki **layout.json** üzerine kopyalayın.
   İlk masaüstü açılışından ÖNCE yapın.
3. `PC_UYGULAMASI_OLUSTUR.bat` dosyasına çift tıklayın.
4. Script bağımsız `.desktop-venv` Python ortamı oluşturur, gerekli paketleri
   internetten indirir ve PyInstaller ile Windows uygulamasını üretir.
   Mevcut Python paketlerinizi değiştirmez.
5. İşlem bitince şu klasör açılır:
   **dist\DualLidarS3\DualLidarS3.exe**

Bu ZIP, Windows'ta oluşturma için hazır kaynak paketidir; önceden derlenmiş
Windows EXE içermez. EXE'nin Windows üzerinde oluşturulması gerekir.
Python 3.12 64-bit oluşturma için önerilen sürümdür. Script PATH'teki `python`
komutunu kullanır. Python sürümünüzde bağımlılık kurulumu hatası alırsanız hata
çıktısını paylaşın; çalışan tarayıcı ortamını kaldırmayın.

Microsoft Edge WebView2 Runtime gerekir. Windows'ta bulunmuyorsa resmi Microsoft
kurulumunu kullanın: https://developer.microsoft.com/microsoft-edge/webview2/

## Her kullanımda

1. ESP32'yi bağlayın; Arduino Seri Monitörünü ve eski görüntüleyiciyi kapatın.
2. **DualLidarS3.exe** dosyasını açın.
3. COM portunu listeden seçin; gerekirse elle COM5 biçiminde yazın.
4. **Uygulamayi Ac** düğmesine basın. Görüntüleyici aynı pencereye yüklenir.
5. Uygulama kapanınca arka plandaki görüntüleyici durur ve seri port bırakılır.

ESP32 firmware'i yeniden yüklenmez. Paket önceki çift sensör 460800 baud
firmware'iyle çalışır. RX, Render Hz ve tüm tarama işlevleri aynıdır.

Programı başka yere taşırken yalnız EXE'yi değil, **dist\DualLidarS3 klasörünün
tamamını** taşıyın. Hedef PC'de Python gerekmez; WebView2 Runtime ve ESP32'nin
USB seri sürücüsü gerekir. Dağıtım klasörünü kısayolla masaüstünden açabilirsiniz.

Kaynak olarak çalıştırmak için, ortam oluşturulduktan sonra
`PC_UYGULAMASI_AC.bat` dosyası da kullanılabilir.

## Kalibrasyon ve günlükler

Masaüstü ayarları kullanıcıya ait şu dizine kaydedilir:
**%LOCALAPPDATA%\DualLidarS3**

- `layout.json`: Save Calibration ile kaydedilen montaj ve görünüm ayarları.
- `desktop.json`: son COM portu.
- `viewer.log`: son başlatmanın ayrıntıları.

İlk açılışta proje kökündeki layout.json bu dizine kopyalanır. Sonraki açılışlarda
kullanıcının kayıtlı kalibrasyonu korunur ve otomatik üzerine yazılmaz.
Mevcut kaydı bilerek değiştirmek isterseniz program kapalıyken burada bulunan
layout.json dosyasının yedeğini alıp kendi dosyanızla değiştirin.

Tarayıcı sürümü kendi layout.json'unu kullanmaya devam eder; iki sürümün
ayarları ilk kopyalamadan sonra bağımsızdır.

PLY indirme aynı arayüzdeki Download PLY düğmesinden yapılır; yerel pencerenin
indirme desteği açıktır. Kaydetme ekranını/indirilen dosyayı Windows'ta ilk kullanımda
kontrol edin. Kalıcı harita kaydı için pencereyi kapatmadan PLY indirin.

Port dolu/yanlışsa bağlantı ekranında hata gösterilir. ESP32 takılı değilse
Yenile düğmesiyle yeniden tarayın. Tarama sırasında cihaz koparsa pencereyi
kapatın, cihazı bağlayıp yeniden açın.

## Doğrulama sınırı

48 Python testi geçti. Gerçek yerel sunucu, örnek seri veri akışı, HTTP açılışı ve
kapanışta alt sürecin/seri bağlantının bırakılması test edildi. Masaüstü eklenmeden
önceki görüntüleyici, montaj ayarları ve firmware dosyaları byte düzeyinde aynı.
Windows EXE oluşturma, WebView2 penceresi ve yerel dosya indirmesi bu Linux
ortamında çalıştırılamadı; Windows'ta ilk açılış kontrolü gereklidir.
