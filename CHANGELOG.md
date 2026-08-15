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
