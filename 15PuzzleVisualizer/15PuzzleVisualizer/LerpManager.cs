using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _15PuzzleVisualizer
{
    public static class LerpManager<T, U>
        where U : ISettable<T>
    {
        private static List<Lerp<T, U>> Lerps = new List<Lerp<T, U>>();
        public static int Count => Lerps.Count;
        public static void AddLerp(Lerp<T, U> lerp)
        {
            Lerps.Add(lerp);
        }

        public static void Update()
        {
            for(int i = 0; i < Lerps.Count; i++)
            {
                if (Lerps[i].Completed())
                {
                    Lerps.RemoveAt(i);
                    i--;
                    continue;
                }
                Lerps[i].Update();
            }
        }
    }
}
