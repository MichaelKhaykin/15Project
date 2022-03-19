using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _15PuzzleVisualizer
{
    public interface ISettable<T>
    {
        public void Set(T value);
    }
}
