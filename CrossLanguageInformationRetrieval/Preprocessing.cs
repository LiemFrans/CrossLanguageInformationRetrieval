using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace CrossLanguageInformationRetrieval
{
    class Preprocessing
    {
        private NaziefAndrianStemmer idStemmer;
        private PorterStemmer enStemmer;
        private JesusUtreraStemmer esStemmer;
        private string[] rootwords;
        private string[] stopwords;
        private List<string> term;
        public Preprocessing()
        {
            //this.clirForm = clirForm;
            stopwords = File.ReadLines("stopwords.txt").Cast<string>().ToArray();
            rootwords = File.ReadLines("rootwords.txt").Cast<string>().ToArray();
            idStemmer = new NaziefAndrianStemmer(rootwords);
            enStemmer = new PorterStemmer();
            esStemmer = new JesusUtreraStemmer();
        }

        //[indexdoc, [words, frequency]]
        public Dictionary<int, Dictionary<string,int>> termFrequency(string[,] document)
        {
            var termFrequency = new Dictionary<int, Dictionary<String, int>>();
            var token = tokenize(document);
            term = medStem(token);
            term = removeStopword(term);
            term = removeDuplicate(term);
            for (int i = 0; i < document.GetLength(0); i++)
            {
                var matching = Regex.Matches(document[i, 1].ToLower(), @"((\b[^\s]+\b)((?<=\.\w).)?)");
                var matches = new List<string>();
                foreach (var mt in matching)
                {
                    if (IsChinese(mt.ToString()))
                    {
                        char[] characters = mt.ToString().ToCharArray();
                        foreach (var ch in characters)
                        {
                            if (!Char.IsPunctuation(ch)||stopwords.ToList().Contains(ch.ToString()))
                            {
                                matches.Add(ch.ToString());
                            }
                        }
                    }
                    else
                    {
                        string temp = mt.ToString().Replace(",", "");
                        matches.Add(temp);
                    }
                }
                var doc = new Dictionary<string, int>();
                foreach (string t in term)
                {
                    doc.Add(t, 0);
                }
                matches = medStem(matches);
                matches = removeStopword(matches);
                Parallel.ForEach(matches, (w) => {
                    if (term.Contains(w))
                    {
                        doc[w]++;
                    }
                });
                termFrequency.Add(i, doc);
            }
            return termFrequency;
        }

        //[words, frequency]
        public Dictionary<string, int> documentFrequency(Dictionary<int, Dictionary<string, int>> termFreq)
        {
            var documentFrequency = new Dictionary<string, int>();
            term = removeStopword(term);
            foreach (var t in term)
            {
                documentFrequency.Add(t, 0);
            }
            Parallel.ForEach(termFreq, (doc) =>
            {
                Parallel.ForEach(doc.Value, (w) => {
                    if (documentFrequency.ContainsKey(w.Key))
                    {
                        if (w.Value > 0)
                        {
                            documentFrequency[w.Key]++;
                        }
                    }
                });
            });
            return documentFrequency;
        }

        public Dictionary<string, double> idft(Dictionary<string,int> docFreq, int lengthDoc)
        {
            var idft = new Dictionary<string, double>();
            foreach (var df in docFreq) idft.Add(df.Key,0);
            Parallel.ForEach(docFreq, (df) =>
            {
                idft[df.Key] = (Math.Log10(lengthDoc / df.Value)+1);
            });
            return idft;
        }

        public Dictionary<int, Dictionary<string, double>> wtf(Dictionary<int, Dictionary<string, int>> termFreq)
        {
            var wtf = new Dictionary<int, Dictionary<string, double>>();

            foreach (var tf in termFreq)
            {
                var doc = new Dictionary<string, double>();
                foreach (var w in tf.Value)
                {
                    doc.Add(w.Key, 0);
                }
                Parallel.ForEach(tf.Value, (w) => {
                    if (w.Value == 0)
                    {
                        doc[w.Key] = 0;
                    }
                    else
                    {
                        doc[w.Key] = (Math.Log10(w.Value))+1;
                    }
                });
                wtf.Add(tf.Key, doc);
            }
            return wtf;
        }
        
        public Dictionary<int, Dictionary<string, double>> wtd(Dictionary<int, Dictionary<string, double>> wtfreq, Dictionary<string,double> idft)
        {
            var wtd = new Dictionary<int, Dictionary<string, double>>();
            foreach(var wtf in wtfreq)
            {
                var doc = new Dictionary<string, double>();
                foreach (var w in wtf.Value)
                {
                    doc.Add(w.Key, 0);
                }
                var key = new List<string>(wtf.Value.Keys);
                key = removeStopword(key);
                Parallel.ForEach(wtf.Value, (w) =>
                {
                    if (key.Contains(w.Key))
                    {
                        doc[w.Key] = w.Value * idft[w.Key];
                    }
                });
                wtd.Add(wtf.Key, doc);
            }
            return wtd;
        }

        public Dictionary<int, Dictionary<string, double>> normalization(Dictionary<int, Dictionary<string, double>> wtdoc)
        {
            var normalization = new Dictionary<int, Dictionary<string, double>>();
            foreach (var wtd in wtdoc)
            {
                var doc = new Dictionary<string, double>();
                foreach(var w in wtd.Value)
                {
                    doc.Add(w.Key, 0);
                }
                double temp = 0;
                Parallel.ForEach(wtd.Value, (w) => {
                    temp += Math.Pow(w.Value, 2);
                });
                temp = Math.Sqrt(temp);
                Parallel.ForEach(wtd.Value, (w) => {
                if (w.Value == 0 || temp == 0)
                {
                    doc[w.Key] = 0;
                }
                else
                {
                    doc[w.Key] = (w.Value) / (temp);
                    }
                });
                normalization.Add(wtd.Key, doc);
            }
            return normalization;
        }

        private List<string> removeStopword(List<string>token)
        {
            foreach (string sw in stopwords)
            {
                token.Remove(sw);
            }
            return token;
        }

        private List<string> removeDuplicate(List<string> words)
        {
            return words.Distinct().ToList();
        }

        private List<string> medStem(List<string> words)
        {
            foreach (int i in Enumerable.Range(0, words.Count))
            {
                string w = idStemmer.Stemming(words[i]);
                w = enStemmer.StemWord(w);
                w = esStemmer.Execute(w,true);
                words[i] = w;
            }
            return words;
        }

        private List<string> tokenize(string[,] dokumen)
        {
            MatchCollection matches;
            var token = new List<string>();
            for (int i = 0; i < dokumen.GetLength(0); i++)
            {
                matches = Regex.Matches(dokumen[i, 1].ToLower(), @"((\b[^\s]+\b)((?<=\.\w).)?)");
                foreach(var mt in matches)
                {
                    if (IsChinese(mt.ToString()))
                    {
                        char[] characters = mt.ToString().ToCharArray();
                        foreach (var ch in characters)
                        {
                            if (!Char.IsPunctuation(ch))
                            {
                                token.Add(ch.ToString());
                            }
                        }
                    }
                    else
                    {
                        string temp = mt.ToString().Replace(",", "");
                        token.Add(temp);
                    }
                }
            }
            return token;
        }

        public bool IsChinese(string text)
        {
            string word = text;
            bool containUnicode = false;
            for (int x = 0; x < word.Length; x++)
            {
                if (char.GetUnicodeCategory(word[x]) == UnicodeCategory.OtherLetter)
                {
                    containUnicode = true;
                    break;
                }
            }
            if (containUnicode)
            {
                return true;
            }
            else
            {
                return false;
            }
        }
    }
}
