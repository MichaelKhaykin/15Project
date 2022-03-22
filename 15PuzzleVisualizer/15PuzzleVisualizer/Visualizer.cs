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
            this.BackColor = Color.White;

            string n = "background";
            Image ogImage = new Bitmap($"{n}.png");
            Size resize = new Size(800, 800);
            Image resizedImage = new Bitmap(ogImage, resize);

            resizedImage.Save($"{n}{resize.Width}x{resize.Height}.png", ImageFormat.Png);

            board = new Board(new Point(this.Width / 2, this.Height / 2), gridSize: 4, resizedImage, 100, Color.Black, Color.Purple);
            Controls.Add(board);
        }
    }
}
