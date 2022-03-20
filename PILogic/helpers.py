from typing import List
from typing import Tuple

def Swap(arr: List[List[int]], a: Tuple[int, int], b: Tuple[int, int]):
    temp: int = arr[a[0]][a[1]]
    arr[a[0]][a[1]] = arr[b[0]][b[1]]
    arr[b[0]][b[1]] = temp

dirs: List[Tuple[int, int]] = [(0, 1), (0, -1), (-1, 0), (1, 0)]