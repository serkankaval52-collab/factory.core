# factory.core

FactoryGames hattının **paylaşılan çalışma zamanı çekirdeği** (UPM paketi) ve
**oyun reposu iskeleti** (`templates~/`).

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

## Depo şeması kararı (0A adım 3 — KAPANDI, v1.4.1)

**Karar:** UPM paketi **repo kökünde** (`package.json` kökte), oyun iskeleti aynı repoda
**`templates~/`** altında. Unity, adı `~` ile biten dizinleri içe aktarmaz; böylece paket
kökte kalırken iskelet oyun projesine **hiç ithal edilmez** (sıfır ithalat maliyeti),
ama `git` için sıradan bir dizin olduğundan sürümlenmeye ve etiketlenmeye devam eder.

`?path=/Runtime` alternatifi **reddedildi**: repoyu yeniden yapılandırmayı ve her
tüketicinin bağ satırını değiştirmesini gerektirirken `~` ile aynı sonucu veriyordu.

Böylece "paket kökte olduğu için tüm repo `PackageCache`'e kopyalanıyor" borcu kapandı:
kopyalanan içerik artık Unity tarafından **görünmez** ve derlemeye girmez.

## Oyun reposunu şablondan kurma (scaffold)

İskelet, oyun projesinin `Library/PackageCache` altındaki paket kopyasından alınır.
**Sihirli yol yazılmaz** — paket dizini sürüm/hash sonekiyle geldiği için yol çözülür.

**Yol A — Editor script (PackageManager API; en güvenilir):**

```csharp
using UnityEditor.PackageManager;                 // Editor/ altinda gecici bir script
var info = PackageInfo.FindForPackageName("com.factorygames.core");
Debug.Log(info.resolvedPath);                     // .../PackageCache/com.factorygames.core@<hash>
// iskelet: {resolvedPath}/templates~
```

**Yol B — kabuk globu (Unity açmadan):**

```powershell
# Windows / PowerShell — oyun reposunun kokunde
$pkg = Get-ChildItem Library/PackageCache -Directory -Filter 'com.factorygames.core@*' |
       Select-Object -First 1
robocopy "$($pkg.FullName)/templates~" . /E /XD .git
```

```bash
# macOS / Linux
src=$(echo Library/PackageCache/com.factorygames.core@*/templates~)
cp -R "$src"/. .
```

Kopyalama sonrası `Packages/manifest.json` içindeki `#v0.x` etiketi, oyunun pinlendiği
sürüme sabitlenir.

## Sürümleme

`v0.x` serisi; etiket bu repoda serbesttir (0A yetki genelgesi). Etiket = UPM bağının
tek referansı olduğu için geriye dönük etiket taşınmaz — yeni sürüm yeni etiket alır.
