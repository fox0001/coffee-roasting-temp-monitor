'''
Project: Coffee Roast Temperature Record
Version: v2.0

Coffee roast curve, CRC, 咖啡烘焙曲线
Rate of Rise, RoR, 升温速率
Development Time Ratio, DTR, 发展率
'''
from micropython import const
import time
from machine import ADC, Pin, SoftI2C, Timer
from max6675 import MAX6675
import st7789
import tft_config
import vga2_8x16 as font
from series_list import SeriesList

SCREEN_BG = st7789.BLACK
SCREEN_W = const(240)
SCREEN_H = const(240)
GRAPH_X = const(0)
GRAPH_Y = const(18)
GRAPH_W = const(SCREEN_W - GRAPH_X)
GRAPH_H = const(SCREEN_H - GRAPH_Y)
TEMP_MAX = const(250)
TEMP_MIN = const(TEMP_MAX - GRAPH_H + 1)
T2G_RATE = (GRAPH_H - 1) / TEMP_MAX
CRC_COLOR = st7789.color565(255, 85, 113)
ROR_MULT = const(10)
ROR_SEC = const(30)
ROR_COLOR = st7789.CYAN
PHASE_DICT = {
    0:'prepare', # 准备，未开始烘焙
    1:'drying phase', # 脱水期
    2:'yellowing phase', # 转黄
    3:'first crack', # 一爆
    4:'second crack', # 二爆
    5:'finish', # 下豆
    }

""" wiring diagram ################################## """
"""
ESP32-C3
TFT: TFT display, 240x240
MAX6675: 
Roast Button: self-locking switch
Phase Button: self-reset switch

                     +[ ESP32-C3 ]--------+   +[ TFT ]-----------+
                     | GND    |  |    GND |---| GND              |
+--[ Roast Button ]--| GPIO00 |  |   3.3V |---| VCC              |
+--[ Phase Button ]--| GPIO01 |  | GPIO02 |---| SCL (SCK)        |
|                    | GPIO12 |  | GPIO03 |---| SDA (MOSI)       |
|                    | GPIO18 |  | GPIO10 |---| RES (Reset)      |
|                    | GPIO19 |  | GPIO06 |---| DC               |
|                    | GND    |  | GPIO07 |---| BLK (Back Light) |
|                    | -      |  | GPIO11 |   +[ MAX6675 ]+------+
|                    | -      |  |    GND |---| GND       |
|                    | GPIO13 |  |   3.3V |---| VCC       |
|                    | NC     |  | GPIO05 |---| SCK       |
|                    | REST   |  | GPIO04 |---| CS        |
+--------------------| 3.3V   |  | GPIO08 |---| SO        |
                     | GND    |  | GPIO09 |   +-----------+
                     | PWB    |  |     5V |
                     | 5V     |  |    GND |
                     |     USB Type-C     |
                     +--------------------+
"""

""" init MAX6675 ################################## """
print('init MAX6675')
sck = Pin(5, Pin.OUT)
cs = Pin(4, Pin.OUT)
so = Pin(8, Pin.IN)
tp = MAX6675(sck, cs, so)
time.sleep_ms(500)
def getTemperature():
    return tp.read()
curTemp = getTemperature()

""" init TFT ################################## """
print('init TFT')
#tft = tft_config.config(0, buffer_size=66*32*2)
tft = tft_config.config(0)
tft.init()
tft.fill(SCREEN_BG)

""" init Button ################################## """
# Phase of coffee roasting
phase = 0
nextPhase = False
# DTR, start time
dtrStart = None

# Roast Button
roastBtn = Pin(0, Pin.IN, Pin.PULL_DOWN)

def isRoast():
    return roastBtn.value() == 1

# Phase Button
phaseBtn = Pin(1, Pin.IN, Pin.PULL_DOWN)
def phaseBtn_irq(btn):
    # Eliminate jitter
    time.sleep_ms(10)
    if not isRoast():
        return
    global nextPhase
    if not nextPhase and btn.value() == 1:
        # Jump to next phase
        nextPhase = True
    #print('nextPhase: {}, phaseBtn: {}'.format(nextPhase, btn.value()))
    
phaseBtn.irq(phaseBtn_irq, Pin.IRQ_RISING)

def getPhase():
    global phase, nextPhase
    p = phase
    if not isRoast():
        p = 0
    elif p == 0:
        p = 1
        nextPhase = False
    elif nextPhase:
        p = 5 if phase >= 5 else phase + 1
        nextPhase = False
    else:
        pass
    #print('phase: {}, {}'.format(phase, PHASE_DICT[phase]))
    return p

""" init Temperature list ################################## """
sList = SeriesList(SCREEN_W, curTemp)

""" init Ticks ################################## """
ticksStart = time.ticks_ms()

