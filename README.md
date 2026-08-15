# factory.core

FactoryGames hattının **paylaşılan çalışma zamanı çekirdeği** (UPM paketi) ve
**oyun reposu iskeleti** (`templates/`).

Norm kaynağı: [FactoryGames/docs/PIPELINE.md](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/PIPELINE.md).
Bu repo **oyun bilgisi içermez**; oyunlar ayrı repolardır ve buraya UPM bağımlılığıyla bağlanır.

## Kurulum (oyun reposundan)

`Packages/manifest.json`:

```json
{
  "dependencies": {
    "com.factorygames.core": "https://github.com/serkankaval52-collab/factory.core.git#v0.1.0"
  }
}
```

Bağ **sürüm etiketine** (`#tag`) yapılır — dalın ucuna değil: oyun kendi piniyle yaşar
(PIPELINE "Motor" kararının kardeşi). Repo public olduğu için CI'da token gerekmez.

## Paket içeriği (`Runtime/`)

| tür | ne yapar |
|---|---|
| `RuntimeInitBootstrap` | Kod-öncelikli sahne kurulumunun iskeleti: kök nesne, ortografik kamera, güvenli alan dikdörtgeni. Sahne dosyası şablon varsayılanında kalır; `GameObject.Find` / `FindFirstObjectByType` / `Camera.main` kullanılmaz (kural 8) |
| `JsonLoader` | `StreamingAssets` JSON okuyucu (Sözleşme-2 tek kaynağı). Okunamazsa **sessiz varsayım yapmaz** (kural 6): kaynağı metin olarak döndürür. Android'in jar-içi StreamingAssets kısıtı açıkça raporlanır |
| `TelemetryWriter` | Sözleşme-1 satırı (`{ts, asama, olay, sure_dk, kapi_sonucu, insan_saat, factory_core_surumu, build_hash, ci_dakika}`) JSONL olarak `.factory/telemetry.jsonl`e ekler. **Tüm sayılar `InvariantCulture`** — sonda §7.5 bulgusunun (tr-TR ondalık sızıntısı) kalıcı önlemi |
| `GateResult` | `{gecti, kaldi, veri_yok}` — ilk-koşu.md §1: "veri yok" *geçti* sayılmaz |
| `IAnalyticsSink` / `NullAnalyticsSink` | Analitik geçidi + no-op varsayılan. `AnalyticsEvents.SESSIZ_TOPARLANMA` premium P5 gereği sabit satırdır |
| `IAdGateway` / `NullAdGateway` | Reklam geçidi + reklamsız varsayılan; R1 tempo kuralları oyun tarafında yapılandırılır |

Somut sağlayıcılar (GameAnalytics, AppLovin MAX) çekirdeğe **girmez** — oyun reposu
kendi uyarlayıcısını takar. Çekirdek yalnız sözleşmeyi ve güvenli varsayılanı taşır.

## Depo şeması kararı (0A adım 3)

**Karar:** UPM paketi **repo kökünde** (`package.json` kökte), oyun iskeleti aynı
repoda `templates/` altında.

**Gerekçe:** tek repo = tek sürüm etiketi; `templates/` ile onu besleyen çekirdek aynı
etikette donar, sürüm kayması olmaz (L4'ün "UPM tam-repo klonu şişmesin" kaygısı,
oyun deposunun fabrika deposunu klonlamamasıyla zaten karşılanıyor).

**Bilinen yan etki (ölçülmüş, gizlenmiyor):** paket kökte olduğu için UPM git-URL ile
çekildiğinde **repo içeriğinin tamamı** (dolayısıyla `templates/`) paket olarak
`Library/PackageCache` altına kopyalanır. `templates/` küçük tutulduğu sürece maliyet
kabul edilebilir; büyürse iki seçenek vardır:
1. UPM alt dizin desteği: `…factory.core.git?path=/Runtime#v0.x` — paket kökten ayrılır;
2. `templates/` dizinini Unity'nin göz ardı ettiği `templates~/` adına almak.

Bu bir **açık borç kaydıdır**; seçim mimarındır (kural 22).

## Sürümleme

`v0.x` serisi; etiket bu repoda serbesttir (0A yetki genelgesi). Etiket = UPM bağının
tek referansı olduğu için geriye dönük etiket taşınmaz — yeni sürüm yeni etiket alır.
