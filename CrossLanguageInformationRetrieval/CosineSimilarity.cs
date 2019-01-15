using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CrossLanguageInformationRetrieval
{
    class CosineSimilarity
    {
        public Dictionary<string, double> CosSim(Dictionary<int, Dictionary<string, double>> normDocument, Dictionary<int, Dictionary<string, double>> normQuery, string[,] document, string[,] query)
        {
            Dictionary<string, double> cosSim = new Dictionary<string, double>();
            var temporary = normQuery;

            for (int i = 0; i < document.GetLength(0); i++)
            {
                cosSim.Add(document[i, 1], 0);
            }
            var qTemp = new Dictionary<string, double>();
            foreach (var norm in normQuery.ToList())
            {
                foreach (var w in norm.Value.ToList())
                {
                    qTemp.Add(w.Key, w.Value);
                }
            }
            Parallel.ForEach(normDocument.ToList(), (norm) =>
            {
                double temp = 0;
                Parallel.ForEach(norm.Value.ToList(), (w) =>
                {
                    double value;
                    bool exists = qTemp.TryGetValue(w.Key, out value);
                    if (exists)
                    {
                        temp += w.Value * value;
                    }
                });
                cosSim[cosSim.ElementAt(norm.Key).Key] = temp;
            });
            return cosSim;
        }
    }
}
