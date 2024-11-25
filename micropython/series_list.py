import ulogger
import time

class SeriesList:
    
    def __init__(self, maxLen: int, firstVal: float):
        self._maxLen = 1 if maxLen <= 0 else maxLen
        self._list = [firstVal]
        self._len = len(self._list)
        self._logger = ulogger.Logger(
            name = __name__,
            handlers = [
                ulogger.Handler(
                    level=ulogger.INFO,
                    fmt="&(msg)%",
                    clock=NoClock(),
                    direction=ulogger.TO_FILE,
                    file_name="record/crc.csv",
                    max_file_size=102400 # max for 100KB
                )
            ]
        )
        #self._logger.info('//-- start ---')
    
    def append(self, val: float, sec: int, vType: String='-', isSave: bool=False):
        if isSave:
            self._logger.info('{},{},{}'.format(sec, val, vType))
        self._list.append(val)
        if (self._len + 1) > self._maxLen:
            delVal = self._list.pop(0)
        else:
            self._len += 1
    
    def last(self, index: int = 0) -> int:
        return self._list[self._len - index -1]
    
    def load(self) -> list:
        return self._list.copy()
    
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

class NoClock(ulogger.BaseClock):
    def __call__(self) -> str:
        return ''

def getLogger(level = ulogger.INFO) -> ulogger.Logger:
    class NoClock(ulogger.BaseClock):
        def __call__(self) -> str:
            return ''
    
    handler_to_file = ulogger.Handler(
        level=level,
        fmt="&(msg)%",
        clock=NoClock(),
        direction=ulogger.TO_FILE,
        file_name="record/crc.csv",
        max_file_size=102400 # max for 100KB
    )
    
    logger = ulogger.Logger(
        name = __name__,
        handlers = (
            handler_to_file
        )
    )
    return logger
