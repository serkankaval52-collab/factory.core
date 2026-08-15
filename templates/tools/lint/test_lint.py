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

    def test_kirmizi_yesil_cifti_esigi_gecemez(self):
        """Klasik kirmizi-yesil ciftini G6 REDDETMELI.

        SAHA DUZELTMESI (0A): ilk yazimda "protanopide kontrast DUSER" varsayilmisti;
        olculdu ve YANLIS cikti — WCAG kontrasti parlaklik farkina bakar, simulasyon
        parlaklik degistirdigi icin oran ARTABILIR (D40000/00A000: normal 1.59,
        protanopi 2.02, doteranopi 3.77). Kapinin gercek gucu baska yerde: bu cift
        NORMAL goruste zaten esigin altindadir; "renk TEK BASINA bilgi tasiyamaz"
        (G6 ek kurali) ilkesinin sayisal karsiligi budur.
        """
        kirmizi, yesil = LV.hex_rgb("#D40000"), LV.hex_rgb("#00A000")
        self.assertLess(LV.kontrast(kirmizi, yesil), 3.0,
                        "kirmizi-yesil cifti normal goruste esigi gecmemeliydi")
        dusuk = [t for t in ("protanopi", "doteranopi", "tritanopi")
                 if LV.kontrast(LV.cvd_uygula(kirmizi, t), LV.cvd_uygula(yesil, t)) < 3.0]
        self.assertTrue(dusuk, "hicbir simulasyonda esigin altina inmedi")

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
        "gorsel_anim_kare_band": [4, 12],
        "gorsel_anim_dongu_ortusme": 90,
        "gorsel_alpha_sacak_yuzde": 2,
        "gorsel_atlas_doluluk_yuzde": 70,
        "ses_lufs_band": [-17, -15],
        "ses_tepe_dbtp": -1,
        "ses_sfx_sure_tavan_sn": 2,
        "uygulama_boyut_tavan_mb": 150,
    }

    # Bu palet TARAMAYLA bulundu, elle secilmedi (0A adim 3 / V3 yerine gecen olcum):
    # ilk sezgisel aday (#101418/#40D0F0/#FFD200/#FF5A5A) uc simulasyonda da DUSTU —
    # tehlike/vurgu ikisi de parlak oldugu icin oran 1.04-2.11 bandinda kaldi.
    # Gecen palet dusuk doygunluklu tonlar kullanir; ayrinti:
    # FactoryGames docs/factory/verification/03-v3-esik-saglamasi.md
    IYI_PALET = {"roller": {
        "arka_plan": "#1A0D0D", "ana_ozne": "#4C998C", "vurgu": "#FFD480",
        "tehlike": "#994C4C", "ui_metin": "#FFFFFF", "ui_zemin": "#1A0D0D"}}

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
