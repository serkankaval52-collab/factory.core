# Changelog

Bu paket [Semantic Versioning](https://semver.org/lang/tr/) kullanır.

## [0.1.0] — 2026-08-15

İlk sürüm — FactoryGames 0A adım 3 (şablon iskeleti).

### Eklendi
- `RuntimeInitBootstrap` — kod-öncelikli sahne kurulumu iskeleti (kök nesne,
  ortografik kamera, `Screen.safeArea` normalizasyonu). Sahne dosyasına dokunmaz.
- `JsonLoader` — `StreamingAssets` JSON okuyucu; okunamadığında sessiz varsayım
  yapmaz, kaynağı metin olarak döndürür.
- `TelemetryWriter` + `GateResult` — Sözleşme-1 telemetri satırı, JSONL append;
  tüm sayılar `InvariantCulture`.
- `IAnalyticsSink` / `NullAnalyticsSink` / `AnalyticsEvents` — analitik geçidi ve
  `sessiz_toparlanma` dahil sabit olay adları.
- `IAdGateway` / `NullAdGateway` — reklam geçidi ve reklamsız varsayılan.

### Notlar
- Sondadan (Aşama -1) taşınan iki saha dersi kalıcılaştırıldı:
  kültür-bağımsız sayı yazımı (§7.5) ve `Camera.main`/`Find*` kullanmayan
  açık-atama kurulum deseni (kural 8).

## [0.1.1] - 2026-08-15

### Eklendi
- `tools/lint/test_lint.py` - lint'in KENDI dogrulugunun testi (once-kirmizi disiplini):
  WCAG referans degerleri, renk korlugu ayrimi, gecen/kalan palet ornekleri ve
  lint.py surec cikis kodu. 10 test.

### Duzeltildi
- Sablon paletinin kritik ciftleri G6 esigini gecmiyordu (olculdu, taramayla
  degistirildi). Ayrinti: FactoryGames docs/factory/verification/03-v3-esik-saglamasi.md

## [0.1.2] - 2026-08-15

### Degisti
- `templates/` -> `templates~/`: Unity `~` ile biten dizinleri ithal etmez, boylece
  paket kokte kalirken iskelet oyun projesine hic girmez. Depo semasi borcu KAPANDI
  (`?path=/Runtime` alternatifi reddedildi). README'ye scaffold komutlari eklendi
  (PackageManager API veya kabuk globu — sihirli yol yazilmaz).
- G6 (mimar karari v1.4.1): `tehlike<->vurgu` cifti WCAG oranindan CIEDE2000'e tasindi
  (`gorsel_sinyal_deltae_min` = 2.0, `simdilik_tahmin` etiketli). Arka plan ciftleri
  ve ui_metin esikleri DEGISMEDI. Doygun palet artik geciyor; desature zorlamasi kalkti.
- `uygulama_boyut_tavan_mb` esiklerden KALDIRILDI (Ek C'de yok — kural 28); BOYUT kapisi
  artik VERI-YOK + kanit satiri veriyor, "gecti" saymiyor.

### Eklendi
- CIEDE2000 (sRGB->Lab D65 -> dE00), harici bagimlilik yok; Sharma-Wu-Dalal referans
  cifleriyle test edildi.
- Uc yeni oz-test: ayirt edilemeyen sinyal cifti KIRMIZI, doygun mavi/turuncu YESIL,
  eksik esik VERI-YOK. Ayrica kapinin BILINEN SINIRI belgelendi (kirmizi-yesil cifti
  dE00 kapisindan gecer — G6 ek kurali bu yuzden zorunlu). Toplam 15 test.

### Duzeltildi
- `__pycache__` depodan cikarildi ve gitignore'a alindi (kendi HAM-ARTEFAKT
  disiplinimizin geregi — 0A denetim bulgusu).
- Lint'lerdeki kapatilmamis dosya tutamaclari (`-W error::ResourceWarning` temiz).

## [0.1.3] - 2026-08-15

### Degisti
- CVD test kilitleri mimar denetimine gore yeniden duzenlendi: `#E74C3C`/`#E85142`
  testi "NORMAL TABAN" olarak damgalandi (CVD disleri degil, normal gorus tabani).

### Eklendi
- `test_CVD_KILIDI_karisim_metameri_protanopide_KIRMIZI`: asil CVD kilidi —
  `#C64040`/`#33FF00` normal 83.13 iken protanopide 1.26; kapi KIRMIZI vermek zorunda.
- `test_es_L_kirmizi_yesil_de_cokusmuyor`: es-parlaklik ciftlerinde cokus olmadiginin
  regresyon kilidi.
- Toplam 15 -> 17 test.

### Karar kaydi
- Machado ve ark. (2009) matrislerine gecis REDDEDILDI (mimar): mevcut model icin
  olculmus yeterlilik kaniti var; motor degisimi dogrulanmamis karmasiklik.
