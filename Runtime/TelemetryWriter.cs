using System;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;

namespace FactoryGames.Core
{
    /// <summary>Kapi sonucu kumesi — ilk-kosu.md §1: "veri yok" GECTI sayilmaz.</summary>
    public enum GateResult
    {
        gecti,
        kaldi,
        veri_yok
    }

    /// <summary>
    /// PIPELINE Sozlesme-1 telemetri satiri. Alanlar SABIT: {ts, asama, olay, sure_dk,
    /// kapi_sonucu, insan_saat, factory_core_surumu, build_hash, ci_dakika}.
    /// Satir JSONL olarak `.factory/telemetry.jsonl`e eklenir (append-only).
    ///
    /// Kultur bagimsizligi ZORUNLU (sonda §7.5 bulgusu: tr-TR ondalik ayiraci
    /// olcum alanlarina siziyordu) — tum sayilar InvariantCulture ile yazilir.
    /// </summary>
    public static class TelemetryWriter
    {
        public const string RELATIVE_PATH = ".factory/telemetry.jsonl";

        public static string Compose(string asama, string olay, double sureDk,
                                     GateResult? kapiSonucu, double insanSaat,
                                     string factoryCoreSurumu, string buildHash,
                                     double ciDakika, bool serhli = false)
        {
            var inv = CultureInfo.InvariantCulture;
            var sb = new StringBuilder(256);
            sb.Append('{');
            sb.Append("\"ts\":\"").Append(DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ", inv)).Append("\",");
            sb.Append("\"asama\":\"").Append(Escape(asama)).Append("\",");
            sb.Append("\"olay\":\"").Append(Escape(olay)).Append("\",");
            sb.Append("\"sure_dk\":").Append(sureDk.ToString("0.###", inv)).Append(',');
            sb.Append("\"kapi_sonucu\":").Append(kapiSonucu.HasValue
                ? "\"" + kapiSonucu.Value + "\"" : "null").Append(',');
            sb.Append("\"insan_saat\":").Append(insanSaat.ToString("0.###", inv)).Append(',');
            sb.Append("\"factory_core_surumu\":\"").Append(Escape(factoryCoreSurumu)).Append("\",");
            sb.Append("\"build_hash\":\"").Append(Escape(buildHash)).Append("\",");
            sb.Append("\"ci_dakika\":").Append(ciDakika.ToString("0.###", inv));
            if (serhli) sb.Append(",\"serhli\":true");
            sb.Append('}');
            return sb.ToString();
        }

        /// <summary>Satiri projenin `.factory/telemetry.jsonl` dosyasina ekler.</summary>
        public static void Append(string line, string projectRoot = null)
        {
            string root = projectRoot ?? Directory.GetCurrentDirectory();
            string path = Path.Combine(root, RELATIVE_PATH);
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.AppendAllText(path, line + "\n", new UTF8Encoding(false));
        }

        private static string Escape(string s)
        {
            if (string.IsNullOrEmpty(s)) return string.Empty;
            return s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", " ").Replace("\r", " ");
        }
    }
}
