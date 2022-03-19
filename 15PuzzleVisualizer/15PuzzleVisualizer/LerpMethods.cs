using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _15PuzzleVisualizer
{
    public static class LerpMethods
    {
        public static Point PointLerp(Point a, Point b, float amount)
        {
            var xLerp = (int)LerpFloat(a.X, b.X, amount);
            var yLerp = (int)LerpFloat(a.Y, b.Y, amount);
            return new Point(xLerp, yLerp);
        }

        public static float LerpFloat(float a, float b, float amount)
        {
            return a + amount * (b - a);
        }
    }
}
