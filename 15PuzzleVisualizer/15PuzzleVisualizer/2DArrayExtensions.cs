using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _15PuzzleVisualizer
{
    public static class _2DArrayExtensions
    {
        public static T Grab<T>(this T[,] arr, Predicate<T> predicate)
        {
            foreach(var item in arr)
            {
                if (predicate(item)) return item;
            }
            return default;
        }
    }
}
