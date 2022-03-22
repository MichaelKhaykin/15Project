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
        enum States
        {
            Idle,
            Shuffling,
            Resetting,
            ManualMove
        }

        private Tile[,] Grid { get; }
        public int GridWidth => Grid.GetLength(1);
        public int GridHeight => Grid.GetLength(0);

        private Panel panel;
        private Image image;
        private Timer timer;
        private Button shuffleButton;
        private Button resetButton;
        private Control bg;

        Dictionary<int, Tile> intToVal = new Dictionary<int, Tile>();

        States boardState = States.Idle;

        /// <summary>
        /// Location represents where the center of the board should go
        /// </summary>
        /// <param name="location"></param>
        /// <param name="gridSize"></param>
        /// <param name="image"></param>
        /// <param name="padding"></param>
        /// <param name="backColor"></param>
        /// <param name="gameBoardBackColor"></param>
        public Board(Point location, int gridSize, Image image, int padding, Color backColor, Color gameBoardBackColor)
        {
            Grid = new Tile[gridSize, gridSize];
            
            Size = new Size(image.Size.Width + padding, image.Size.Height + padding + 200);

            timer = new()
            {
                Enabled = true,
                Interval = 50,
            };
            timer.Tick += Timer_Tick;

            bg = new Control()
            {
                Size = new Size(image.Width + padding, image.Height + padding),
                BackColor = backColor
            };

            Location = new Point(location.X - bg.Width / 2, location.Y - bg.Height / 2);

            panel = new()
            {
                Location = new Point(padding / 2, padding / 2),
                Size = image.Size,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = gameBoardBackColor
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

                    intToVal.Add(number, tile);

                    tile.Box.Click += Box_Click;

                    panel.Controls.Add(tile.Box);
                    Grid[y, x] = tile;
                }
            }

            shuffleButton = new Button()
            {
                Location = new Point(bg.Left, bg.Bottom),
                Size = new Size(cellWidth / 2, cellHeight / 4),
                Text = "Shuffle",
                BackColor = Color.Red
            };
            shuffleButton.Click += ShuffleButton_Click;

            resetButton = new Button()
            {
                Location = new Point(shuffleButton.Right, bg.Bottom),
                Size = new Size(cellWidth / 2, cellHeight / 4),
                Text = "Reset",
                BackColor = Color.Red
            };
            resetButton.Click += ResetButton_Click;

            Controls.Add(shuffleButton);
            Controls.Add(resetButton);
            bg.Controls.Add(panel);
            Controls.Add(bg);

           // DebugSave("minesweeper");
        }

        private async void ResetButton_Click(object sender, EventArgs e)
        {
            if (boardState != States.Idle) return;

            boardState = States.Resetting;
            //Lerp all tiles into place and when done reset board
            foreach(var item in Grid)
            {
                LerpManager<Point, Tile>.AddLerp(new Lerp<Point, Tile>(item, item.Box.Location, intToVal[item.Value].OgLocation, 0.5f, LerpMethods.PointLerp, () => 
                { 
                       
                }));
            }

            while (LerpManager<Point, Tile>.Count != 0) await Task.Delay(1);

            //Reset grid
            for(int i = 0; i < GridHeight; i++)
            {
                for(int j = 0; j < GridWidth; j++)
                {
                    Grid[i, j] = intToVal[(i * GridWidth + j + 1 ) % (GridWidth * GridHeight)];
                    Grid[i, j].X = Grid[i, j].OgLocationX;
                    Grid[i, j].Y = Grid[i, j].OgLocationY;
                }
            }

            boardState = States.Idle;
        }

        private async void ShuffleButton_Click(object sender, EventArgs e)
        {
            if (boardState != States.Idle) return;

            boardState = States.Shuffling;

            var moves = GetShuffleMoves(5);
            foreach (var move in moves)
            {
                var tile = Grid[move.sy, move.sx];
                var empty = Grid[move.ey, move.ex];
                await SwapTile(tile, empty, 0.5f);
            }

            boardState = States.Idle;
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
                tile.X = goalX;
                tile.Y = goalY;
            }));

            //Set empty location into current tile position
            empty.X = tile.X;
            empty.Y = tile.Y;

            while (oldC != LerpManager<Point, Tile>.Count) await Task.Delay(1);
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

            await SwapTile(tile, empty, 0.5f);

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
