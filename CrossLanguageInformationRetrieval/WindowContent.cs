using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CrossLanguageInformationRetrieval
{
    public partial class WindowContent : Form
    {
        public WindowContent(string content)
        {
            InitializeComponent();
            this.Text = content.Substring(0, 30);
            rcContent.Text = content;
        }

    }
}
