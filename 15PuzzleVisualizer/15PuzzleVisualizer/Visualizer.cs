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
        public Visualizer()
        {
            InitializeComponent();

            this.Load += Visualizer_Load;
            this.WindowState = FormWindowState.Maximized;
        }

        private void Visualizer_Load(object sender, EventArgs e)
        {
            Image ogImage = new Bitmap("minesweeperflag.png");
            Image resizedImage = new Bitmap(ogImage, new Size(600, 600));

            resizedImage.Save("minesweeper900x900.png", ImageFormat.Png);

            board = new Board(new Point(this.Width / 2 - resizedImage.Width / 2, this.Height / 2 - resizedImage.Height / 2), gridSize: 3, resizedImage);
            Controls.Add(board);
        }
    }
}
