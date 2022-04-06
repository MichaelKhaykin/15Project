using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _15PuzzleVisualizer
{
    public class Board : Control
    {
        enum States
        {
            Calibrate,
            Idle,
            Shuffling,
            Resetting,
            ManualMove
        }

        private Tile[,] Grid { get; }
        public int GridWidth => Grid.GetLength(1);
        public int GridHeight => Grid.GetLength(0);

        public int CellWidth { get; }
        public int CellHeight { get; }

        private Panel panel;
        private Image image;
        private Timer timer;
        private Button shuffleButton;
        private Button resetButton;
        private Button calibrateButton;
        private Button solveButton;
        private Button changeImageButton;
        private Control bg;


        Dictionary<int, Tile> intToVal = new Dictionary<int, Tile>();

        States boardState = States.Idle;

        UdpClient client = new UdpClient();

        Bitmap panelBg;
        Graphics panelGfx;
        Image cellImage;

        private int MessageID = 0;

        /// <summary>
        /// Location represents where the center of the board should go
        /// </summary>
        /// <param name="location"></param>
        /// <param name="gridSize"></param>
        /// <param name="image"></param>
        /// <param name="padding"></param>
        /// <param name="backColor"></param>
        /// <param name="gameBoardBackColor"></param>
        Size imageSize = new Size(600, 600);

        public Board(Point location, int gridSize, Image rawimage, int padding, Color backColor, Color gameBoardBackColor, Image rawbackgroundCellImage)
        {
            client.Connect("192.168.1.126", 5000);

            SetImage((Bitmap)rawimage);

            panelBg = new Bitmap(imageSize.Width, imageSize.Height);
            panelGfx = Graphics.FromImage(panelBg);
            panelGfx.FillRectangle(new SolidBrush(gameBoardBackColor), new Rectangle(0, 0, panelBg.Width, panelBg.Height));

            Grid = new Tile[gridSize, gridSize];

            CellWidth = imageSize.Width / gridSize;
            CellHeight = imageSize.Height / gridSize;

            panel = new()
            {
                Location = new Point(padding / 2, padding / 2),
                Size = imageSize,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = gameBoardBackColor,
            };

            for (int x = 0; x < gridSize; x++)
            {
                for (int y = 0; y < gridSize; y++)
                {
                    int number = (y * gridSize + x + 1) % Grid.Length;
                    var cut = Cut(x * CellWidth, y * CellHeight, CellWidth, CellHeight);
                    Tile tile = new Tile(number, x, y, cut);

                    intToVal.Add(number, tile);

                    tile.Box.Click += Box_Click;

                    panel.Controls.Add(tile.Box);
                    tile.Box.Name = number == 0 ? "Empty" : "Filled";
                    Grid[y, x] = tile;
                }
            }

            Image ogLogo = new Bitmap(rawbackgroundCellImage);
            float ratio = ((imageSize.Width / gridSize) / 2) / ogLogo.Width;
            Size newLogoSize = new Size((int)(ratio * ogLogo.Width), (int)(ratio * ogLogo.Height));
            Bitmap logo = new Bitmap(ogLogo, newLogoSize);

            this.cellImage = logo;

            DrawLogo(GridWidth - 1, GridHeight - 1);
            panel.BackgroundImage = panelBg;
            
            this.Tag = "Keep";

            Size = new Size(imageSize.Width + padding, imageSize.Height + padding + 200);

            timer = new()
            {
                Enabled = true,
                Interval = 50,
            };
            timer.Tick += Timer_Tick;

            bg = new Control()
            {
                Size = new Size(imageSize.Width + padding, imageSize.Height + padding),
                BackColor = backColor,
                Tag = "Keep"
            };

            Location = location;

            shuffleButton = new Button()
            {
                Location = new Point(bg.Left, bg.Bottom),
                Size = new Size(CellWidth / 2, CellHeight / 4),
                Text = "Shuffle",
                BackColor = Color.Red
            };
            shuffleButton.Click += ShuffleButton_Click;

            resetButton = new Button()
            {
                Location = new Point(shuffleButton.Right, bg.Bottom),
                Size = new Size(CellWidth / 2, CellHeight / 4),
                Text = "Reset",
                BackColor = Color.Red
            };
            resetButton.Click += ResetButton_Click;

            calibrateButton = new Button()
            {
                Location = new Point(resetButton.Right, bg.Bottom),
                Size = new Size(CellWidth / 2, CellHeight / 4),
                Text = "Calibrate",
                Tag = "Keep",
                BackColor = Color.Red
            };
            calibrateButton.Click += CalibrateButton_Click;

            solveButton = new Button()
            {
                Location = new Point(shuffleButton.Left, shuffleButton.Bottom),
                Size = new Size(CellWidth / 2, CellHeight / 4),
                Text = "Solve",
                BackColor = Color.Red
            };

            solveButton.Click += SolveButton_Click;

            changeImageButton = new Button()
            {
                Location = new Point(solveButton.Right, calibrateButton.Bottom),
                Size = new Size(CellWidth / 2, CellHeight / 4),
                Text = "Choose Image",
                BackColor = Color.Red
            };

            changeImageButton.Click += ChangeImageButton_Click;

            Controls.Add(shuffleButton);
            Controls.Add(resetButton);
            Controls.Add(calibrateButton);
            Controls.Add(solveButton);
            Controls.Add(changeImageButton);
            bg.Controls.Add(panel);
            Controls.Add(bg);

            boardState = States.Calibrate;

            this.KeyDown += Board_KeyDown;
            // DebugSave("minesweeper");
        }

        private void SetImage(Bitmap rawimage)
        {
            Image ogImage = new Bitmap(rawimage);
            Image resizedImage = new Bitmap(ogImage, imageSize);
            this.image = resizedImage;
        }
        private void ChangeImageButton_Click(object sender, EventArgs e)
        {
            OpenFileDialog f = new OpenFileDialog();
            var result = f.ShowDialog();
            if(result == DialogResult.OK || result == DialogResult.Yes)
            {
                var extension = Path.GetExtension(f.FileName);
                if(extension != ".bmp" && extension != ".png")
                {
                    MessageBox.Show("Please choose a file with a png or bmp format!");
                    return;
                }
                Load(new Bitmap(f.FileName));
            }
        }

        private void Load(Bitmap newpicture)
        {
            SetImage(newpicture);
            for (int y = 0; y < GridHeight; y++)
            {
                for(int x = 0; x < GridWidth; x++)
                {
                    Grid[y, x].Box.Image = Cut(x * CellWidth, y * CellHeight, CellWidth, CellHeight);
                }
            }
        }

        bool isDebug = false;
        private void Board_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.D)
            {
                isDebug = !isDebug;
            }

            for (int y = 0; y < GridHeight; y++)
            {
                for (int x = 0; x < GridWidth; x++)
                {
                    if (isDebug)
                    {
                        Grid[y, x].DrawNumber(this.Font);
                    }
                    else
                    {
                        Grid[y, x].ClearNumber();
                    }
                }
            }
        }

        private async void SolveButton_Click(object sender, EventArgs e)
        {
            await SendMessage("M");
        }

        private void RecursivelyChange(Control c, Predicate<Control> p, bool enabled)
        {
            if (p(c))
            {
                c.Enabled = enabled;
                c.Visible = enabled;
            }

            foreach (Control m in c.Controls)
            {
                RecursivelyChange(m, p, enabled);
            }
        }
        private async void CalibrateButton_Click(object sender, EventArgs e)
        {
            RecursivelyChange(this, p => p.Tag != "Keep", false);

            Panel newP = new Panel()
            {
                Location = panel.Location,
                Size = panel.Size,
                BackColor = Color.Brown
            };
            bg.Controls.Add(newP);
            Bitmap m = new Bitmap(newP.Width, newP.Height);
            Graphics gfx = Graphics.FromImage(m);

            for (int i = 0; i < GridHeight; i++)
            {
                for (int j = 0; j < GridWidth; j++)
                {
                    int rad = CellWidth / 6;
                    gfx.FillRectangle(new SolidBrush(Color.Purple), new Rectangle(j * CellWidth + CellWidth / 2 - rad, i * CellHeight + CellHeight / 2 - rad, rad * 2, rad * 2));
                }
            }
            newP.BackgroundImage = m;

            await SendMessage("C");
            await Task.Delay(5250);

            bg.Controls.Remove(bg);
            Controls.Remove(calibrateButton);

            RecursivelyChange(this, p => p.Name != "Empty", true);

            boardState = States.Idle;
        }

        private async Task SendMessage(string message)
        {
            var bytes = Encoding.ASCII.GetBytes(message + $"{MessageID++}");
            await client.SendAsync(bytes, bytes.Length);
        }
        private async void ResetButton_Click(object sender, EventArgs e)
        {
            if (boardState != States.Idle) return;

            boardState = States.Resetting;
            //Lerp all tiles into place and when done reset board
            foreach (var item in Grid)
            {
                LerpManager<Point, Tile>.AddLerp(new Lerp<Point, Tile>(item, item.Box.Location, intToVal[item.Value].OgLocation, 0.5f, LerpMethods.PointLerp, () =>
                {

                }));
            }

            while (LerpManager<Point, Tile>.Count != 0) await Task.Delay(1);

            //Reset grid
            for (int i = 0; i < GridHeight; i++)
            {
                for (int j = 0; j < GridWidth; j++)
                {
                    Grid[i, j] = intToVal[(i * GridWidth + j + 1) % (GridWidth * GridHeight)];
                    Grid[i, j].X = Grid[i, j].OgLocationX;
                    Grid[i, j].Y = Grid[i, j].OgLocationY;
                }
            }

            DrawLogo(GridWidth - 1, GridHeight - 1);

            boardState = States.Idle;
        }

        float speed = 0.5f;
        private async void ShuffleButton_Click(object sender, EventArgs e)
        {
            if (boardState != States.Idle) return;


            await SendMessage("F");
            await Task.Delay(250);

            boardState = States.Shuffling;

            var moves = GetShuffleMoves(20);
            foreach (var move in moves)
            {
                var tile = Grid[move.sy, move.sx];
                var empty = Grid[move.ey, move.ex];
                await SwapTile(tile, empty, speed);
                await Task.Delay(150);
            }

            boardState = States.Idle;

            await Task.Delay(250);
            await SendMessage("W");
        }

        public List<Swap> GetShuffleMoves(int iterations)
        {
            List<(int x, int y)> GetNextToEmpty(int x, int y)
            {
                List<(int x, int y)> tiles = new List<(int x, int y)>();
                if (x - 1 >= 0) tiles.Add((x - 1, y));
                if (x + 1 < GridHeight) tiles.Add((x + 1, y));
                if (y - 1 >= 0) tiles.Add((x, y - 1));
                if (y + 1 < Grid.GetLength(0)) tiles.Add((x, y + 1));

                return tiles;
            }
            //Empty tile starts in (gridSize - 1, gridSize - 1)

            List<Swap> actions = new List<Swap>();

            var lastEmpty = (-1, -1);
            var empty = (x: Grid.Grab(t => t.Value == 0).X, y: Grid.Grab(t => t.Value == 0).Y);
            for (int i = 0; i < iterations; i++)
            {
                var neighboringTiles = GetNextToEmpty(empty.x, empty.y);
                var (x, y) = neighboringTiles[Statics.Random.Next(0, neighboringTiles.Count)];
                while (lastEmpty == (x, y))
                {
                    (x, y) = neighboringTiles[Statics.Random.Next(0, neighboringTiles.Count)];
                }

                actions.Add(new Swap(x, y, empty.x, empty.y));
                lastEmpty = empty;
                empty = (x, y);
            }

            return actions;
        }

        private void Timer_Tick(object sender, EventArgs e)
        {
            LerpManager<Point, Tile>.Update();
        }

        async Task SwapTile(Tile tile, Tile empty, float speed)
        {
            //Swap grid
            var temp = Grid[tile.Y, tile.X];
            Grid[tile.Y, tile.X] = Grid[empty.Y, empty.X];
            Grid[empty.Y, empty.X] = temp;

            int goalX = empty.X;
            int goalY = empty.Y;

            int oldC = LerpManager<Point, Tile>.Count;
            //Lerp this tile to empty tile location
            LerpManager<Point, Tile>.AddLerp(new Lerp<Point, Tile>(tile, tile.Box.Location, empty.Box.Location, speed, LerpMethods.PointLerp, () =>
            {
                int x = tile.X;
                int y = tile.Y;

                tile.X = goalX;
                tile.Y = goalY;

                DrawLogo(x, y);
            }));

            //Set empty location into current tile position
            empty.X = tile.X;
            empty.Y = tile.Y;

            while (oldC != LerpManager<Point, Tile>.Count) await Task.Delay(1);
        }

        private void DrawLogo(int x, int y)
        {
            panelGfx.Clear(panel.BackColor);
            panelGfx.DrawImage(cellImage, x * CellWidth + CellWidth / 2 - cellImage.Width / 2, y * CellHeight + CellHeight / 2 - cellImage.Height / 2);
            panel.BackgroundImage = panelBg;
            panel.Invalidate();
        }
        private async void Box_Click(object sender, EventArgs e)
        {
            if (boardState != States.Idle) return;

            boardState = States.ManualMove;

            var box = (PictureBox)sender;
            var location = (Point)box.Tag;
            var tile = Grid[location.Y, location.X];
            Tile empty = GetEmptyNeighbor(tile.X, tile.Y);
            if (empty == null)
            {
                boardState = States.Idle;
                return;
            }

            await SendMessage("F");
            await SwapTile(tile, empty, speed);
            await SendMessage("W");

            boardState = States.Idle;
        }

        private Tile GetEmptyNeighbor(int x, int y)
        {
            if (x - 1 >= 0 && Grid[y, x - 1].Value == 0) return Grid[y, x - 1];
            if (x + 1 < Grid.GetLength(1) && Grid[y, x + 1].Value == 0) return Grid[y, x + 1];
            if (y - 1 >= 0 && Grid[y - 1, x].Value == 0) return Grid[y - 1, x];
            if (y + 1 < Grid.GetLength(0) && Grid[y + 1, x].Value == 0) return Grid[y + 1, x];

            return null;
        }

        private Image Cut(int x, int y, int width, int height)
        {
            Bitmap map = new(width, height);
            Graphics gfx = Graphics.FromImage(map);
            gfx.DrawImage(image, 0, 0, new Rectangle(x, y, width, height), GraphicsUnit.Pixel);
            return map;
        }

        private PointF[] StarPoints(int num_points, Rectangle bounds)
        {
            // Make room for the points.
            PointF[] pts = new PointF[num_points];

            double rx = bounds.Width / 2;
            double ry = bounds.Height / 2;
            double cx = bounds.X + rx;
            double cy = bounds.Y + ry;

            // Start at the top.
            double theta = -Math.PI / 2;
            double dtheta = 4 * Math.PI / num_points;
            for (int i = 0; i < num_points; i++)
            {
                pts[i] = new PointF(
                    (float)(cx + rx * Math.Cos(theta)),
                    (float)(cy + ry * Math.Sin(theta)));
                theta += dtheta;
            }

            return pts;
        }

        private void DebugSave(string name)
        {
            Bitmap map = new Bitmap(image.Width, image.Height);
            Graphics gfx = Graphics.FromImage(map);

            for (int y = 0; y < GridHeight; y++)
            {
                for (int x = 0; x < GridWidth; x++)
                {
                    if (Grid[y, x].Value == 0) continue;
                    gfx.DrawImage(Grid[y, x].Box.Image, new Point(x * image.Width / GridWidth, y * image.Height / GridHeight));
                }
            }

            map.Save(name + ".png", ImageFormat.Png);
        }
    }
}
