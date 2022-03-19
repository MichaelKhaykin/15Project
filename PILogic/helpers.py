def Swap(arr: list[list[int]], a: tuple[int, int], b: tuple[int, int]):
    temp: int = arr[a[0]][a[1]]
    arr[a[0]][a[1]] = arr[b[0]][b[1]]
    arr[b[0]][b[1]] = temp

dirs: list[tuple[int, int]] = [(0, 1), (0, -1), (-1, 0), (1, 0)]