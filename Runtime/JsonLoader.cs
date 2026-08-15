using System;
using System.IO;
using UnityEngine;

namespace FactoryGames.Core
{
    /// <summary>
    /// Ayarlarin tek kaynagi StreamingAssets JSON'udur (Sozlesme-2; ScriptableObject
    /// yasak — kod-standardi §4). Okunamazsa SESSIZ varsayim yapilmaz (kural 6):
    /// cagiran taraf kaynagi metin olarak alir ve raporlar.
    /// </summary>
    public static class JsonLoader
    {
        /// <summary>Android'de StreamingAssets jar icindedir; File API ile okunamaz.</summary>
        public static bool NeedsWebRequest =>
            Application.streamingAssetsPath.Contains("://") ||
            Application.platform == RuntimePlatform.Android;

        public static string PathFor(string fileName) =>
            Path.Combine(Application.streamingAssetsPath, fileName).Replace("\\", "/");

        /// <summary>
        /// Dosya sisteminden okur (Editor, masaustu, iOS). Android icin
        /// <see cref="FromJson{T}"/> ile UnityWebRequest govdesi birlestirilir.
        /// </summary>
        public static T Load<T>(string fileName, out string source) where T : class
        {
            string path = PathFor(fileName);
            try
            {
                if (NeedsWebRequest)
                {
                    source = "OKUNAMADI (bu platformda UnityWebRequest gerekir: " + path + ")";
                    return null;
                }
                if (!File.Exists(path))
                {
                    source = "OKUNAMADI (dosya yok: " + path + ")";
                    return null;
                }
                T value = FromJson<T>(File.ReadAllText(path));
                source = value != null ? path : "OKUNAMADI (JSON cozumlendi ama bos dondu: " + path + ")";
                return value;
            }
            catch (Exception ex)
            {
                source = "OKUNAMADI (" + ex.GetType().Name + ": " + ex.Message + ")";
                return null;
            }
        }

        public static T FromJson<T>(string json) where T : class
        {
            if (string.IsNullOrWhiteSpace(json)) return null;
            return JsonUtility.FromJson<T>(json);
        }
    }
}
