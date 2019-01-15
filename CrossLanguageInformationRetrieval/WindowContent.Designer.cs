namespace CrossLanguageInformationRetrieval
{
    partial class WindowContent
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.rcContent = new System.Windows.Forms.RichTextBox();
            this.SuspendLayout();
            // 
            // rcContent
            // 
            this.rcContent.Location = new System.Drawing.Point(13, 13);
            this.rcContent.Name = "rcContent";
            this.rcContent.ReadOnly = true;
            this.rcContent.Size = new System.Drawing.Size(580, 312);
            this.rcContent.TabIndex = 0;
            this.rcContent.Text = "";
            // 
            // WindowContent
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(605, 337);
            this.Controls.Add(this.rcContent);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.Name = "WindowContent";
            this.Text = "Window Content";
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.RichTextBox rcContent;
    }
}