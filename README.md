一个基于ESP32C3开发板创建的温度监测模块，用于咖啡生豆烘焙。

硬件的选择和接线图，详见`micropython/main.py`的注释。

# 1. 硬件介绍

## 1.1 主控

合宙ESP32C3-core开发板，只需9.9RMB，多种固件提供支持，拥有WiFi 2.4GHz和蓝牙BLE 5网络链接，非常适合折腾。

本项目采用Micropython固件，并集成ST7789显示屏驱动。已编译好的固件文件，放在`firmware`目录。

相关参考：

- 开发板的官方介绍：[ESP32C3-CORE开发板](https://wiki.luatos.com/chips/esp32c3/board.html)
- Micropython针对ESP32C3的固件下载及刷机说明：[MicroPython - Python for microcontrollers](https://micropython.org/download/ESP32_GENERIC_C3/)
- Micropython的ST7789驱动模块：[Fast MicroPython driver for ST7789 display module written in C](https://github.com/russhughes/st7789_mpy)

## 1.2 温度传感器

K型热电偶MAX6675 + K型探针式铠装热电偶WRNK-191

MAX6675，测温范围0～1024°C，最大精度0.25°C。主要是廉价和够用。

WRNK-191，推荐探针式，反应比较快，探针可弯曲。材质一般为不锈钢304或316，各部分的尺寸和零件都可以定制。适合嵌入各种烘豆设备。

Micropython的MAX6675驱动程序：[https://github.com/BetaRavener/micropython-hw-lib/blob/master/MAX6675/max6675.py](https://github.com/BetaRavener/micropython-hw-lib/blob/master/MAX6675/max6675.py)

## 1.3 显示屏

ST7789，1.3寸TFT彩屏，7针，分辨率240x240。廉价、高分辨率的显示模块。

## 1.4 按钮

自锁开关，用于设置是否正在烘豆。

复位开关，用于设置烘焙过程的五个阶段，包括脱水、转黄、一爆、二爆、结束。按一下，跳到下一个阶段。

# 2. 安装

- 按`micropython/main.py`注释中的电路图，连接好硬件。
- 开发板刷入Micropython固件，该固件文件在`firmware`目录。
- 把`micropython`目录内的文件和子目录，全部上传到开发板。推荐使用Thonny操作。

# 3. 使用

屏幕左上角显示当前烘焙阶段。0：未烘焙，1：脱水，2：转黄，3：一爆，4：二爆，5：结束。

进入“一爆”阶段后，右上角会自动计算“烘焙度”。其计算公式：烘焙度 = 一爆到当前的秒数 / 脱水到当前的秒数 * 100%

屏幕显示的红色曲线，是咖啡豆的温度曲线，即烘焙曲线。蓝色曲线，是按30秒计算一次豆温差的升温曲线，即RoR。

Roast Button，按下表示开始烘焙，左上角显示“1”，即进入“脱水”阶段。反之表示结束烘焙。

Phase Button，按一下，跳到下一阶段。

开始烘焙后，自动记录豆温，直到烘焙结束。相关数据记录在开发板的`record/crc.csv`文件。

把`crc.csv`文件导出到电脑上。用浏览打开`chart/chart.html`网页后，选择导出的`crc.csv`文件，即可生成烘焙曲线和升温曲线。
