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

        public int OgLocationX { get; }
        public int OgLocationY { get; }

        public Point OgLocation => new Point(OgLocationX * Box.Image.Width, OgLocationY * Box.Image.Height);

        Graphics gfx;
        Bitmap canvas;
        Image ogImage;
        public Tile(int value, int x, int y, Image image)
        {
            OgLocationX = x;
            OgLocationY = y;

            Value = value;
            Box = new PictureBox()
            {
                Image = image,
                SizeMode = PictureBoxSizeMode.AutoSize,
                Tag = new Point(x, y),
                Visible = value != 0,
                BorderStyle = BorderStyle.FixedSingle,
            };

            ogImage = image;

            canvas = new Bitmap(image);
            gfx = Graphics.FromImage(canvas);



            X = x;
            Y = y;
        }

        public void Set(Point value)
        {
            Box.Location = value;
        }

        public void ClearNumber()
        {
            canvas = (Bitmap)ogImage;
            Box.Image = canvas;
        }

        public void DrawNumber(Font font)
        {
            string text = this.Value.ToString();
            var size = TextRenderer.MeasureText(text, font);
            gfx.DrawString(text, font, Brushes.Red, new PointF(Box.Width / 2 - size.Width / 2, Box.Height / 2 - size.Height / 2));
            Box.Image = canvas;
        }
    }
}
