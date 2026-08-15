using UnityEngine;

namespace FactoryGames.Core
{
    /// <summary>
    /// Kod-oncelikli sahne kurulumunun paylasilan iskeleti (Sozlesme-2): sahne dosyasi
    /// sablon varsayilani olarak KALIR, hiyerarsi runtime'da kurulur.
    ///
    /// Bu sinif OYUN BILGISI ICERMEZ; yalnizca her oyunda tekrar eden uc isi yapar:
    /// kok nesne, kamera ve idempotenlik. Oyun kendi
    /// [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    /// metodunu yazar ve buradaki yardimcilari cagirir.
    ///
    /// `GameObject.Find` / `FindFirstObjectByType` / `Camera.main` KULLANILMAZ
    /// (kural 8): referanslar kurulum aninda ACIK atanir, cagirana dondurulur.
    /// </summary>
    public static class RuntimeInitBootstrap
    {
        /// <summary>Sahne yuklemeleri arasinda yasayan kok nesneyi kurar (idempotent).</summary>
        public static GameObject CreateRoot(string name)
        {
            var root = new GameObject(string.IsNullOrEmpty(name) ? "FactoryRoot" : name);
            Object.DontDestroyOnLoad(root);
            return root;
        }

        /// <summary>
        /// Ortografik kamerayi kurar. Sahnedeki sablon kamerasina DOKUNULMAZ; bu kamera
        /// daha yuksek `depth` ile onun ustune cizer — sahne dosyasi degismeden kalir.
        /// </summary>
        public static Camera CreateOrthographicCamera(Transform parent, float halfHeight,
                                                      Color background, float depth = 10f)
        {
            var go = new GameObject("FactoryCamera");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(0f, 0f, -10f);

            var cam = go.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = halfHeight;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = background;
            cam.depth = depth;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 100f;
            return cam;
        }

        /// <summary>
        /// Guvenli alan (centik/delik) dikkate alinarak normalize edilmis yerlesim
        /// dikdortgeni. Ham Pos X/Y tek cihazdan yazilmaz (kod-standardi §3): arayuz
        /// kokleri bu dikdortgene oturur (Ek C `ekran_centik_varsayimi`).
        /// </summary>
        public static Rect SafeAreaNormalized()
        {
            Rect safe = Screen.safeArea;
            float w = Screen.width <= 0 ? 1f : Screen.width;
            float h = Screen.height <= 0 ? 1f : Screen.height;
            return new Rect(safe.x / w, safe.y / h, safe.width / w, safe.height / h);
        }
    }
}