""" init Timer ################################## """
def timerRefresh(t):
    #doStart = time.ticks_ms()
    global tp, tft, sList, ticksStart, phase, dtrStart
    
    # Get phase
    curPhase = getPhase()
    #print(f'curPhase: {curPhase}')
    isFirstCrack = False
    if curPhase == 0 and phase != 0:
        ticksStart = time.ticks_ms()
    elif curPhase == 1 and phase != 1:
        # Start roasting, reset duration
        ticksStart = time.ticks_ms()
    elif curPhase == 3 and phase < 3:
        isFirstCrack = True
    elif curPhase == 5 and phase != 5:
        # Stop roasting, reset duration
        ticksStart = time.ticks_ms()
    phase = curPhase
    
    # Get current time
    duration = 0 if ticksStart==None else int(time.ticks_diff(time.ticks_ms(), ticksStart) / 1000)
    dSec = duration % 60
    dMin = int(duration / 60)
    
    # Get DTR, from first crack
    isDtr = True if phase == 3 or phase == 4 else False
    if isDtr:
        if dtrStart is None:
            dtrStart = time.ticks_ms()
            isFirstCrack = True
        dtrSec = int(time.ticks_diff(time.ticks_ms(), dtrStart) / 1000)
        dtr = dtrSec / duration * 100
    else:
        dtrStart = None
    
    # Save current temperature
    curTemp = tp.read()
    sList.append(curTemp, duration, 'first-crack' if isFirstCrack else '-', (phase > 0 and phase < 5))
    
    # Get temperature list
    hList = sList.load()
    hLen = len(hList)
    maxTemp = max(hList)
    minTemp = min(hList)
    tempDiff = hList[hLen-1] - hList[hLen-2] if hLen > 1 else 0
    
    # Show text
    # Show current phase
    tft.text(font, '{:1d}'.format(phase), 0, 0, st7789.GREEN) # 2 characters, left align
    # Duration
    tft.text(font, '{: 3d}:{:02d},'.format(dMin, dSec), font.WIDTH, 0, st7789.WHITE) # 7 characters, left align
    # Current temperature
    tft.text(font, '{:>6.2f} C'.format(curTemp), font.WIDTH * 8, 0, st7789.YELLOW) # 8 characters, left align
    # Temperature difference
    tft.text(font, '      '.format(tempDiff), font.WIDTH * 16, 0, SCREEN_BG) # clean
    if tempDiff != 0:
        tft.text(font, '{:+.2f}'.format(tempDiff), font.WIDTH * 16, 0, st7789.MAGENTA if tempDiff > 0 else st7789.CYAN) # 6 characters, left align
    if isDtr:
        tft.text(font, '{:5.2f}%'.format(dtr), SCREEN_W - (font.WIDTH * 6), 0, st7789.GREEN) # 5 characters, right align
    else:
        # Min temperature
        tft.text(font, '{:2d}'.format(int(minTemp)), SCREEN_W - (font.WIDTH * 6), 0, st7789.BLUE) # (2+4) characters, right align
        # Separator
        tft.text(font, '\x1a', SCREEN_W - (font.WIDTH * 4), 0, st7789.WHITE) # (1+3) characters, right align
        # Max temperature
        tft.text(font, '{:3d}'.format(int(maxTemp)), SCREEN_W - (font.WIDTH * 3), 0, st7789.RED) # 3 characters, right align
    
    # Show graph of temperature list
    startX = GRAPH_W - hLen
    crcPre = None
    rorPre = None
    for i, v in enumerate(hList):
        # Clean
        tft.vline(startX + i, GRAPH_Y, GRAPH_H, SCREEN_BG)
        
        # Draw graph of RoR
        if i >= ROR_SEC:
            rorCur = int(min((int(v) - int(hList[i - ROR_SEC])) * ROR_MULT, TEMP_MAX) * T2G_RATE)
            tft.vline(startX + i, GRAPH_H - 1 - rorCur + GRAPH_Y, (rorCur - rorPre if rorPre is not None and rorPre < rorCur else 1), ROR_COLOR)
            if rorPre is not None and rorPre > rorCur:
                tft.vline(startX + i - 1, GRAPH_H - 1 - rorPre + GRAPH_Y, rorPre - rorCur, ROR_COLOR)
            rorPre = rorCur # Save previous data
        
        # Draw graph of CRC
        crcCur = int(min(v, TEMP_MAX) * T2G_RATE)
        tft.vline(startX + i, GRAPH_H - 1 - crcCur + GRAPH_Y, (crcCur - crcPre if crcPre is not None and crcPre < crcCur else 1), CRC_COLOR)
        if crcPre is not None and crcPre > crcCur:
            tft.vline(startX + i - 1, GRAPH_H - 1 - crcPre + GRAPH_Y, crcPre - crcCur, CRC_COLOR)
        crcPre = crcCur # Save previous data
        
        if i % 10 == 0:
            tft.pixel(startX + i, GRAPH_H - 1 + GRAPH_Y, st7789.WHITE)
    
    #print(time.ticks_diff(time.ticks_ms(), doStart)) # Print process time

timerTemp = Timer(0)
timerTemp.init(period=1000, mode=Timer.PERIODIC, callback=timerRefresh) # Every 1 second

print('start run')


