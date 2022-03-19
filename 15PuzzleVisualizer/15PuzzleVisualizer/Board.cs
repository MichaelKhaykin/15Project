using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _15PuzzleVisualizer
{
    public class Board : Control
    {
        private Tile[,] Grid { get; }
        public int Width => Grid.GetLength(1);
        public int Height => Grid.GetLength(0);

        private Panel panel;
        private Image image;
        private Timer timer;
        private Button shuffleButton;

        public Board(Point location, int gridSize, Image image)
        {
            Grid = new Tile[gridSize, gridSize];
            Location = location;
            Size = new Size(image.Size.Width, image.Size.Height + 200);

            timer = new()
            {
                Enabled = true,
                Interval = 50,
            };
            timer.Tick += Timer_Tick;

            panel = new()
            {
                Location = new Point(0, 0),
                Size = image.Size,
                BorderStyle = BorderStyle.FixedSingle
            };

            int cellWidth = image.Width / gridSize;
            int cellHeight = image.Height / gridSize;

            this.image = image;

            for (int x = 0; x < gridSize; x++)
            {
                for (int y = 0; y < gridSize; y++)
                {
                    int number = (y * gridSize + x + 1) % Grid.Length;
                    var cut = Cut(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
                    Tile tile = new Tile(number, x, y, cut);
                    tile.Box.Click += Box_Click;

                    panel.Controls.Add(tile.Box);
                    Grid[y, x] = tile;
                }
            }

            shuffleButton = new Button()
            {
                Location = new Point(panel.Left, panel.Bottom),
                Size = new Size(cellWidth / 2, cellHeight / 4),
                Text = "Shuffle",
                BackColor = Color.Green
            };
            shuffleButton.Click += ShuffleButton_Click;

            Controls.Add(shuffleButton);
            Controls.Add(panel);

           // DebugSave("minesweeper");
        }

        private async void ShuffleButton_Click(object sender, EventArgs e)
        {
            var moves = GetShuffleMoves(50);
            foreach (var move in moves)
            {
                var tile = Grid[move.sy, move.sx];
                var empty = Grid[move.ey, move.ex];
                int count = LerpManager<Point, Tile>.Count;
                SwapTile(tile, empty, 0.7f);
                while (count != LerpManager<Point, Tile>.Count) await Task.Delay(1);
            }
        }

        public List<Swap> GetShuffleMoves(int iterations)
        {
            List<(int x, int y)> GetNextToEmpty(int x, int y)
            {
                List<(int x, int y)> tiles = new List<(int x, int y)>();
                if (x - 1 >= 0) tiles.Add((x - 1, y));
                if (x + 1 < Height) tiles.Add((x + 1, y));
                if (y - 1 >= 0) tiles.Add((x, y - 1));
                if (y + 1 < Grid.GetLength(0)) tiles.Add((x, y + 1));

                return tiles;
            }
            //Empty tile starts in (gridSize - 1, gridSize - 1)

            List<Swap> actions = new List<Swap>();

            var lastEmpty = (-1, -1);
            var empty = (x: Width - 1, y: Height - 1);
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

        void SwapTile(Tile tile, Tile empty, float speed)
        {
            //Swap grid
            var temp = Grid[tile.Y, tile.X];
            Grid[tile.Y, tile.X] = Grid[empty.Y, empty.X];
            Grid[empty.Y, empty.X] = temp;

            int goalX = empty.X;
            int goalY = empty.Y;

            //Lerp this tile to empty tile location
            LerpManager<Point, Tile>.AddLerp(new Lerp<Point, Tile>(tile, tile.Box.Location, empty.Box.Location, speed, LerpMethods.PointLerp, () =>
            {
                tile.X = goalX;
                tile.Y = goalY;
            }));

            //Set empty location into current tile position
            empty.X = tile.X;
            empty.Y = tile.Y;
        }
        private void Box_Click(object sender, EventArgs e)
        {
            var box = (PictureBox)sender;
            var location = (Point)box.Tag;
            var tile = Grid[location.Y, location.X];
            Tile empty = GetEmptyNeighbor(tile.X, tile.Y);
            if (empty == null) return;

            SwapTile(tile, empty, 0.1f);
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

        private void DebugSave(string name)
        {
            Bitmap map = new Bitmap(image.Width, image.Height);
            Graphics gfx = Graphics.FromImage(map);

            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    if (Grid[y, x].Value == 0) continue;
                    gfx.DrawImage(Grid[y, x].Box.Image, new Point(x * image.Width / Width, y * image.Height / Height));
                }
            }

            map.Save(name + ".png", ImageFormat.Png);
        }
    }
}
