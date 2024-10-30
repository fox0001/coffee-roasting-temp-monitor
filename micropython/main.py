'''
Project: Coffee Roasting Temperature Record
Version: v1.0

Coffee roast curve, CRC, 咖啡烘焙曲线
Rate of Rise, RoR, 升温速率
Development Time Ratio, DTR, 发展率
'''

from micropython import const
import time
from machine import Pin, SoftI2C, Timer
from max6675 import MAX6675
from ssd1306 import SSD1306_I2C
from series_list import SeriesList

""" wiring diagram ################################## """
"""
- Core Board: ESP32-C3
- Display: TFT display, SSD1306, 128x64
- Temperature Sensor: MAX6675, 0~1024°C

+[ ESP32-C3 ]--------+   +[ MAX6675 ]+
| GND    |  |    GND |---| GND       |
| GPIO00 |  |   3.3V |---| VCC       |
| GPIO01 |  | GPIO02 |---| SCK       |
| GPIO12 |  | GPIO03 |---| CS        |
| GPIO18 |  | GPIO10 |---| SO        |
| GPIO19 |  | GPIO06 |   +-----------+
| GND    |  | GPIO07 |
| -      |  | GPIO11 |   +[ TFT ]----+
| -      |  |    GND |---| GND       |
| GPIO13 |  |   3.3V |---| VCC       |
| NC     |  | GPIO05 |---| SCL       |
| REST   |  | GPIO04 |---| SDA       |
| 3.3V   |  | GPIO08 |   +-----------+
| GND    |  | GPIO09 |
| PWB    |  |     5V |
| 5V     |  |    GND |
|     USB Type-C     |
+--------------------+
"""

""" global config ################################## """
UNIT_60 = const(60)
SCREEN_W = const(128)
SCREEN_H = const(64)
HISTOGRAM_X = const(0)
HISTOGRAM_Y = const(10)
HISTOGRAM_W = const(SCREEN_W)
HISTOGRAM_H = const(SCREEN_H - HISTOGRAM_Y)

""" init MAX6675 ################################## """
print('init MAX6675')
sck = Pin(2, Pin.OUT) # GPIO02
cs = Pin(3, Pin.OUT) # GPIO03，待确定
so = Pin(10, Pin.IN) # GPIO10
max = MAX6675(sck, cs, so)
time.sleep(1)
curTemp = max.read()

""" init OLED ################################## """
print('init OLED')
i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
oled = SSD1306_I2C(SCREEN_W, SCREEN_H, i2c)

""" init Ticks ################################## """
ticksStart = time.ticks_ms()

""" init Temperature list ################################## """
sList = SeriesList(SCREEN_W, curTemp)

""" init Timer ################################## """
def timerRefresh(t):
    global max, curTemp, oled, timeSec, sList
    
    duration = 0 if ticksStart==None else int(time.ticks_diff(time.ticks_ms(), ticksStart) / 1000)
    dSec = duration % UNIT_60
    dMin = int(duration / UNIT_60)
    
    curTemp = max.read() # Current temperature
    sList.append(curTemp)
    
    oled.fill(0)
    oled.text('{:02d}:{:02d} | {:>6.2f} C'.format(dMin, dSec, curTemp) , 0, 0)
    hList = sList.histogram(HISTOGRAM_H)
    hLen = len(hList)
    hPre = 0
    hCur = 0
    startX = SCREEN_W - hLen
    startY = HISTOGRAM_Y + HISTOGRAM_H - 1
    for i, v in enumerate(hList):
        hPre = v if i == 0 else hCur
        hCur = v
        oled.vline(startX + i, startY - hCur, (hCur - hPre if hPre < hCur else 1), 1)
        if hPre > hCur:
            oled.vline(startX + i - 1, startY - hPre, hPre - hCur, 1)
    oled.show()

timerTemp = Timer(0)
timerTemp.init(period=500, mode=Timer.PERIODIC, callback=timerRefresh) # Every 1 second

print('start run')


