#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sxtwl 兼容层 — 基于 lunar_python（6tail lunar 的 Python 移植）实现。
让依赖 sxtwl 的 paipan.py 在本机无需编译 C++ 扩展即可获得同等精确的排盘能力。
lunar_python 底层同样使用寿星天文历算法，八字/节气精度与 sxtwl 一致。

用法：将本文件命名为 sxtwl.py 并放在 paipan.py 同目录，
      Python 的模块解析会优先命中本地文件，paipan.py 的 `import sxtwl` 无需任何修改。
"""
# -*- coding: utf-8 -*-

from lunar_python import Solar, LunarYear
from datetime import datetime

# 节气名（与 paipan.py JIEQI_NAMES 一致，索引即 jqIndex）
JIEQI_NAMES = [
    '冬至', '小寒', '大寒', '立春', '雨水', '惊蛰',
    '春分', '清明', '谷雨', '立夏', '小满', '芒种',
    '夏至', '小暑', '大暑', '立秋', '处暑', '白露',
    '秋分', '寒露', '霜降', '立冬', '小雪', '大雪',
]

TG = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DZ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


class GZ:
    """干支（与 sxtwl 的 GZ 对象兼容：.tg 天干索引 0-9, .dz 地支索引 0-11）"""
    __slots__ = ('tg', 'dz')

    def __init__(self, tg, dz):
        self.tg = tg
        self.dz = dz

    def __repr__(self):
        return f'GZ({TG[self.tg]}{DZ[self.dz]})'


def _str_to_gz(s):
    """'癸未' → GZ(9, 7)"""
    return GZ(TG.index(s[0]), DZ.index(s[1]))


class Time:
    """时间对象（与 sxtwl.Time 兼容）"""
    __slots__ = ('y', 'm', 'd', 'h', 'min', 's')

    def __init__(self, y, m, d, h=0, min=0, s=0):
        self.y, self.m, self.d, self.h, self.min, self.s = y, m, d, h, min, s

    def __repr__(self):
        return f'Time({self.y}-{self.m}-{self.d} {self.h}:{self.min}:{self.s})'


class Day:
    """某一天（与 sxtwl.fromSolar 返回对象兼容）"""
    def __init__(self, year, month, day):
        self.year, self.month, self.day = year, month, day
        self._solar = Solar.fromYmdHms(year, month, day, 12, 0, 0)
        self._lunar = self._solar.getLunar()
        self._ec = self._lunar.getEightChar()
        # sect=2：晚子时（23:00-23:59）日柱算当天（与 sxtwl 默认一致）
        self._ec.setSect(2)

    def getYearGZ(self):
        return _str_to_gz(self._ec.getYear())

    def getMonthGZ(self):
        return _str_to_gz(self._ec.getMonth())

    def getDayGZ(self):
        return _str_to_gz(self._ec.getDay())

    def getHourGZ(self, hour):
        """按小时取时柱（hour: 0-23）。sxtwl 语义：基于当天日柱起时柱。"""
        solar = Solar.fromYmdHms(self.year, self.month, self.day, hour, 0, 0)
        ec = solar.getLunar().getEightChar()
        ec.setSect(2)
        return _str_to_gz(ec.getTime())

    def hasJieQi(self):
        return bool(self._lunar.getJieQi())

    def getJieQi(self):
        """返回节气索引（对应 paipan.py 的 JIEQI_NAMES），非节气日返回 -1"""
        name = self._lunar.getJieQi()
        if not name:
            return -1
        if name in JIEQI_NAMES:
            return JIEQI_NAMES.index(name)
        # lunar_python 可能返回英文名（如 DA_XUE）
        en_map = {
            'DONG_ZHI': 0, 'XIAO_HAN': 1, 'DA_HAN': 2, 'LI_CHUN': 3,
            'YU_SHUI': 4, 'JING_ZHE': 5, 'CHUN_FEN': 6, 'QING_MING': 7,
            'GU_YU': 8, 'LI_XIA': 9, 'XIAO_MAN': 10, 'MANG_ZHONG': 11,
            'XIA_ZHI': 12, 'XIAO_SHU': 13, 'DA_SHU': 14, 'LI_QIU': 15,
            'CHU_SHU': 16, 'BAI_LU': 17, 'QIU_FEN': 18, 'HAN_LU': 19,
            'SHUANG_JIANG': 20, 'LI_DONG': 21, 'XIAO_XUE': 22, 'DA_XUE': 23,
        }
        return en_map.get(name, -1)


class JieQi:
    """节气对象（与 sxtwl getJieQiByYear 返回元素兼容：.jd, .jqIndex）"""
    __slots__ = ('jd', 'jqIndex')

    def __init__(self, jd, jqIndex):
        self.jd = jd
        self.jqIndex = jqIndex

    def __repr__(self):
        return f'JieQi(jd={self.jd}, idx={self.jqIndex})'


def fromSolar(year, month, day):
    """sxtwl.fromSolar 等价"""
    return Day(year, month, day)


def toJD(t):
    """sxtwl.toJD 等价：Time → 儒略日（float）"""
    return Solar.fromYmdHms(t.y, t.m, t.d, t.h, t.min, t.s).getJulianDay()


def getJieQiByYear(year):
    """sxtwl.getJieQiByYear 等价：返回该年（含前后跨年）全部节气列表。

    lunar_python 的 LunarYear.getJieQiJulianDays() 返回 31 个 JD，
    顺序从上一年的 DA_XUE 到下一年的 小寒 附近。为兼容 paipan.py 的
    '收集前后三年 → 排序 → 找最近节气' 逻辑，这里返回 (jd, 近似索引) 列表，
    索引仅用于排序参考，paipan.py 实际只用 jd。
    """
    jds = LunarYear.fromYear(year).getJieQiJulianDays()
    out = []
    for i, jd in enumerate(jds):
        # lunar_python 列表从 DA_XUE(23) 开始：24 节气 + 次年 7 个
        out.append(JieQi(jd, (i + 23) % 24))
    return out


if __name__ == '__main__':
    # 自检：2004-01-19 12:00 应得 癸未 乙丑 丁酉 丙午
    d = fromSolar(2004, 1, 19)
    print('年柱:', d.getYearGZ())
    print('月柱:', d.getMonthGZ())
    print('日柱:', d.getDayGZ())
    print('时柱(12时):', d.getHourGZ(12))
    print('节气日?', d.hasJieQi(), '索引:', d.getJieQi())
    t = Time(2004, 1, 19, 12, 0, 0)
    print('JD:', toJD(t))
    print('2004节气数:', len(getJieQiByYear(2004)))
