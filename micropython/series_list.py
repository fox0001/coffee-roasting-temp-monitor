class SeriesList:
    
    def __init__(self, maxLen: int, firstVal: float):
        self._maxLen = 1 if maxLen <= 0 else maxLen
        self._list = [firstVal]
        self._len = len(self._list)
    
    def append(self, val: float):
        self._list.append(val)
        if (self._len + 1) > self._maxLen:
            delVal = self._list.pop(0)
        else:
            self._len += 1
    
    def last(self, index: int = 0) -> int:
        return self._list[self._len - index -1]
    
    def histogram(self, maxRange: int) -> list:
        hList = self._list.copy()
        hMax = int(max(self._list))
        hMin = int(min(self._list))
        hRange = hMax - hMin + 1
        rate = 1 if hRange <= maxRange else (maxRange / hRange)
        if rate == 1:
            for i, v in enumerate(hList):
                hList[i] = int(v) - hMin
        else:
            for i, v in enumerate(hList):
                hList[i] = int((int(v) - hMin) * rate)
        return hList