# -*- coding: utf-8 -*-
# encoding: utf-8
'''
baidu to google(I guess the original version contributed by zms@newsmth)
http://www.newsmth.net/nForum/#!article/Java/317952?p=6
https://gist.github.com/zxkane/8096237

@author: kane
'''
import math
'''
百度坐标转火星坐标
@param lat,lng 返回(lat,lng)，直接修改自参数
'''
x_pi = math.pi * 3000.0 / 180.0
def bd2gcj(lat, lng):
    x = lng - 0.0065
    y = lat - 0.006;
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi);
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi);
    return (z * math.sin(theta), z * math.cos(theta))

'''
火星坐标转百度坐标
@param lat,lng 返回(lat,lng)，直接修改自参数
 '''
def gcj2bd(lat, lng):
    x = lng
    y = lat;
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * x_pi);
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * x_pi);
    return (z * math.sin(theta) + 0.006, z * math.cos(theta) + 0.0065)