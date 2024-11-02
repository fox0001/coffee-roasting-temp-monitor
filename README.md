一个基于ESP32C3开发板创建的温度监测模块，用于咖啡生豆烘焙。

硬件的选择和接线图，详见`micropython/main.py`的注释。

## 主控

合宙ESP32C3-core开发板，只需9.9RMB，多种固件提供支持，拥有WiFi 2.4GHz和蓝牙BLE 5网络链接，非常适合折腾。本项目采用Micropython固件，版本为1.20。

Micropython固件下载及刷机说明：[MicroPython - Python for microcontrollers](https://micropython.org/download/ESP32_GENERIC_C3/)

## 温度传感器

K型热电偶MAX6675 + K型探针式铠装热电偶WRNK-191

MAX6675，测温范围0～1024°C，最大精度0.25°C。主要是廉价和够用。

WRNK-191，推荐探针式，反应比较快，探针可弯曲。材质一般为不锈钢304或316，各部分的尺寸和零件都可以定制。适合嵌入各种烘豆设备。

## 显示屏

SSD1306或SSD1315，0.96寸OLED液晶屏，4针，白光，分辨率128x64。主要是廉价。

