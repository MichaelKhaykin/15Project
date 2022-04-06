using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _15PuzzleVisualizer
{
    public partial class Visualizer : Form
    {
        Board board;
        Label exitLabel;
        public Visualizer()
        {
            InitializeComponent();

            this.Load += Visualizer_Load;
            this.WindowState = FormWindowState.Maximized;
            this.FormBorderStyle = FormBorderStyle.None;

        }

        private void ExitLabel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void Visualizer_Load(object sender, EventArgs e)
        {
            this.BackColor = Color.Brown;

            string exitText = "Exit";
            exitLabel = new Label()
            {
                Text = exitText,
                BackColor = this.BackColor,
                Font = this.Font,
                AutoSize = true,
                Location = new Point(this.Right - TextRenderer.MeasureText(exitText, this.Font).Width, this.Top),
            };
            exitLabel.Click += ExitLabel_Click;
            Controls.Add(exitLabel);

            string restartText = "Restart";
            var restartLabel = new Label()
            {
                Text = restartText,
                BackColor = this.BackColor,
                Font = this.Font,
                AutoSize = true,
                Location = new Point(this.Right - TextRenderer.MeasureText(restartText, this.Font).Width, exitLabel.Bottom),
            };
            restartLabel.Click += RestartLabel_Click;
            Controls.Add(restartLabel);
            Init();
        }

        void Init()
        {
            int gridSize = 3;
            int padding = 100;
            board = new Board(new Point(0, 0), gridSize, Properties.Resources.background, padding, Color.Black, Color.Purple, Properties.Resources.gmrLogoYellowBrain);
            Controls.Add(board);
        }

        private void RestartLabel_Click(object sender, EventArgs e)
        {
            Controls.Remove(board);
            Init();
        }

        private void Visualizer_Load_1(object sender, EventArgs e)
        {

        }
    }
}
