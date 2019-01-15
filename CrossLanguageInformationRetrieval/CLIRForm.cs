using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CrossLanguageInformationRetrieval
{
    public partial class CLIRForm : Form
    {
        private int count = 0;
        private string[,] dokumen;
        private Stopwatch watch;
        private Dictionary<int, Dictionary<string, double>> normTraining;
        private Preprocessing pre;
        public CLIRForm()
        {
            InitializeComponent();
            pre = new Preprocessing();
            
            if (alreadyTrain())
            {
                openDataset();
                normTraining = openNormalization();
            }
            else
            {
                openDataset();
                training();
            }
        }
                
        private bool alreadyTrain()
        {
            var file = File.ReadLines("alreadytrain.txt").Cast<string>().ToList();
            return (file[0] == "yes" && Convert.ToInt16(file[1]) == Directory.EnumerateFiles("./data/", "*.txt").Count()&&Convert.ToInt64(file[2])== GetDirectorySize("./data/"));
        }

        private long GetDirectorySize(string folder)
        {
            string[] a = Directory.GetFiles(folder, "*.txt");

            long b = 0;
            foreach (string name in a)
            {
                FileInfo info = new FileInfo(name);
                b += info.Length;
            }
            return b;
        }

        private void training()
        {
            watch = new Stopwatch();
            watch.Start();
            normTraining = new Dictionary<int, Dictionary<string, double>>();
            var lengthDoc = dokumen.GetLength(0);
            var tf = pre.termFrequency(dokumen);
            var df = pre.documentFrequency(tf);
            var idft = pre.idft(df, lengthDoc);
            var wtf = pre.wtf(tf);
            var wtd = pre.wtd(wtf, idft);
            normTraining = pre.normalization(wtd);
            using (StreamWriter file = new StreamWriter("normalization.txt"))
                foreach (var entry in normTraining)
                {
                    foreach (var w in entry.Value)
                    {
                        file.WriteLine("{0},{1},{2}",entry.Key,w.Key, w.Value,Encoding.Unicode);
                    }
                }
            using (StreamWriter file = new StreamWriter("alreadytrain.txt"))
            {
                file.WriteLine("yes");
                file.WriteLine(Directory.EnumerateFiles("./data/", "*.txt").Count());
                file.WriteLine(GetDirectorySize("./data/"));
            }
            watch.Stop();
            log("Learning time : "+watch.Elapsed.TotalSeconds.ToString()+" seconds");
        }   
        
        private void btSearch_Click(object sender, EventArgs e)
        {
            watch = new Stopwatch();
            watch.Start();
            string q = rcSearch.Text;
            Translator translator = new Translator();
            q += " " + translator.translate(q);
            log("Query Expansion " +q);
            var query = new string[1,3];
            query[0, 0] = "Dokumen Query";
            query[0, 1] = q;
            pre = new Preprocessing();
            var tf = pre.termFrequency(query);
            var df = pre.documentFrequency(tf);
            var idft = pre.idft(df, 1);
            var wtf = pre.wtf(tf);
            var wtd = pre.wtd(wtf, idft);
            var normQuery = pre.normalization(wtd);
            var cossim = new CosineSimilarity().CosSim(normTraining, normQuery, dokumen, query);
            var items = from pair in cossim orderby pair.Value descending select pair;
            result.Rows.Clear();
            result.Refresh();
            int ret = 0, notret = 0;
            foreach (KeyValuePair<string, double> pair in items)
            {

                if (pair.Value != 0 && pair.Value<1)
                {
                    result.Rows.Add(pair.Key, pair.Value);
                    ret++;
                }
                else
                {
                    notret++;
                }
            }
            log("retrieve : " + ret);
            log("notretrieve : " + notret);
            watch.Stop();
            log("retrieved : "+watch.Elapsed.TotalSeconds.ToString() + " seconds");
        }

        private void openDataset()
        {
            count = Directory.EnumerateFiles("./data/", "*.txt").Count();
            dokumen = new String[count, 3];
            int i = 0;
            foreach (string file in Directory.EnumerateFiles("./data/", "*.txt"))
            {
                dokumen[i, 0] = "Dokumen " + i;
                dokumen[i, 1] = File.ReadAllText(file);
                i++;
            }
            log("load "+count+" dataset done");
        }

        public void log(string log)
        {
            rcLog.Text += log + "\n";
        }

        private void result_CellContentDoubleClick(object sender, DataGridViewCellEventArgs e)
        {
            WindowContent wc = new WindowContent(result.SelectedCells[0].Value.ToString());
            wc.Show();
        }

        private Dictionary<int, Dictionary<string, double>> openNormalization()
        {
            watch = new Stopwatch();
            watch.Start();
            var temp = new Dictionary<int, Dictionary<string, double>>();
            var file = File.ReadLines("normalization.txt", Encoding.UTF8).Cast<string>().ToList();
            int index = 0;
            var doc = new Dictionary<string, double>();
            foreach (string f in file)
            {
                string[] entry = f.Split(',');
                index = Convert.ToInt16(entry[0]);
                break;
            }
            foreach (string f in file)
            {
                string[] entry = f.Split(',');
                int id = Convert.ToInt16(entry[0]);
                string tempString = entry[1];
                double tempDouble = Double.Parse(entry[2], CultureInfo.InvariantCulture);
                if (id == index)
                {
                    doc.Add(tempString, tempDouble);
                }
                else if (id != index)
                {
                    temp.Add(index, doc);
                    index = id;
                    doc = new Dictionary<string, double>();
                    doc.Add(tempString, tempDouble);
                }
            }
            watch.Stop();
            log("Load Normalization "+watch.Elapsed.TotalSeconds.ToString() + " seconds");
            return temp;

        }

    }
}
