using System;

namespace FactoryGames.Core
{
    /// <summary>
    /// Analitik gecidi. Somut saglayici (GameAnalytics vb.) fabrika cekirdegine
    /// GIRMEZ — oyun reposu kendi uyarlayicisini takar. Cekirdek yalnizca sozlesmeyi
    /// ve guvenli varsayilani tasir.
    ///
    /// `sessiz_toparlanma` olayi premium-sozlesme P5 geregi ZORUNLU sabit satirdir:
    /// oyuncudan gizlenen bizden gizlenmez; Asama 10 raporu bunu AYRI sayar.
    /// </summary>
    public interface IAnalyticsSink
    {
        void Event(string name);
        void Event(string name, string key, string value);
    }

    /// <summary>Saglayici takilmadan once kullanilan sessiz varsayilan (cokme yerine no-op).</summary>
    public sealed class NullAnalyticsSink : IAnalyticsSink
    {
        public static readonly NullAnalyticsSink Instance = new NullAnalyticsSink();
        public void Event(string name) { }
        public void Event(string name, string key, string value) { }
    }

    /// <summary>Sozlesmenin sabit olay adlari — kod ile manifest arasindaki tek kaynak.</summary>
    public static class AnalyticsEvents
    {
        public const string SESSIZ_TOPARLANMA = "sessiz_toparlanma";
        public const string BOOT_TAMAM = "boot_tamam";
        public const string TUR_BASLADI = "tur_basladi";
        public const string TUR_BITTI = "tur_bitti";
    }

    /// <summary>
    /// Reklam gecidi. R1 tempo kurallari (Ek C `reklam_siklik_tavan`,
    /// `reklam_arasi_min_sn`, `reklam_ilk_gun_sifir_turler`) OYUN tarafinda
    /// yapilandirilir; cekirdek yalnizca cagri yuzeyini ve "gosterilemedi" yolunu tanimlar.
    /// </summary>
    public interface IAdGateway
    {
        bool IsInterstitialReady { get; }
        void ShowInterstitial(Action<bool> onClosed);
    }

    /// <summary>Reklamsiz varsayilan: her zaman "gosterilmedi" doner, oyun akisi durmaz.</summary>
    public sealed class NullAdGateway : IAdGateway
    {
        public static readonly NullAdGateway Instance = new NullAdGateway();
        public bool IsInterstitialReady => false;
        public void ShowInterstitial(Action<bool> onClosed) => onClosed?.Invoke(false);
    }
}
