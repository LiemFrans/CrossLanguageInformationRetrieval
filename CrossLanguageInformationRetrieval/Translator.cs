using Newtonsoft.Json;
using RestSharp;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CrossLanguageInformationRetrieval
{
    class Translator
    {
        public string translate(string word)
        {
            var response = RequestService(string.Format(AppCache.UrlDetectSrcLanguage, AppCache.API, word));
            var dict = JsonConvert.DeserializeObject<IDictionary>(response.Content);
            var statusCode = dict["code"].ToString();
            string lang = null;
            if (statusCode.Equals("200"))
            {
                lang = dict["lang"].ToString();
                if (lang != "en" && lang != "id")
                {
                    lang = "id";
                }
            }
            response = null;
            dict = null;
            statusCode = null;
            var language = new string[,] { { "en","id","es","zh" }, { "id","en","es","zh" }, { "es","en","id","zh"},{ "zh","en","id","es"}};
            string text = null;
            for(int i = 0;i < language.GetLength(0); i++)
            {
                if(lang == language[i, 0])
                {
                    for(int j = 1; j < language.GetLength(1); j++)
                    {
                        response = RequestService(string.Format(AppCache.UrlTranslateLanguage, AppCache.API, word, language[i, j]));
                        dict = JsonConvert.DeserializeObject<IDictionary>(response.Content);
                        statusCode = dict["code"].ToString();
                        string temp = null;
                        if (statusCode.Equals("200"))
                        {
                            temp = string.Join(",", dict["text"]);
                            temp = temp.Remove(0, 6);
                            temp = temp.Remove(temp.Length - 4, 4);
                        }
                        text += temp+" ";
                    }
                }
            }
          
            return text;
        }

        private IRestResponse RequestService(string strUrl)
        {
            var client = new RestClient()
            {
                BaseUrl = new Uri(strUrl)
            };
            var request = new RestRequest()
            {
                Method = Method.GET
            };
            return client.Execute(request);
        }
    }
}
