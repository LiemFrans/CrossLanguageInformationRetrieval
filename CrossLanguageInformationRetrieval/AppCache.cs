using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CrossLanguageInformationRetrieval
{
    class AppCache
    {
        public static string API { get; } = @"trnsl.1.1.20180426T022437Z.b834425af9e5f09c.e858b7e59c8423292047102e9fb2981894b890b5";
        public static string UrlGetAvailableLanguages { get; } = @"https://translate.yandex.net/api/v1.5/tr.json/getLangs?key={0}&ui={1}";
        public static string UrlDetectSrcLanguage { get; } = @"https://translate.yandex.net/api/v1.5/tr.json/detect?key={0}&text={1}";
        public static string UrlTranslateLanguage { get; } = @"https://translate.yandex.net/api/v1.5/tr.json/translate?key={0}&text={1}&lang={2}";

    }
}
