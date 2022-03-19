class Hueristics:
    def ManhattanHueristic(cur: list[list[int]], mapping: dict[int, tuple[int, int]]) -> float:
        
        sum: float = 0

        for i in range(0, len(cur)):
            for j in range(0, len(cur[i])):

                if(cur[i][j] == 0):
                    continue

                (y, x) = mapping[cur[i][j]]
                yDiff = abs(y - i)
                xDiff = abs(x - j)

                sum += xDiff + yDiff

        return sum