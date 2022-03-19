using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _15PuzzleVisualizer
{
    public class Tile : ISettable<Point>
    {
        public int Value { get; set; }

        private int x;
        public int X
        {
            get
            {
                return x;
            }
            set
            {
                x = value;
                Box.Location = new Point(x * Box.Image.Width, Box.Location.Y);
                Box.Tag = new Point(x, ((Point)Box.Tag).Y);
            }
        }
        private int y;
        public int Y
        {
            get
            {
                return y;
            }
            set
            {
                y = value;
                Box.Location = new Point(Box.Location.X, y * Box.Image.Height);
                Box.Tag = new Point(((Point)Box.Tag).X, y);
            }
        }

        public PictureBox Box;

        public Tile(int value, int x, int y, Image image)
        {
            Value = value;
            Box = new PictureBox()
            {
                Image = image,
                SizeMode = PictureBoxSizeMode.AutoSize,
                Visible = value != 0,
                Tag = new Point(x, y),
                BorderStyle = BorderStyle.FixedSingle
            };
            X = x;
            Y = y;
        }

        public void Set(Point value)
        {
            Box.Location = value;
        }
    }
}
