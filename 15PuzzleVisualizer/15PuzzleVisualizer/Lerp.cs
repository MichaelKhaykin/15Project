using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _15PuzzleVisualizer
{
    public class Lerp<T, U>
        where U : ISettable<T>
    {
        public U @Object { get; }
        public T Start { get; }
        public T End { get; }
        public float TravelPercentage { get; private set; }
        public float Step { get; }

        private Func<T, T, float, T> LerpFunc;

        private Action OnCompleted;
        public Lerp(U @object, T start, T end, float step, Func<T, T, float, T> lerp, Action oncompleted)
        {
            @Object = @object;
            Start = start;
            End = end;
            Step = step;
            LerpFunc = lerp;
            OnCompleted = oncompleted;
        }

        public void Update()
        {
            var cur = LerpFunc(Start, End, TravelPercentage);
            @Object.Set(cur);

            TravelPercentage += Step;
        }

        public bool Completed()
        {
            bool completed = TravelPercentage >= 1f;
            if (completed)
            {
                OnCompleted();
            }
            return completed;
        }
    }
}
