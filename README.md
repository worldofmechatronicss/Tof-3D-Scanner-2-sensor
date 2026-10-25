# Dual LiDAR S3

ESP32-S3, iki VL53L5CX ve BNO085 ile deneysel 3D nokta bulutu görüntüleyici.

Bu çalışma [Henrique Ferrolho'nun VL53L5CX-BNO08X-viewer projesinden](https://github.com/ferrolho/VL53L5CX-BNO08X-viewer)
türetilmiştir. İki sensör desteği, ayrı montaj dönüşümleri ve Windows masaüstü
başlatıcısı eklenmiştir. Orijinal MIT lisansı ve yazar atfı korunmuştur.

## Özellikler

- Sensör başına 8×8 mesafe, ayrı sensör kimliği ve kare sayacı.
- BNO085 quaternion yön verisi; Game Rotation Vector modu.
- Sensör başına RX hızı ve ayrı çizim döngüsü hızı.
- Bağımsız zamansal filtre, Least Squares ve RANSAC düzlem tahmini, RMSE.
- Nokta biriktirme, voxel örnekleme ve PLY indirme.
- Ayrı sensör konum/açı ayarları ve kalibrasyon kaydı.
- Kalıcı toplu ışın çizimi; Clip to Measurement desteği.
- Tarayıcı arayüzü ve aynı arayüzü açan Windows masaüstü başlatıcısı.

## Donanım

| Parça | Adet |
|---|---:|
| ESP32-S3 N16R8 | 1 |
| VL53L5CX-SATEL | 2 |
| BNO085 / uyumlu BNO08X modülü | 1 |

| Sinyal | ESP32-S3 |
|---|---|
| Ortak SDA / SCL | GPIO8 / GPIO9 |
| ToF 1 LPn / ToF 2 LPn | GPIO4 / GPIO5 |
| Ortak ToF I2C_RST | GPIO6 |
| ToF AVDD ve IOVDD | 3V3 |
| BNO085 VCC | 3V3 (kullanılan modül) |
| BNO085 PS0 ve PS1 | GND, I2C modu |
| Tüm GND | Ortak GND |

Adresler: ToF 1 `0x2A`, ToF 2 `0x29`, BNO085 `0x4B` veya `0x4A`.
Bağlantıları güç kapalıyken yapın; farklı breakout kartlarında besleme gereksinimini doğrulayın.

## Hızlı başlangıç

### ESP32 firmware

Arduino IDE'de şu kütüphaneleri kurun:

- SparkFun VL53L5CX Arduino Library
- SparkFun BNO08x Cortex Based IMU

`firmware/dual_vl53l5cx_bno085/dual_vl53l5cx_bno085.ino` dosyasını açıp ESP32-S3'e yükleyin.
Hedef sensör başına 10 Hz, seri haberleşme 460800 baud. Seri Monitörde `READY`
ve `"s":1` / `"s":2` paketlerini kontrol edin, ardından Seri Monitörü kapatın.

### Bilgisayar görüntüleyici

Python 3.12 ile test edilmiştir. Proje kökünde:

```sh
python -m pip install -r viewer/requirements.txt
python -m viewer --port COM5 --baud 460800
```

`COM5` yerine kendi portunuzu yazın. Linux/macOS'ta uygun `/dev/...` yolunu kullanın.
Tarayıcıda http://localhost:8080 adresini açın.
Windows'ta `KURULUM.bat` ve `BASLAT.bat` dosyaları da kullanılabilir.

### Windows masaüstü uygulaması

`PC_UYGULAMASI_OLUSTUR.bat` dosyasını çalıştırın. Sonuç:

```text
dist/DualLidarS3/DualLidarS3.exe
```

Bu repo hazır EXE içermez. Oluşturma Windows üzerinde yapılır. Klasörün tamamı
birlikte dağıtılır. Edge WebView2 Runtime gerekir. Ayrıntılar: [PC_OKU.md](PC_OKU.md).

## Önce kalibrasyon

**layout.json içindeki montaj değerleri geçicidir.** 64,91 mm aralık ve sensör
merkezine göre simetrik yerleşim varsayılmıştır. Kendi optik merkez mesafelerinizi,
BNO085 gövde eksenlerini ve kart dönüşlerini doğrulayın.

İlk denemeyi düz duvarla, biriktirme kapalıyken yapın. İki renkli yüzeyin hizasını
kontrol edin. Sonra yön takibini açıp küçük açılarla test edin. Görünüm dönüşü ve
kamera ayarı, fiziksel montaj kalibrasyonunun yerine geçmez.

## Sınırlar

- Deneysel prototiptir; doğruluğu belgelenmiş ticari tarayıcı değildir.
- BNO085 yön ölçer. Yürüyerek tarama için konum takibi/SLAM uygulanmamıştır.
- Game Rotation Vector manyetometre kullanmaz; yaw zamanla kayabilir.
- ToF ve IMU poz ortası zaman eşleştirmesi uygulanmamıştır; yavaş tarayın.
- Aynı yöne bakan iki sensör görüş alanını iki katına çıkarmaz.
- RANSAC düzlem tahminini iyileştirir; haritadaki aykırı noktaları otomatik silmez.
- Windows EXE/WebView2 ve fiziksel çift sensör testlerinin kullanıcı sisteminde doğrulanması gerekir.

## Testler

```sh
python -m pip install pytest
python -m pytest -q viewer/tests
```

48 test: paket doğrulama, dönüşümler, iki sensör, düzlem/RANSAC, gerçek Viser
sunucusu, PLY yönü, masaüstü alt süreci ve örnek seri akış testleri. Windows'ta
POSIX pseudo-terminal testi atlanır. Native Windows pencere testi kapsam dışıdır.

## Belgeler ve lisans

- [Ayrıntılı Türkçe teknik rehber](docs/TECHNICAL_GUIDE_TR.md)
- [Masaüstü kurulum rehberi](PC_OKU.md)
- [Orijinal proje README](docs/README_UPSTREAM.md)
- [Katkı ve kaynak atıfları](NOTICE.md)
- [MIT License](LICENSE)

Proje paylaşımları: [@worldofmechatronics](https://www.instagram.com/worldofmechatronics/)
