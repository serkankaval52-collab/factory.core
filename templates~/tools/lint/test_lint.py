#!/usr/bin/env python3
"""Lint'in KENDI dogrulugunun testi — "kapi gercekten olcuyor mu?"

Gerekce (0A adim 3 / V3): esiklerin gercek bir oyunda tutup tutmadigi ancak gercek
varlikla olculur ve o olcum bu kosuda YAPILAMADI (kullanici karari: elde yalnizca
acemi donem oyunu vardi, yanlis orneklem olurdu — dusuk oran esigi degil o oyunu
yargilardi). Yerine olcum ARACININ dogrulugu kanitlanir: lint bilinen-dogru
degerlerde yesil, bilinen-kotu degerlerde KIRMIZI vermeli.

Once-kirmizi disiplini (Sozlesme-5): her kapi icin hem gecen hem KALAN ornek vardir;
kapi her zaman yesil yanan bir susleme degildir.

Kosum: python tools/lint/test_lint.py   (harici bagimlilik yok)
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

import lint_varlik as LV  # noqa: E402


class KontrastMatematigi(unittest.TestCase):
    """G4 — WCAG formulunun dis kaynakla dogrulanmasi (referans degerler WCAG 2.x)."""

    def test_siyah_beyaz_21e1(self):
        oran = LV.kontrast(LV.hex_rgb("#000000"), LV.hex_rgb("#FFFFFF"))
        self.assertAlmostEqual(oran, 21.0, places=2)

    def test_gri_beyaz_bilinen_deger(self):
        # #767676 uzerinde beyaz: WCAG AA metin esiginin (4.5) hemen ustu — kanonik ornek
        oran = LV.kontrast(LV.hex_rgb("#767676"), LV.hex_rgb("#FFFFFF"))
        self.assertGreaterEqual(oran, 4.5)
        self.assertLess(oran, 5.0)

    def test_ayni_renk_1e1(self):
        oran = LV.kontrast(LV.hex_rgb("#3366CC"), LV.hex_rgb("#3366CC"))
        self.assertAlmostEqual(oran, 1.0, places=6)


class RenkKorluguAyrimi(unittest.TestCase):
    """G6 — simulasyonun GERCEKTEN ayirt ettigi kanit."""

    def test_kirmizi_yesil_orani_dusuk(self):
        """WCAG orani bu cifti yakalar (kayit: dE00 yakalamiyor — asagidaki teste bak)."""
        kirmizi, yesil = LV.hex_rgb("#D40000"), LV.hex_rgb("#00A000")
        self.assertLess(LV.kontrast(kirmizi, yesil), 3.0)

    def test_kirmizi_yesil_deltae_kapiyi_GECER_bilinen_sinir(self):
        """KAPININ BILINEN SINIRI — belgelenmis, gizlenmemis olsun diye test.

        v1.4.1 karariyla tehlike<->vurgu cifti WCAG oranindan CIEDE2000'e tasindi.
        Olcum (0A-3): klasik kirmizi-yesil cifti dE00 kapisindan GECIYOR —
        normal 73.70, protanopi 21.20, doteranopi 44.91, tritanopi 47.32; hicbiri
        2.0'in altina inmiyor. Sebep: buradaki CVD matrisleri (Brettel/Vienot
        yaklasimi) iki rengi tam BIRLESTIRMIYOR, parlaklik/kroma farki koruyor.

        Sonuc: mekanik kapi bu klasik karisikligi YAKALAMAZ; G6'nin ek kurali
        (renk tek basina bilgi tasiyamaz — bicim/ikon destegi ZORUNLU) bu yuzden
        vazgecilmezdir. Test, sinirin sessizce unutulmamasi icin vardir.
        """
        kir, yes = LV.hex_rgb("#D40000"), LV.hex_rgb("#00A000")
        for t in ("protanopi", "doteranopi", "tritanopi"):
            self.assertGreaterEqual(
                LV.delta_e(LV.cvd_uygula(kir, t), LV.cvd_uygula(yes, t)), 2.0,
                f"{t}: olcum degisti — kapinin sinir kaydi guncellenmeli")

    def test_ciede2000_referans_verisi(self):
        """CIEDE2000 dogrulugu — Sharma-Wu-Dalal (2005) yayinlanmis test cifleri.

        Not (durustluk kaydi): ilk denemede Pair 8 ile Pair 12 karistirilarak yanlis
        beklenen deger yazilmis ve implementasyon hatali sanilmisti; dogru esleme ile
        besi de birebir tutuyor.
        """
        for lab1, lab2, beklenen in [
            ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
            ((50.0, 2.49, -0.001), (50.0, -2.49, 0.0009), 7.1792),
            ((50.0, -0.001, 2.49), (50.0, 0.0009, -2.49), 4.8045),
            ((50.0, 0.0, 0.0), (50.0, -1.0, 2.0), 2.3669),
            ((50.0, 2.5, 0.0), (73.0, 25.0, -18.0), 27.1492),
        ]:
            self.assertAlmostEqual(LV.ciede2000(lab1, lab2), beklenen, places=3)

    def test_mavi_sari_protanopide_ayrik_kalir(self):
        mavi, sari = LV.hex_rgb("#0050C8"), LV.hex_rgb("#FFD200")
        prot = LV.kontrast(LV.cvd_uygula(mavi, "protanopi"),
                           LV.cvd_uygula(sari, "protanopi"))
        self.assertGreater(prot, 3.0,
                           "mavi-sari cifti protanopide de ayrik kalmaliydi")


class KapiUctanUca(unittest.TestCase):
    """Kapinin surec olarak once-KIRMIZI, sonra yesil verdigi kanit."""

    ESIKLER = {
        "gorsel_palet_kademe": 5,
        "gorsel_kontrast_ana_ozne": 3.0,
        "gorsel_kontrast_ui_metin": 4.5,
        "gorsel_sinyal_deltae_min": 2.0,
        "gorsel_anim_kare_band": [4, 12],
        "gorsel_anim_dongu_ortusme": 90,
        "gorsel_alpha_sacak_yuzde": 2,
        "gorsel_atlas_doluluk_yuzde": 70,
        "ses_lufs_band": [-17, -15],
        "ses_tepe_dbtp": -1,
        "ses_sfx_sure_tavan_sn": 2,
        "uygulama_boyut_tavan_mb": 150,
    }

    # DOYGUN palet — v1.4.1 kararinin sinavi. Bu palet WCAG-oran kapisinda (eski G6)
    # tehlike/vurgu yuzunden 4/4 DUSUYORDU; dE00 kapisinda GECMELI. Olculdu (0A-3):
    #   tehlike/vurgu dE00 -> normal 49.42 · prot 15.23 · dote 10.70 · trit 2.55
    #   tehlike/arka  oran -> prot 8.79 · dote 10.91 · trit 5.70
    #   ana_ozne/arka oran -> prot 5.46 · dote 4.50 · trit 11.51
    # Yani karar, doygun paleti serbest birakti; desature zorlamasi kalkti.
    IYI_PALET = {"roller": {
        "arka_plan": "#101418", "ana_ozne": "#40D0F0", "vurgu": "#FFD200",
        "tehlike": "#FF5A5A", "ui_metin": "#FFFFFF", "ui_zemin": "#101418"}}

    KOTU_PALET = {"roller": {
        "arka_plan": "#808080", "ana_ozne": "#8A8A8A", "vurgu": "#8F8F8F",
        "tehlike": "#949494", "ui_metin": "#9A9A9A", "ui_zemin": "#808080"}}

    def _kos(self, palet):
        with tempfile.TemporaryDirectory() as kok:
            sa = os.path.join(kok, "Assets", "StreamingAssets")
            os.makedirs(sa)
            with open(os.path.join(sa, "palette.json"), "w", encoding="utf-8") as f:
                json.dump(palet, f)
            r = LV.Rapor()
            LV.kapi_palet(kok, self.ESIKLER, r)
            return r

    def test_iyi_palet_yesil(self):
        r = self._kos(self.IYI_PALET)
        self.assertEqual(r.kirmizi, 0, "gecerli palet kirmizi verdi")

    def test_kotu_palet_KIRMIZI(self):
        r = self._kos(self.KOTU_PALET)
        self.assertGreater(r.kirmizi, 0,
                           "ayirt edilemeyen gri palet YESIL gecti — kapi olcmuyor")

    def test_ayirt_edilemeyen_sinyal_cifti_KIRMIZI(self):
        """Once-kirmizi: dE00 kapisi gercekten kirmizi verebiliyor mu?

        tehlike ile vurgu birbirine cok yakin secilirse (dE00 1.20) kapi KIRMIZI
        vermeli — yoksa kapi her zaman yesil yanan bir susleme olurdu.
        """
        palet = {"roller": {
            "arka_plan": "#101418", "ana_ozne": "#40D0F0",
            "vurgu": "#E74C3C", "tehlike": "#E85142",   # dE00 = 1.20
            "ui_metin": "#FFFFFF", "ui_zemin": "#101418"}}
        r = self._kos(palet)
        de_satirlari = [s for s in r.satirlar if s[0] == "G6-dE"]
        self.assertTrue(any(s[1] == "KIRMIZI" for s in de_satirlari),
                        "ayirt edilemeyen sinyal cifti YESIL gecti — dE00 kapisi olcmuyor")

    def test_doygun_mavi_turuncu_dort_goruste_YESIL(self):
        """Yanlis-pozitif testi: gercekten ayrik bir doygun cift kapiyi gecmeli."""
        mavi, turuncu = LV.hex_rgb("#1E5AFF"), LV.hex_rgb("#FF7A1E")
        self.assertGreaterEqual(LV.delta_e(mavi, turuncu), 2.0, "normal gorus")
        for t in ("protanopi", "doteranopi", "tritanopi"):
            self.assertGreaterEqual(
                LV.delta_e(LV.cvd_uygula(mavi, t), LV.cvd_uygula(turuncu, t)), 2.0, t)

    def test_deltae_esigi_yoksa_veri_yok(self):
        """Kural 28: esik yoksa tahmin uretilmez, kapi 'gecti' de sayilmaz."""
        esikler = dict(self.ESIKLER)
        esikler.pop("gorsel_sinyal_deltae_min")
        with tempfile.TemporaryDirectory() as kok:
            sa = os.path.join(kok, "Assets", "StreamingAssets")
            os.makedirs(sa)
            with open(os.path.join(sa, "palette.json"), "w", encoding="utf-8") as f:
                json.dump(self.IYI_PALET, f)
            r = LV.Rapor()
            LV.kapi_palet(kok, esikler, r)
            de = [s for s in r.satirlar if s[0] == "G6-dE"]
            self.assertTrue(de and de[0][1] == "VERI-YOK", "eksik esik sessizce gecti")
            self.assertTrue(de[0][3], "VERI-YOK satiri kanitsiz")

    def test_palet_yoksa_veri_yok_ve_kanit(self):
        with tempfile.TemporaryDirectory() as kok:
            r = LV.Rapor()
            LV.kapi_palet(kok, self.ESIKLER, r)
            durumlar = [s[1] for s in r.satirlar]
            self.assertIn("VERI-YOK", durumlar, "eksik girdi sessizce gecti")
            self.assertEqual(r.kirmizi, 0)
            self.assertTrue(any(s[3] for s in r.satirlar), "VERI-YOK satiri kanitsiz")


class LintSurecKontrolu(unittest.TestCase):
    """lint.py'nin ihlali gercekten KIRMIZI yaptigi kanit (surec cikis kodu)."""

    def test_baseline_asimi_kirmizi(self):
        with tempfile.TemporaryDirectory() as kok:
            os.makedirs(os.path.join(kok, "Assets", "Scenes"))
            os.makedirs(os.path.join(kok, "tools", "lint"))
            with open(os.path.join(kok, "scene-baseline.json"), "w", encoding="utf-8") as f:
                json.dump({"pin": "test", "dosya": "x", "sha256": "y", "nesne_sayisi": 2}, f)
            with open(os.path.join(kok, "tools", "lint", "esikler.json"), "w", encoding="utf-8") as f:
                json.dump({"uygulama_boyut_tavan_mb": 150}, f)
            # 40 nesneli sahne — 0A adim 5'in (a) kasitli ihlalinin birebir karsiligi
            with open(os.path.join(kok, "Assets", "Scenes", "S.unity"), "w", encoding="utf-8") as f:
                f.write("GameObject:\n" * 40)

            p = subprocess.run([sys.executable, os.path.join(BURASI, "lint.py"), "--kok", kok],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 1, "baseline asimi kirmizi vermedi\n" + p.stdout)
            self.assertIn("SAHNE-BASELINE", p.stdout)

    def test_temiz_agac_yesil(self):
        with tempfile.TemporaryDirectory() as kok:
            os.makedirs(os.path.join(kok, "Assets", "Scenes"))
            os.makedirs(os.path.join(kok, "tools", "lint"))
            with open(os.path.join(kok, "scene-baseline.json"), "w", encoding="utf-8") as f:
                json.dump({"pin": "test", "dosya": "x", "sha256": "y", "nesne_sayisi": 2}, f)
            with open(os.path.join(kok, "tools", "lint", "esikler.json"), "w", encoding="utf-8") as f:
                json.dump({"uygulama_boyut_tavan_mb": 150}, f)
            with open(os.path.join(kok, "Assets", "Scenes", "S.unity"), "w", encoding="utf-8") as f:
                f.write("GameObject:\nGameObject:\n")

            p = subprocess.run([sys.executable, os.path.join(BURASI, "lint.py"), "--kok", kok],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, "temiz agac kirmizi verdi\n" + p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
