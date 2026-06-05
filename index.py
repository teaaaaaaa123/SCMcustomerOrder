#!/usr/bin/env python3
"""
客商订单管理技能 - Python入口文件
支持创建订单、查询订单状态、修改订单信息、取消订单等功能
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta

import requests

# API配置
API_CONFIG = {
    "login_url": "http://api.ceyadi.cn/v1/oauth/getToken",
    "order_add_url": "http://api.ceyadi.cn/v1/order/add",
    "order_info_url": "http://api.ceyadi.cn/v1/order/info",
    "order_page_url": "http://api.ceyadi.cn/v1/order/page",
    "order_items_add_url": "http://api.ceyadi.cn/v1/orderItems/add",
    "order_items_list_url": "http://api.ceyadi.cn/v1/orderItems/list",
    # 基础信息API
    "pattern_type_list_url": "http://api.ceyadi.cn/v1/patternType/list",
    "pattern_list_url": "http://api.ceyadi.cn/v1/pattern/list",
    "massing_list_url": "http://api.ceyadi.cn/v1/massing/list",
    "pattern_attr_list_url": "http://api.ceyadi.cn/v1/patternAttr/list",
    "pattern_attr_type_list_url": "http://api.ceyadi.cn/v1/patternAttrType/list",
    "pattern_structure_list_url": "http://api.ceyadi.cn/v1/patternStructure/list",
    "pattern_structure_type_list_url": "http://api.ceyadi.cn/v1/patternStructureType/list",
    "special_massing_list_url": "http://api.ceyadi.cn/v1/specialMassing/list",
    "specs_info_by_code_url": "http://api.ceyadi.cn/v1/specs/info_byCode",
    # 图片上传API
    "upload_url": "http://api.ceyadi.cn/v1/upload/image",
    "access_key_id": "xx",
    "access_key_secret": "xx",
    "cached_token": None
}

# 模拟订单存储（实际应用中应使用数据库）
ORDERS_STORAGE = "orders.json"

# 定制选项映射表 - 自动从版型属性数据1.xlsx生成
custom_option_mappings = {
    "DY_coatPockets": {
        "4KN1075斜双支线袋": "DY_coatPockets_xszxd",
        "A款 直斜插袋": "DY_coatPockets_zxcd",
        "B款 明袋": "DY_coatPockets_bkmd",
        "C款 两袋盖": "DY_coatPockets_dg",
        "D款 明袋加袋盖": "DY_coatPockets_mdjdg",
        "E款 明袋加西装袋盖": "DY_coatPockets_ekmdjxzdg",
        "F款 单开线加袋盖": "DY_coatPockets_fkdkxjdg",
        "G款 弧型斜插袋": "DY_coatPockets_gkhxxcd",
        "H款 袋盖斜插袋": "DY_coatPockets_dgxcd",
        "I款 袋盖斜插袋": "DY_coatPockets_ikdgjxd",
        "J款 斜袋袋盖小料": "DY_coatPockets_jkxddg",
        "K款 斜插明袋": "DY_coatPockets_kkxcmd",
        "L款 三袋盖": "DY_coatPockets_lksdg",
        "M款 明袋加斜袋盖": "DY_coatPockets_mdjxdg",
        "N款 可侧插明袋加袋盖": "DY_coatPockets_Nk",
        "O款 加大版 明袋加袋盖": "DY_coatPockets_jdbmdjdg",
        "P款 明袋袋盖 加斜插袋": "DY_coatPockets_pkkd",
        "Q款：立体明袋袋盖 加斜插袋": "DY_coatPockets_ltmdjxcd",
        "专用口袋": "DY_coatPockets_zymd",
        "双支线": "DY_coatPockets_szx",
        "拼接明袋": "DY_coatPockets_pjmd",
        "无": "DY_coatPockets_wu",
    },
    "DY_coatSleeveButton": {
        "一扣": "DY_coatSleeveButton_oneBuckle",
        "专用袖扣": "DY_coatSleeveButton_zyxk",
        "叠扣": "DY_coatSleeveButton_dk",
        "平扣": "DY_coatSleeveButton_flatBuckle",
        "斜扣	": "DY_coatSleeveButton_diagonalBuckle",
        "斜眼叠扣": "DY_coatSleeveButton_slantBuckle",
        "斜眼平扣": "DY_coatSleeveButton_flatFoldingBuckle",
        "无": "DY_coatSleeveButton_wu",
        "翻折 7.5cm": "DY_coatSleeveButton_fz7.5",
        "翻折10.8cm": "DY_coatSleeveButton_fz10.8",
        "翻折6CM": "DY_coattSleeveButton_bz6cm",
        "翻折9.5cm": "DY_coatSleeveButton_xkfb9.5",
        "袖袢": "DY_coatSleeveButton_xb",
    },
    "DY_craft": {
        "全麻衬": "DY_craft_fullCanvas",
        "半麻衬": "DY_craft_bmc",
        "粘合衬": "DY_craft_adhesionCanvas",
    },
    "DY_cuffKeyhole": {
        "一扣": "DY_cuffKeyhole_oneButton ",
        "三扣": "DY_cuffKeyhole_threeBuckles",
        "二扣": "DY_cuffKeyhole_twoBuckles",
        "五扣": "DY_cuffKeyhole_fiveBuckles",
        "四扣": "DY_cuffKeyhole_fourBuckles",
        "无": "DY_cuffKeyhole_wu",
    },
    "DY_curvedHandmadeColor": {
        "000": "DY_curvedHandmadeColor_000",
        "130": "DY_curvedHandmadeColor_130",
        "131": "DY_curvedHandmadeColor_131",
        "155": "DY_curvedHandmadeColor_155",
        "174": "DY_curvedHandmadeColor_174",
        "196": "DY_curvedHandmadeColor_196",
        "214": "DY_curvedHandmadeColor_214",
        "247": "DY_curvedHandmadeColor_247",
        "339": "DY_curvedHandmadeColor_339",
        "367": "DY_curvedHandmadeColor_367",
        "387": "DY_curvedHandmadeColor_387",
        "412": "DY_curvedHandmadeColor_412",
        "440": "DY_curvedHandmadeColor_440",
        "454": "DY_curvedHandmadeColor_454",
        "46": "DY_curvedHandmadeColor_46",
        "540": "DY_curvedHandmadeColor_540",
        "542": "DY_curvedHandmadeColor_542",
        "665": "DY_curvedHandmadeColor_665",
        "697": "DY_curvedHandmadeColor_697",
        "701": "DY_curvedHandmadeColor_701",
        "702": "DY_curvedHandmadeColor_702",
        "769": "DY_curvedHandmadeColor_769",
        "800": "DY_curvedHandmadeColor_800",
        "802": "DY_curvedHandmadeColor_802",
        "810": "DY_curvedHandmadeColor_810",
        "812": "DY_curvedHandmadeColor_812",
        "889": "DY_curvedHandmadeColor_889",
        "909": "DY_curvedHandmadeColor_909",
        "925": "DY_curvedHandmadeColor_925",
        "964": "DY_curvedHandmadeColor_964",
        "顺色": "DY_curvedHandmadeColor_matchFabric",
    },
    "DY_halfAMile": {
        "半里包边	": "DY_halfAMile_halfMileEdging",
        "锁边翘边": "DY_halfAMile_lockingAndWarping	",
    },
    "DY_hbks": {
        "4KN041 A款": "DY_hbks_ak",
        "4KN041无腰带款": "DY_hbks_ak041",
        "4KN042 A款": "DY_hbks_ak042",
        "4KN042 A腰带款": "DY_hbks_ak042yyd",
        "4KN045中开叉": "DY_hbks_zkc045",
        "4KN045无叉款": "DY_hbks_wck045",
        "4KN993 A款": "DY_hbks_dazhonak",
        "4KN993 B款": "DY_hbks_dazhobk",
        "A款": "DY_hbks_akzy",
        "B款": "DY_hbks_bk",
        "C款": "DY_hbks_ck",
    },
    "DY_jacketButtonholeColor": {
        "000": "DY_jacketButtonholeColor_000",
        "130": "DY_jacketButtonholeColor_130",
        "131": "DY_jacketButtonholeColor_131",
        "155": "DY_jacketButtonholeColor_155",
        "174": "DY_jacketButtonholeColor_174",
        "196": "DY_jacketButtonholeColor_196",
        "214": "DY_jacketButtonholeColor_214",
        "247": "DY_jacketButtonholeColor_247",
        "339": "DY_jacketButtonholeColor_339",
        "367": "DY_jacketButtonholeColor_367",
        "387": "DY_jacketButtonholeColor_387",
        "412": "DY_jacketButtonholeColor_412",
        "440": "DY_jacketButtonholeColor_440",
        "454": "DY_jacketButtonholeColor_454",
        "46": "DY_jacketButtonholeColor_46",
        "540": "DY_jacketButtonholeColor_540",
        "542": "DY_jacketButtonholeColor_542",
        "665": "DY_jacketButtonholeColor_665",
        "697": "DY_jacketButtonholeColor_697",
        "701": "DY_jacketButtonholeColor_701",
        "702": "DY_jacketButtonholeColor_702",
        "769": "DY_jacketButtonholeColor_769",
        "800": "DY_jacketButtonholeColor_800",
        "802": "DY_jacketButtonholeColor_802",
        "810": "DY_jacketButtonholeColor_810",
        "812": "DY_jacketButtonholeColor_812",
        "889": "DY_jacketButtonholeColor_889",
        "909": "DY_jacketButtonholeColor_909",
        "925": "DY_jacketButtonholeColor_925",
        "964": "DY_jacketButtonholeColor_964",
        "顺色": "DY_jacketButtonholeColor_matchFabric",
    },
    "DY_overcoatButtonHole": {
        "双边米兰眼": "DY_overcoatButtonHole_sbly",
        "取消驳头锁眼": "DY_overcoatButtonHole_cancelLapelButtonhole",
        "手工米兰眼": "DY_overcoatButtonHole_milanese",
        "机器锁眼": "DY_overcoatButtonHole_machineMade ",
        "艾伦眼": "DY_overcoatButtonHole_curvedHandmade",
    },
    "DY_placketKeyhole": {
        "一扣": "DY_placketKeyhole_oneButton ",
        "一明扣三暗扣": "DY_placketKeyhole_ymksaks",
        "一明扣四暗扣": "DY_placketKeyhole_ymksak",
        "三扣": "DY_placketKeyhole_sq",
        "二扣": "DY_placketKeyhole_twoBuckles",
        "二扣半": "DY_placketKeyhole_twoAndAHalfBuckles",
        "八扣四": "DY_placketKeyhole_bks",
        "六扣一": "DY_placketKeyhole_sixBucklesAndOne",
        "六扣三": "DY_placketKeyhole_lks",
        "六扣二": "DY_placketKeyhole_sixBucklesAndTwo",
        "十扣三": "DY_placketKeyhole_sksnk",
        "十扣五": "DY_placketKeyhole_sbkw",
        "四扣": "DY_placketKeyhole_4b",
        "四扣一": "DY_placketKeyhole_fourBucklesAndone",
        "四扣二": "DY_placketKeyhole_fourBucklesAndWwo",
    },
    "DY_safariSuit": {
        "抽绳款": "DY_safariSuit_pullOutPayment",
        "腰带款": "DY_safariSuit_beltStyle",
    },
    "DY_sjd": {
        "一个圆角打褶明袋加斜袋盖": "DY_sjd_yjdzmdjxdg",
        "上两直手巾袋": "DY_sjd_slzsjd",
        "两个打褶圆角明袋加袋盖": "DY_sjd_dzyjmdjdg",
        "两个打褶直角明袋加袋盖": "DY_sjd_dzjjmdjdg",
        "双支线加袋盖": "DY_sjd_szxjdg",
        "小明袋": "DY_sjd_xmd",
        "小酒杯明袋": "DY_sjd_xjbmd",
        "弧形小明袋": "DY_sjd_hxxmd",
        "弧手巾袋": "DY_sjd_hsjd",
        "斜插双支线袋": "DY_sjd_xcszxd",
        "无": "DY_sjd_wu",
        "直手巾袋": "DY_sjd_zsjd",
        "船型手巾袋": "DY_sjd_CXSJD",
    },
    "LZ_bl": {
        "半里包边": "LZ_bl_blbb",
        "锁边翘边": "LZ_bl_sbqb",
    },
    "LZ_bllbfg": {
        "一字后里": "LZ_bllbfg_yzhl",
        "交叉后里": "LZ_bllbfg_jchl",
        "前全里后半里": "LZ_bllbfg_qqlhbl",
    },
    "LZ_btsy": {
        "双边米兰眼": "LZ_btsy_sbmly",
        "取消驳头锁眼": "LZ_btsy_qxbtsy",
        "圆头锁眼": "LZ_btsy_ytsy",
        "手工圆头1.5圆头锁眼": "LZ_btsy_sgyt",
        "手工圆头锁眼": "LZ_btsy_sgytsy",
        "手工米兰眼": "LZ_btsy_sgmly",
        "机器锁眼": "LZ_btsy_yqsy",
        "艾伦眼": "LZ_btsy_aly",
    },
    "LZ_gy": {
        "全麻衬": "LZ_gy_qmc",
        "半麻衬": "LZ_gy_bmc",
        "无结构": "LZ_gy_wjg",
    },
    "LZ_lz": {
        "抽绳款": "LZ_lz_csk",
        "腰带款": "LZ_lz_ydk",
    },
    "LZ_mjsy": {
        "一扣": "LZ_mjsy_1b",
        "一明扣四暗扣": "LZ_mjsy_1mksak",
        "一暗扣两明扣": "LZ_mjsy_yaklmk",
        "三扣": "LZ_mjsy_3sk",
        "三扣二": "LZ_mjsy_3kr",
        "二扣": "LZ_mjsy_2B",
        "二扣一": "LZ_mjsy_2ky",
        "二扣半": "LZ_mjsy_2KB",
        "五扣": "LZ_mjsy_5k",
        "六扣": "LZ_mjsy_lk",
        "六扣一": "LZ_mjsy_6ky",
        "六扣二": "LZ_mjsy_6kr",
        "四扣": "LZ_mjsy_4b",
        "四扣一": "LZ_mjsy_4ky",
        "四扣二": "LZ_mjsy_4skr",
        "对扣": "LZ_mjsy_dk",
    },
    "LZ_sjd": {
        "1JAS03专用口袋": "LZ_sjd_jaszykd",
        "1SF014专用口袋": "LZ_sjd_1sf014zykd",
        "1SF024专用口袋": "LZ_sjd_1SF024zy",
        "1SF028专用口袋": "LZ_sjd_1SF028",
        "MG口袋": "LZ_sjd_mgkd",
        "SA": "LZ_sjd_SA",
        "SA立体": "LZ_sjd_SAlt",
        "SB": "LZ_sjd_SB",
        "SC": "LZ_sjd_SC",
        "SC立体": "LZ_sjd_sclt",
        "SD": "LZ_sjd_SD",
        "SE": "LZ_sjd_SE",
        "SF": "LZ_sjd_SF",
        "SH": "LZ_sjd_SH",
        "SI": "LZ_sjd_SI",
        "SI立体": "LZ_sjd_silt",
        "SJ": "LZ_sjd_SJ",
        "SK": "LZ_sjd_SK",
        "SL": "LZ_sjd_SL",
        "SM": "LZ_sjd_SM",
        "SM立体": "LZ_sjd_smltmdjdg",
        "SN": "LZ_sjd_sn",
        "SS": "LZ_sjd_ss",
        "ST": "LZ_sjd_st",
        "Y款 圆角打褶明袋": "LZ_sjd_yk",
        "弧手巾袋": "LZ_sjd_hsjd",
    },
    "LZ_syhc": {
        "不开叉": "LZ_syhc_bkc",
        "中开叉": "LZ_syhc_zkc",
        "双开叉": "LZ_syhc_skc",
    },
    "LZ_symdd": {
        "1JAS03专用口袋": "LZ_symdd_jaszyd",
        "1SF006专用口袋": "LZ_symdd_sf006",
        "1SF012专用口袋": "LZ_symdd_1sf012zykd",
        "1SF014专用口袋": "LZ_symdd_1sf014zykd",
        "1SF019专用口袋": "LZ_symdd_1sf019md",
        "1SF021专用口袋": "LZ_symdd_zymd",
        "1SF024专用口袋": "LZ_symdd_1SF024",
        "1SF035专用口袋": "LZ_symdd_zykd035",
        "1SF044": "LZ_symdd_zykd1sf044",
        "A款 两直袋盖": "LZ_symdd_lzdg",
        "B款 两明袋": "LZ_symdd_bklmd",
        "C款 双支线": "LZ_symdd_szx",
        "MA": "LZ_symdd_MA",
        "MA立体": "LZ_symdd_MAlt",
        "MB": "LZ_symdd_MB",
        "MC": "LZ_symdd_MC",
        "MC立体": "LZ_symdd_mclt",
        "MD": "LZ_symdd_MD",
        "ME": "LZ_symdd_ME",
        "MG三明袋": "LZ_symdd_MG",
        "MH": "LZ_symdd_MH",
        "MI": "LZ_symdd_MI",
        "MI立体": "LZ_symdd_milt",
        "MJ": "LZ_symdd_MJ",
        "MK": "LZ_symdd_MK",
        "ML": "LZ_symdd_ML",
        "MM": "LZ_symdd_MM",
        "MM立体": "LZ_symdd_mmltmd",
        "MN": "LZ_symdd_MN",
        "MO": "LZ_symdd_MO",
        "MP": "LZ_symdd_mpkd",
        "MQ": "LZ_symdd_mq",
        "MR": "LZ_symdd_mr",
        "MS": "LZ_symdd_mskd",
        "MT": "LZ_symdd_mtkd",
        "Y款 圆角打褶明袋": "LZ_symdd_yk",
        "同工艺书": "LZ_symdd_tgys",
    },
    "LZ_syxk": {
        "一扣": "LZ_syxk_xxyk",
        "叠扣": "LZ_syxk_dk",
        "平扣": "LZ_syxk_pk",
        "斜扣": "LZ_syxk_xk",
        "斜眼叠扣": "LZ_syxk_xdk",
        "斜眼平扣": "LZ_syxk_xpk",
        "袖克夫圆头": "LZ_syxk_xkfyt",
        "袖克夫尖头": "LZ_syxk_xkfjt",
        "贴边": "LZ_syxk_tb",
    },
    "LZ_xc": {
        "三层胸衬": "LZ_xc_scxc",
        "二层胸衬": "LZ_xc_ecxc",
        "五层胸衬": "LZ_xc_wcxc",
        "四层胸衬": "LZ_xc_scxc4",
        "无胸衬": "LZ_xc_wxc",
    },
    "LZ_xksy": {
        "一扣": "LZ_xksy_1b",
        "三扣": "LZ_xksy_3b",
        "二扣": "LZ_xksy_2b",
        "五扣": "LZ_xksy_5B",
        "六扣": "LZ_xksy_6B",
        "四扣": "LZ_xksy_4B",
    },
    "LZ_xt": {
        "无袖弹": "LZ_xt_wxt",
        "有袖弹": "LZ_xt_yxt",
        "袖弹一层棉": "LZ_xt_xtycm",
    },
    "LZ_xz": {
        "1SF035无袖里专用袖": "LZ_xz_1SF035wxlzyx",
        "1SF035有袖里专用袖": "LZ_xz_1sf035wxl",
        "A款袖克夫1扣": "LZ_xz_typec",
        "B款袖开叉1扣": "LZ_xz_typea",
        "C款无袖里袖克夫1扣": "LZ_xz_typeb",
        "D款无袖里开叉一扣": "LZ_xz_akwxl",
        "专用袖": "LZ_xz_zyx",
    },
    "LZ_ydj": {
        "0.2cm": "LZ_ydj_0.2",
        "0.5cm": "LZ_ydj_0.5",
        "0.7cm": "LZ_ydj_0.7",
        "1.5cm": "LZ_ydj_1.5",
        "1cm": "LZ_ydj_1",
        "无垫肩": "LZ_ydj_wdj",
    },
    "LZ_zdj": {
        "0.2cm": "LZ_zdj_0.2",
        "0.5cm": "LZ_zdj_0.5",
        "0.7cm": "LZ_zdj_0.7",
        "1.5cm": "LZ_zdj_1.5",
        "1cm": "LZ_zdj_1",
        "无垫肩": "LZ_zdj_wdj",
    },
    "MJ_mjhx": {
        "不开叉": "MJ_mjhx_bkc",
        "中开叉": "MJ_mjhx_zkc",
        "侧开叉": "MJ_mjhx_ckx",
        "侧面和后中都开叉": "MJ_mjhx_czkc",
    },
    "MJ_sjd": {
        "上两直手巾袋": "MJ_sjd_slzsjd",
        "专用明袋": "MJ_sjd_zymd",
        "弧形小明袋": "MJ_sjd_hxxmd",
        "弧手巾袋": "MJ_sjd_hsjd",
        "无": "MJ_sjd_wu",
        "直手巾袋": "MJ_sjd_zsjd",
    },
    "MJ_waistBack": {
        "本料": "MJ_waistBack_bl",
        "里布": "MJ_waistBack_lb",
    },
    "MJ_xkd": {
        "下两明袋": "MJ_xkd_xlmd",
        "专用明袋": "MJ_xkd_zymd",
        "两斜袋盖": "MJ_xkd_lxdg",
        "单支线开袋": "MJ_xkd_dzxkd",
        "双支线加袋盖": "MJ_xkd_szxjdg",
        "双支线开袋": "MJ_xkd_szxkd",
        "弧形手巾袋": "MJ_xkd_barchetta",
        "手巾袋": "MJ_xkd_sjd",
        "斜双支线开袋": "MJ_xkd_slantJetted",
        "无": "MJ_xkd_wu",
    },
    "SY_craft": {
        "全麻衬": "SY_craft_qmc",
        "半麻衬": "SY_craft_bmc",
        "无结构": "SY_craft_wjg",
    },
    "SY_cuffKeyhole": {
        "一扣	": "SY_cuffKeyhole_oneButton",
        "三扣": "SY_cuffKeyhole_threeBuckles",
        "二扣	 ": "SY_cuffKeyhole_twoBuckles",
        "五扣": "SY_cuffKeyhole_fiveBuckles",
        "六扣": "SY_cuffKeyhole_6b",
        "四扣": "SY_cuffKeyhole_fourBuckles",
    },
    "SY_curvedHandmadeColor": {
        "000": "SY_curvedHandmadeColor_000",
        "130": "SY_curvedHandmadeColor_130",
        "131": "SY_curvedHandmadeColor_131",
        "155": "SY_curvedHandmadeColor_155",
        "174": "SY_curvedHandmadeColor_174",
        "196": "SY_curvedHandmadeColor_196",
        "214": "SY_curvedHandmadeColor_214",
        "247": "SY_curvedHandmadeColor_247",
        "339": "SY_curvedHandmadeColor_339",
        "367": "SY_curvedHandmadeColor_367",
        "387": "SY_curvedHandmadeColor_387",
        "412": "SY_curvedHandmadeColor_412",
        "440": "SY_curvedHandmadeColor_440",
        "454": "SY_curvedHandmadeColor_454",
        "46": "SY_curvedHandmadeColor_46",
        "540": "SY_curvedHandmadeColor_540",
        "542": "SY_curvedHandmadeColor_542",
        "665": "SY_curvedHandmadeColor_665",
        "697": "SY_curvedHandmadeColor_697",
        "701": "SY_curvedHandmadeColor_701",
        "702": "SY_curvedHandmadeColor_702",
        "769": "SY_curvedHandmadeColor_769",
        "800": "SY_curvedHandmadeColor_800",
        "802": "SY_curvedHandmadeColor_802",
        "810": "SY_curvedHandmadeColor_810",
        "812": "SY_curvedHandmadeColor_812",
        "889": "SY_curvedHandmadeColor_889",
        "909": "SY_curvedHandmadeColor_909",
        "925": "SY_curvedHandmadeColor_925",
        "964": "SY_curvedHandmadeColor_964",
        "顺色": "SY_curvedHandmadeColor_matchFabric",
    },
    "SY_halfAMile": {
        "半里包边": "SY_halfAMile_halfMileEdging",
        "锁边翘边": "SY_halfAMile_lockingAndWarping",
    },
    "SY_halfMileLiningStyle": {
        "一字后里": "SY_halfMileLiningStyle_yzhl",
        "交叉后里": "SY_halfMileLiningStyle_jxhl",
        "前全里后半里": "SY_halfMileLiningStyle_qqlhbl",
    },
    "SY_jacketButtonhole": {
        "不开口手工米兰眼": "SY_jacketButtonhole_bkksgmly",
        "双边手工圆头锁眼": "SY_jacketButtonhole_sbsgytsy",
        "双边米兰眼": "SY_jacketButtonhole_sbmly",
        "取消驳头锁眼": "SY_jacketButtonhole_qxbtsy",
        "圆头锁眼": "SY_jacketButtonhole_ytsy",
        "手工圆头1.5cm圆头锁眼": "SY_jacketButtonhole_sgytsy1.5",
        "手工圆头2cm圆头锁眼": "SY_jacketButtonhole_sgytsy2",
        "手工圆头锁眼": "SY_jacketButtonhole_qxytsy",
        "手工米兰眼": "SY_jacketButtonhole_sgmly",
        "机器锁眼": "SY_jacketButtonhole_jqsy",
        "艾伦眼": "SY_jacketButtonhole_aly",
    },
    "SY_jacketButtonholeColor": {
        "000": "SY_jacketButtonholeColor_000",
        "130": "SY_jacketButtonholeColor_130",
        "131": "SY_jacketButtonholeColor_131",
        "155": "SY_jacketButtonholeColor_155",
        "174": "SY_jacketButtonholeColor_174",
        "196": "SY_jacketButtonholeColor_196",
        "214": "SY_jacketButtonholeColor_214",
        "247": "SY_jacketButtonholeColor_247",
        "310": "SY_jacketButtonholeColor_310",
        "339": "SY_jacketButtonholeColor_339",
        "367": "SY_jacketButtonholeColor_367",
        "387": "SY_jacketButtonholeColor_387",
        "412": "SY_jacketButtonholeColor_412",
        "440": "SY_jacketButtonholeColor_440",
        "454": "SY_jacketButtonholeColor_454",
        "46": "SY_jacketButtonholeColor_46",
        "540": "SY_jacketButtonholeColor_540",
        "542": "SY_jacketButtonholeColor_542",
        "665": "SY_jacketButtonholeColor_665",
        "697": "SY_jacketButtonholeColor_697",
        "701": "SY_jacketButtonholeColor_701",
        "702": "SY_jacketButtonholeColor_702",
        "707": "SY_jacketButtonholeColor_707",
        "769": "SY_jacketButtonholeColor_769",
        "800": "SY_jacketButtonholeColor_800",
        "802": "SY_jacketButtonholeColor_802",
        "810": "SY_jacketButtonholeColor_810",
        "812": "SY_jacketButtonholeColor_812",
        "889": "SY_jacketButtonholeColor_889",
        "909": "SY_jacketButtonholeColor_909",
        "925": "SY_jacketButtonholeColor_925",
        "964": "SY_jacketButtonholeColor_964",
        "顺色": "SY_jacketButtonholeColor_matchFabric",
    },
    "SY_jacketChestLining": {
        "一层胸衬": "SY_jacketChestLining_ycxc",
        "三层胸衬": "SY_jacketChestLining_threeLayerChestLining",
        "二层胸衬": "SY_jacketChestLining_ecxc",
        "五层胸衬": "SY_jacketChestLining_fiveLayerChestLining",
        "四层胸衬": "SY_jacketChestLining_scxc",
        "无胸衬": "SY_jacketChestLining_wxc",
    },
    "SY_jacketPockets": {
        "1SF012专用口袋": "SY_jacketPockets_zykd",
        "AA款 立体直角明袋加直角袋盖": "SY_jacketPockets_ltzjmdjzjdg",
        "AB款 切角拼接明袋": "SY_jacketPockets_abkqjpjmd",
        "AC款 切角拼接三明袋": "SY_jacketPockets_ackqjpjsmd",
        "AD款": "SY_jacketPockets_aekkd",
        "AE款 风琴袋": "SY_jacketPockets_fqd",
        "AF款 三斜双支线袋": "SY_jacketPockets_SlidePocketJetted",
        "AG款 上口压线两明袋": "SY_jacketPockets_agskyxlmd",
        "AH款 斜插袋": "SY_jacketPockets_xcd",
        "AI款": "SY_jacketPockets_ahkkd",
        "AJ款 单支线袋盖": "SY_jacketPockets_singleBranchBagCover",
        "AK下三明袋": "SY_jacketPockets_akxsmd",
        "AK专用打褶明袋": "SY_jacketPockets_dzmd",
        "AK款 明袋": "SY_jacketPockets_akmd",
        "AL款 两斜袋盖加斜双支线": "SY_jacketPockets_xlxdgjxszx",
        "AM款 弧形明袋加袋盖": "SY_jacketPockets_amkhxlmdjdg",
        "AN款": "SY_jacketPockets_ank",
        "AO款 两袋盖加小单支线袋": "SY_jacketPockets_aokldgjxdzxq",
        "AP款 斜单支线袋": "SY_jacketPockets_apkxszxd",
        "A款 两直袋盖": "SY_jacketPockets_gd",
        "B款 两明袋": "SY_jacketPockets_md",
        "C款 双支线": "SY_jacketPockets_szx",
        "D款 两弧形明袋": "SY_jacketPockets_lhxmd",
        "E款 两明袋加袋盖": "SY_jacketPockets_mdjgd",
        "F款 下三明袋": "SY_jacketPockets_xsmd",
        "G款 下三双支线": "SY_jacketPockets_xszx",
        "H款 两弧形双支线袋": "SY_jacketPockets_hklhxszxd",
        "I款 酒杯明袋": "SY_jacketPockets_jbmd",
        "J款 水滴明袋": "SY_jacketPockets_sdmd",
        "K款 三直袋盖": "SY_jacketPockets_sxdg",
        "L款 两斜袋盖": "SY_jacketPockets_lxdg",
        "MK": "SY_jacketPockets_mk",
        "MM款": "SY_jacketPockets_MM",
        "M款 两斜双支线袋": "SY_jacketPockets_lxszxd",
        "N款 三斜袋盖": "SY_jacketPockets_tripleInclinedBagCover",
        "O款 三弧形明袋": "SY_jacketPockets_xshxmd",
        "P款 两袋盖加小双支线": "SY_jacketPockets_xldgjszx",
        "Q款 圆角打褶明袋加直袋盖": "SY_jacketPockets_yjdzmdjzdg",
        "R款 打褶直角明袋加袋盖": "SY_jacketPockets_dzzjmdjgd",
        "S款 梯型袋盖加打褶明袋": "SY_jacketPockets_txdgjdzmd",
        "T款 圆角风琴袋加袋盖": "SY_jacketPockets_yjfqzjgd",
        "U款 立体明袋加袋盖": "SY_jacketPockets_ltmdjgd",
        "V款 圆角打褶明袋加斜袋盖": "SY_jacketPockets_yjdzmdjxdg",
        "W款 单支线": "SY_jacketPockets_dzx",
        "X款 下三水滴明袋": "SY_jacketPockets_xssdmd",
        "Y款 圆角打褶明袋": "SY_jacketPockets_yjdzmd",
        "Z款 直角打褶明袋": "SY_jacketPockets_zjdzmd",
        "专用袋": "SY_jacketPockets_zyd",
        "前侧缝插袋": "SY_jacketPockets_qcfxd",
        "无": "SY_jacketPockets_wu",
        "月牙双支线": "SY_jacketPockets_yyszx",
        "省道隐形拉链插袋": "SY_jacketPockets_sdyxlld",
    },
    "SY_jacketShoulderPads": {
        "0.2cm": "SY_jacketShoulderPads_0.2",
        "0.5cm": "SY_jacketShoulderPads_0.5",
        "0.7cm": "SY_jacketShoulderPads_0.7",
        "1.5cm": "SY_jacketShoulderPads_1.5",
        "1cm": "SY_jacketShoulderPads_1",
        "2cm": "SY_jacketShoulderPads_2",
        "2cm硬的": "SY_jacketShoulderPads_2yd",
        "无垫肩": "SY_jacketShoulderPads_wdk",
    },
    "SY_jacketSleeveButton": {
        "叠扣": "SY_jacketSleeveButton_dk",
        "平扣": "SY_jacketSleeveButton_pk",
        "斜扣": "SY_jacketSleeveButton_diagonalBuckle",
        "斜眼叠扣": "SY_jacketSleeveButton_slantBuckle",
        "斜眼平扣": "SY_jacketSleeveButton_xpk",
        "袖克夫圆头": "SY_jacketSleeveButton_xfkjt",
        "袖克夫尖头": "SY_jacketSleeveButton_xkf",
        "贴边": "SY_jacketSleeveButton_tb",
    },
    "SY_jacketSleeveType": {
        "AK无袖里自然肩": "SY_jacketSleeveType_akwxlzrj",
        "AK溜肩袖": "SY_jacketSleeveType_ljx",
        "AK翘袖": "SY_jacketSleeveType_akqjsc",
        "KN翘袖": "SY_jacketSleeveType_knqx",
        "TF翘袖": "SY_jacketSleeveType_tfqx",
        "专用袖": "SY_jacketSleeveType_zyx",
        "斜三角袖正常袖": "SY_jacketSleeveType_xsjx",
        "斜三角袖自然肩": "SY_jacketSleeveType_xsjxzrj",
        "斜袖一扣正常袖": "SY_jacketSleeveType_xxyk",
        "斜袖一扣自然肩": "SY_jacketSleeveType_xxykzrj",
        "无袖里自然肩": "SY_jacketSleeveType_wxlzrj",
        "无袖里衬衫肩": "SY_jacketSleeveType_wxlcsj",
        "无袖里袖山分缝": "SY_jacketSleeveType_wxlxsff",
        "正常袖": "SY_jacketSleeveType_normal",
        "瑞典自然袖": "SY_jacketSleeveType_rdzrx",
        "自然肩": "SY_jacketSleeveType_naturalShoulder",
        "自然肩+反上肩": "SY_jacketSleeveType_fsj",
        "衬衫肩": "SY_jacketSleeveType_shirtShoulder",
        "衬衫肩+反上肩": "SY_jacketSleeveType_csjfsj",
        "袖山分缝": "SY_jacketSleeveType_xsff",
    },
    "SY_jacketTowelBag": {
        "1KN333专用明袋": "SY_jacketTowelBag_zymd",
        "AK 打褶明袋加斜袋盖": "SY_jacketTowelBag_akdzmdjxdg",
        "AK专用打褶明袋": "SY_jacketTowelBag_dzmd",
        "AK小明袋": "SY_jacketTowelBag_akxmd",
        "AK弧手巾袋": "SY_jacketTowelBag_aksjd",
        "A款 弧手巾袋": "SY_jacketTowelBag_hxsjd",
        "B款 直手巾袋": "SY_jacketTowelBag_zxsjd",
        "C款 小明袋": "SY_jacketTowelBag_xmd",
        "D款 弧形小明袋": "SY_jacketTowelBag_md",
        "E款 小酒杯明袋": "SY_jacketTowelBag_xjbmd",
        "F款 两个打褶圆角明袋加袋盖": "SY_jacketTowelBag_dzyjmdjdg",
        "G款 两个打褶直角明袋加袋盖": "SY_jacketTowelBag_dzmdjdg",
        "H款 两个圆角打褶明袋加斜袋盖": "SY_jacketTowelBag_lgyjdzmdjxdg",
        "I款 圆角拼接两明袋": "SY_jacketTowelBag_yjpjmd",
        "J款 小水滴明袋": "SY_jacketTowelBag_xsdmd",
        "K款 弧形小明袋加袋盖": "SY_jacketTowelBag_kkhxxmdjdg",
        "L款 双支线袋": "SY_jacketTowelBag_lkszxd",
        "MG口袋": "SY_jacketTowelBag_mgkd",
        "M款": "SY_jacketTowelBag_mk",
        "SK": "SY_jacketTowelBag_sk",
        "SM": "SY_jacketTowelBag_smkd",
        "一个圆角打褶明袋加斜袋盖": "SY_jacketTowelBag_yjdzmd",
        "可抽拉手巾袋": "SY_jacketTowelBag_kclsjd",
        "圆角打褶明袋": "SY_jacketTowelBag_yjdzmdbag",
        "无": "SY_jacketTowelBag_wu",
        "明袋加袋盖": "SY_jacketTowelBag_mdjdg",
        "猎装手巾袋": "SY_jacketTowelBag_lzsjd",
    },
    "SY_jacketVent": {
        "不开叉": "SY_jacketVent_notForked",
        "中开叉": "SY_jacketVent_singleFork",
        "双开叉": "SY_jacketVent_doubleFork",
    },
    "SY_placketKeyhole": {
        "一扣": "SY_placketKeyhole_oneButton ",
        "一扣半": "SY_placketKeyhole_1.5b",
        "三扣": "SY_placketKeyhole_sankou",
        "三扣二": "SY_placketKeyhole_ske",
        "三扣半": "SY_placketKeyhole_skb",
        "两扣半": "SY_placketKeyhole_twoAndAHalfButtons",
        "二扣	": "SY_placketKeyhole_twoBuckles",
        "二扣一": "SY_placketKeyhole_erkouyi",
        "五扣": "SY_placketKeyhole_wlk",
        "八扣三": "SY_placketKeyhole_bks",
        "六扣": "SY_placketKeyhole_mjsy6k",
        "六扣一": "SY_placketKeyhole_sixBucklesAndOne",
        "六扣三": "SY_placketKeyhole_6bno3",
        "六扣二": "SY_placketKeyhole_sixBucklesAndTwo	",
        "四扣": "SY_placketKeyhole_sk",
        "四扣一": "SY_placketKeyhole_fourBucklesAndone",
        "四扣二": "SY_placketKeyhole_fourBucklesAndWwo",
        "四暗扣": "SY_placketKeyhole_sak",
        "对扣": "SY_placketKeyhole_mjsydk",
    },
    "SY_safariSuit": {
        "抽绳款": "SY_safariSuit_pullOutPayment",
        "腰带款": "SY_safariSuit_beltStyle",
    },
    "SY_sleeveElastic": {
        "一层黑炭": "SY_sleeveElastic_ycht",
        "无袖弹": "SY_sleeveElastic_wxt",
        "有袖弹": "SY_sleeveElastic_sleevedBullet",
        "袖弹一层棉": "SY_sleeveElastic_sleevePlaysALayerOfCotton",
    },
    "SY_ydj": {
        "0.2cm": "SY_ydj_0.2",
        "0.5cm": "SY_ydj_0.5",
        "0.7cm": "SY_ydj_0.7cm",
        "1.5cm": "SY_ydj_1.5cm",
        "1cm": "SY_ydj_1cm",
        "2cm": "SY_ydj_2",
        "2cm硬的": "SY_ydj_2y",
        "无垫肩": "SY_ydj_wdj",
    },
    "XK_Slide": {
        "2": "XK_Slide_2",
        "3": "XK_Slide_pqs",
        "4": "XK_Slide_4",
        "5": "XK_Slide_5",
        "6": "XK_Slide_6",
    },
    "XK_curvedHem": {
        "是": "XK_curvedHem_1",
    },
    "XK_footOpeningReversed": {
        "2": "XK_footOpeningReversed_2",
        "3": "XK_footOpeningReversed_3",
        "3.5": "XK_footOpeningReversed_3.5",
        "4": "XK_footOpeningReversed_4",
        "4.5": "XK_footOpeningReversed_4.5",
        "5": "XK_footOpeningReversed_5",
        "6": "XK_footOpeningReversed_6",
    },
    "XK_hemOpening": {
        "反撬": "XK_hemOpening_fq",
        "同工艺书": "XK_hemOpening_ptys",
        "平撬": "XK_hemOpening_pq",
        "斜裤脚": "XK_hemOpening_diagonalHem",
        "松紧拉链": "XK_hemOpening_elasticZipper",
        "裤子毛长": "XK_hemOpening_mc",
    },
    "XK_jkjzd": {
        "无": "XK_jkjzd_wu",
        "本料": "XK_jkjzd_fabric",
        "织带": "XK_jkjzd_you",
        "面料布边织带": "XK_jkjzd_mlbbzd",
    },
    "XK_jkyx": {
        "4": "XK_jkyx_4",
    },
    "XK_pantBackPocket": {
        "单支线": "XK_pantBackPocket_dzx",
        "双支线": "XK_pantBackPocket_szx",
        "双支线加袋盖": "XK_pantBackPocket_dg",
        "双支线口袋，口袋锁眼取消": "XK_pantBackPocket_szxkd",
        "右边单口袋": "XK_pantBackPocket_ybdkd",
        "同工艺书": "XK_pantBackPocket_tgys",
        "后口袋锁眼取消": "XK_pantBackPocket_hdsyqx",
        "后袋取消": "XK_pantBackPocket_hdqx",
        "明袋": "XK_pantBackPocket_md",
        "牛仔袋": "XK_pantBackPocket_nzd",
    },
    "XK_pantFrontFly": {
        "拉链": "XK_pantFrontFly_ll",
        "纽扣": "XK_pantFrontFly_nk",
    },
    "XK_pantsPocket": {
        "无表袋": "XK_pantsPocket_wbd",
        "普通表袋": "XK_pantsPocket_ptbd",
        "表袋袢": "XK_pantsPocket_bdp",
        "袋盖": "XK_pantsPocket_dg",
    },
    "XK_strapBuckle": {
        "无": "XK_strapBuckle_notHave",
        "有": "XK_strapBuckle_have",
    },
    "XK_trouserFrontPockets": {
        "侧缝隐形拉链袋": "XK_trouserFrontPockets_cfyxldd",
        "单支线": "XK_trouserFrontPockets_dzx",
        "双支线袋": "XK_trouserFrontPockets_szxd",
        "弧形斜插袋": "XK_trouserFrontPockets_hxxcd",
        "斜插拉链袋": "XK_trouserFrontPockets_xclld",
        "斜插袋": "XK_trouserFrontPockets_xcd",
        "牛仔袋": "XK_trouserFrontPockets_nzd",
        "直插拉链袋": "XK_trouserFrontPockets_zclld",
        "直插袋": "XK_trouserFrontPockets_straightPocket",
    },
    "XK_waistStyle": {
        "不开叉两侧松紧": "XK_waistStyle_bkc",
        "全松紧": "XK_waistStyle_qsj",
        "后中开叉": "XK_waistStyle_hzkc",
        "后中开叉两侧松紧": "XK_waistStyle_hzkclcsj",
        "松紧": "XK_waistStyle_sj",
        "腰袢": "XK_waistStyle_yp",
        "裤袢": "XK_waistStyle_kp",
        "裤袢+腰袢": "XK_waistStyle_kpjyp",
        "连腰": "XK_waistStyle_lyk",
    },
    "XK_yks": {
        "AB款：腰面宽4CM;加腰带款": "XK_yks_aby",
        "AC款:无宝剑头，腰面宽4.5CM": "XK_yks_ackwbjt",
        "AD款：无宝剑头，腰面宽5CM": "XK_yks_adkwbjt",
        "AE款:宝剑头长14CM，腰面宽4.5CM": "XK_yks_aek",
        "AF款：无宝剑头，腰面宽3.5CM": "XK_yks_afk",
        "AG款：无宝剑头，腰面宽4CM": "XK_yks_agk",
        "AH款:交叉腰，宝剑头长28CM 腰面宽7CM": "XK_yks_ah",
        "AI款：宝剑头长15CM，腰面宽4CM": "XK_yks_aik",
        "AJ款:宝剑头长5CM，腰面宽3.5CM": "XK_yks_ajkyt",
        "A款:腰头长5CM，腰面宽3.5CM": "XK_yks_ak",
        "B款:腰头长12CM，腰面宽5CM": "XK_yks_bkym",
        "C款:无宝剑头，腰面宽3.5CM": "XK_yks_ckym",
        "D款:腰头长22CM，腰面宽3.5CM": "XK_yks_dkym",
        "E款:腰头长26CM，腰面宽5CM": "XK_yks_ekym",
        "F款:交叉腰，腰头长25CM 腰面宽6CM": "XK_yks_fkym",
        "G款:腰头长6CM，腰面宽3.5CM": "XK_yks_gkym",
        "H款:腰头长12CM，腰面款3.5CM": "XK_yks_hkym",
        "I款:腰头长12CM，腰宽3.5CM": "XK_yks_ikym",
        "J款:双宝剑头，腰宽6CM": "XK_yks_jkym",
        "K款:双宝剑头，双扣袢，腰宽6CM": "XK_yks_kkym",
        "L款:腰头长11CM，腰宽5CM": "XK_yks_lkym",
        "M款:腰头长10CM，腰宽3.5CM": "XK_yks_mkym",
        "P款:腰头长26CM，腰宽5CM": "XK_yks_pkym",
        "Q款:腰头长14CM，腰宽4CM": "XK_yks_qkym",
        "S款:腰头长5CM，腰宽4CM": "XK_yks_skym",
        "T款:腰头长16CM，腰宽5CM": "XK_yks_tkym",
        "U款:腰头长25CM，腰宽6CM": "XK_yks_ukym",
        "V款:腰袢，腰头长14CM，腰头处加一个裤袢，腰面宽5CM": "XK_yks_rdy",
        "W款：腰袢，长7公分三角宝剑头，腰宽3.5CM": "XK_yks_rdak",
        "X款：腰袢，长12公分三角宝剑头，腰头处加一个裤袢，腰宽3.5CM": "XK_yks_rdyak",
        "Y款：腰头长12CM，腰面宽5CM": "XK_yks_YK",
        "Z款：腰头长15CM，腰面宽3.5CM": "XK_yks_zk",
        "专用腰": "XK_yks_zyy",
        "两侧松紧腰": "XK_yks_lcsjy",
        "全松紧腰": "XK_yks_wsjy",
        "无腰款": "XK_yks_wyk",
        "活动腰": "XK_yks_hdy",
    },
}

def map_custom_option(field_key, value):
    """根据字段名和输入值，返回映射后的系统值"""
    if field_key in custom_option_mappings:
        mappings = custom_option_mappings[field_key]
        if value in mappings:
            return mappings[value]
        for key in mappings:
            if key.startswith(value + " "):
                return mappings[key]
        for key in mappings:
            if key.startswith(value + ":"):
                return mappings[key]
        for key in mappings:
            if key.startswith(value + "："):
                return mappings[key]
    return value

def load_orders():
    """加载订单数据"""
    if os.path.exists(ORDERS_STORAGE):
        with open(ORDERS_STORAGE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_orders(orders):
    """保存订单数据"""
    with open(ORDERS_STORAGE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def parse_massing_codes(massing_codes):
    """解析量体部位编码，支持字符串和数组格式"""
    if not massing_codes:
        return []
    # 如果已经是列表/数组，直接返回
    if isinstance(massing_codes, list):
        return massing_codes
    # 如果是字符串，按逗号分隔
    if isinstance(massing_codes, str):
        return [code.strip() for code in massing_codes.split(',') if code.strip()]
    return []

def get_token():
    """
    获取登录token（使用SCM API认证方式）
    """
    # 优先使用环境变量中的密钥
    access_key_id = os.environ.get("ACCESS_KEY_ID", API_CONFIG["access_key_id"])
    access_key_secret = os.environ.get("ACCESS_KEY_SECRET", API_CONFIG["access_key_secret"])
    
    # 检查缓存的token
    if API_CONFIG.get("cached_token"):
        return API_CONFIG["cached_token"]
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    data = {
        "accessKeyId": access_key_id,
        "accessKeySecret": access_key_secret
    }
    
    try:
        response = requests.post(API_CONFIG["login_url"], headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 1000:
                token = result.get("data", {}).get("token")
                if token:
                    API_CONFIG["cached_token"] = token
                    return token
        
        print(f"登录失败: {result.get('message', '未知错误')}")
        return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def authenticate():
    """验证API密钥（使用真实API认证）"""
    token = get_token()
    if token:
        return True, "认证成功", token
    return False, "API认证失败", None

def api_add_order(order_data):
    """
    调用订单新增API
    :param order_data: 订单数据字典
    :return: API响应结果
    """
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 打印调试信息
    print(f"=== 订单新增API调用 ===")
    print(f"请求URL: {API_CONFIG['order_add_url']}")
    print(f"请求Headers: {headers}")
    print(f"请求数据(部分):")
    for key, value in order_data.items():
        if isinstance(value, dict):
            print(f"  {key}: {{...}}")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = requests.post(API_CONFIG["order_add_url"], headers=headers, json=order_data, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "订单新增成功", "data": result.get("data")}
            else:
                return {"success": False, "message": f"订单新增失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"订单新增请求失败，状态码: {response.status_code}"}
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return {"success": False, "message": f"订单新增请求异常: {str(e)}"}

def api_add_order_items(order_items):
    """
    调用订单明细新增API
    :param order_items: 订单明细列表
    :return: API响应结果
    """
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["order_items_add_url"], headers=headers, json=order_items, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "订单明细新增成功", "data": result.get("data")}
            else:
                return {"success": False, "message": f"订单明细新增失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"订单明细新增请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"订单明细新增请求异常: {str(e)}"}

def get_pattern_info(pattern_code):
    """根据版型编码获取版型详情（包含默认选项）"""
    token = get_token()
    if not token:
        return {}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 获取版型列表并查找指定版型（使用POST请求）
    try:
        response = requests.post(API_CONFIG["pattern_list_url"], headers=headers, json={}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000 and result.get("data"):
                # 查找匹配的版型
                for pattern in result["data"]:
                    if pattern.get("code") == pattern_code:
                        return pattern
        return {}
    except Exception as e:
        print(f"获取版型详情异常: {str(e)}")
        return {}

def get_pattern_attr_options():
    """获取版型属性选项列表（编码到中文名称的映射）"""
    token = get_token()
    if not token:
        return {}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_attr_list_url"], headers=headers, json={}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000 and result.get("data"):
                # 创建编码到中文名称的映射（API返回的字段是cnName）
                attr_map = {}
                for attr in result["data"]:
                    code = attr.get("code")
                    name = attr.get("cnName")  # 使用cnName字段
                    if code and name:
                        attr_map[code] = name
                print(f"=== 加载了 {len(attr_map)} 个版型属性选项 ===")
                return attr_map
        return {}
    except Exception as e:
        print(f"获取版型属性选项异常: {str(e)}")
        return {}

# 缓存版型属性选项映射
pattern_attr_options_cache = {}
pattern_attr_name_to_code_cache = {}

def get_pattern_attr_options():
    """获取版型属性选项列表（编码到中文名称的映射）"""
    global pattern_attr_name_to_code_cache
    
    token = get_token()
    if not token:
        return {}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_attr_list_url"], headers=headers, json={}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000 and result.get("data"):
                # 创建编码到中文名称的映射
                attr_map = {}
                name_to_code_map = {}
                for attr in result["data"]:
                    code = attr.get("code")
                    name = attr.get("cnName")
                    if code and name:
                        attr_map[code] = name
                        # 建立中文名称到编码的映射（用于反向查找）
                        name_to_code_map[name] = code
                # 更新名称到编码的缓存
                pattern_attr_name_to_code_cache = name_to_code_map
                print(f"=== 加载了 {len(attr_map)} 个版型属性选项 ===")
                return attr_map
        return {}
    except Exception as e:
        print(f"获取版型属性选项异常: {str(e)}")
        return {}

def get_attr_name(code):
    """根据版型属性编码获取中文名称"""
    global pattern_attr_options_cache
    
    # 如果缓存为空，先获取
    if not pattern_attr_options_cache:
        pattern_attr_options_cache = get_pattern_attr_options()
    
    # 返回中文名称，如果找不到则返回原编码
    return pattern_attr_options_cache.get(code, code)

def get_attr_code(name, category=None):
    """根据中文名称获取版型属性编码（支持模糊匹配和分类过滤）"""
    global pattern_attr_name_to_code_cache, pattern_attr_options_cache
    
    # 如果缓存为空，先获取
    if not pattern_attr_options_cache:
        pattern_attr_options_cache = get_pattern_attr_options()
    
    # 精确匹配
    if name in pattern_attr_name_to_code_cache:
        return pattern_attr_name_to_code_cache[name]
    
    # 根据分类进行过滤匹配
    if category:
        for attr_name, code in pattern_attr_name_to_code_cache.items():
            # 检查编码是否匹配指定分类
            if code.startswith(category) and name in attr_name:
                return code
    
    # 模糊匹配（包含匹配）
    for attr_name, code in pattern_attr_name_to_code_cache.items():
        if name in attr_name:
            return code
    
    # 如果都找不到，返回原名称（可能用户已经传递的是编码）
    return name

def parse_text_order(text):
    """解析自然语言描述的订单数据，支持多个订单组（按空行分隔）"""
    import re
    
    # 默认值
    result = {
        "khName": "",
        "khImgurls": "https://example.com/photo.jpg",
        "image_path": "",
        "isManualOrder": False,
        "items": [],
        "orderRemarks": ""
    }
    
    # 提取客户姓名（支持中文、英文、数字）
    name_match = re.search(r'客户姓名[是为：:]([\u4e00-\u9fa5A-Za-z0-9\s]+)', text)
    if not name_match:
        # 尝试英文格式 "Customer's name:"（单行格式）
        name_match = re.search(r"Customer's name:\s*([A-Za-z ]+?)\s+BASE SIZE", text)
    if not name_match:
        # 尝试通用英文格式（带撇号或不带，支持跨行）
        name_match = re.search(r"Customer['’]?\s*name\s*[:：]\s*\n\s*([A-Za-z ]+?)\s*\n", text)
    if not name_match:
        # 尝试简单匹配（逐行查找）
        lines = text.split('\n')
        name_found = False
        for i, line in enumerate(lines):
            if "name:" in line.lower() and "customer" in line.lower():
                if i + 1 < len(lines):
                    name_line = lines[i + 1].strip()
                    if name_line:
                        result["khName"] = name_line
                        name_found = True
                        break
        if not name_found:
            # 尝试匹配带撇号的情况
            import re
            name_match = re.search(r"Customer.*?name.*?\n\s*(.*?)\n", text, re.DOTALL)
    if name_match and not result.get("khName"):
        result["khName"] = name_match.group(1).strip()
    
    # 提取图片路径（支持本地文件路径或URL）
    image_path_match = re.search(r'图片[是为：:]([^，。、\n]+)', text)
    if image_path_match:
        image_path = image_path_match.group(1).strip()
        result["image_path"] = image_path
        if image_path.startswith("http://") or image_path.startswith("https://"):
            result["khImgurls"] = image_path
    
    # 判断是否团单
    if "团单" in text or "团购" in text or "团体" in text:
        result["isGroupOrder"] = True
    
    # 判断是否是英文订单
    is_english_order = "ORDER #" in text or "Customer's name" in text or "Customer’s name" in text
    
    # 尝试按空行分割多个订单组
    # 对于英文订单，不要按空行分割 - 把整个文本作为一个订单组
    if is_english_order:
        order_groups = [text.strip()]
    else:
        # 匹配两个或多个换行符（可能包含空格）
        order_groups = re.split(r'\n\s*\n', text.strip())
    
    # 如果没有明显的分组分隔，检查是否有多个订单组
    if len(order_groups) == 1 and not is_english_order:
        # 首先检查是否有换行符后跟订单号格式（如 "\n FW25049,"）
        # 或者逗号后跟多个空格加订单号格式（如 "，  FW25049,"）
        # 这些格式都表示新的订单组开始
        # 优先匹配换行符格式
        newline_order_matches = list(re.finditer(r'\n\s*([A-Z0-9]+),', text))
        
        # 如果没有换行符格式，检查逗号后跟多个空格加订单号格式
        if len(newline_order_matches) == 0:
            newline_order_matches = list(re.finditer(r'，\s*([A-Z0-9]+),', text))
        
        if len(newline_order_matches) > 0:
            # 按这种格式分割订单组
            order_groups = []
            # 第一个订单组从文本开头到第一个匹配位置
            first_match_start = newline_order_matches[0].start()
            order_groups.append(text[0:first_match_start].strip())
            
            # 后续的订单组
            for i, match in enumerate(newline_order_matches):
                start = match.start()
                if i < len(newline_order_matches) - 1:
                    end = newline_order_matches[i + 1].start()
                    order_groups.append(text[start:end].strip())
                else:
                    order_groups.append(text[start:].strip())
        else:
            # 查找所有团单客户单号的位置
            group_order_matches = list(re.finditer(r'团单客户单号[是为：:]([\w\-]+)', text))
            if len(group_order_matches) > 1:
                # 如果有多个团单客户单号，按它们的位置分割
                order_groups = []
                for i, match in enumerate(group_order_matches):
                    start = match.start()
                    if i < len(group_order_matches) - 1:
                        end = group_order_matches[i + 1].start()
                        order_groups.append(text[start:end].strip())
                    else:
                        order_groups.append(text[start:].strip())
            else:
                # 检查是否有多个面料货号（可能是另一种多订单组格式）
                fabric_matches = list(re.finditer(r'面料货号[是为：:]([\w\-\./]+)', text))
                if len(fabric_matches) > 1:
                    # 按面料货号分割，但需要找到每个面料货号对应的订单组范围
                    order_groups = []
                    for i, match in enumerate(fabric_matches):
                        start = match.start()
                        # 向前查找，找到这个面料货号对应的版型编码位置
                        # 或者向后查找，找到下一个面料货号之前的所有内容
                        if i < len(fabric_matches) - 1:
                            end = fabric_matches[i + 1].start()
                            # 向前查找，找到这个订单组的开始（可能是上一个订单组的结束）
                            if i == 0:
                                # 第一个订单组从文本开头开始
                                order_groups.append(text[0:end].strip())
                            else:
                                order_groups.append(text[start:end].strip())
                        else:
                            if i == 0:
                                order_groups.append(text.strip())
                            else:
                                order_groups.append(text[start:].strip())
    
    all_items = []
    
    for group_index, group_text in enumerate(order_groups):
        if not group_text.strip():
            continue
        
        # 提取当前订单组的团单客户单号（支持中文和英文格式）
        group_order_no_match = re.search(r'团单客户单号[是为：:]([\w\-]+)', group_text)
        if group_order_no_match:
            group_order_no = group_order_no_match.group(1).strip()
        else:
            # 尝试英文格式 "ORDER #xxx"（支持跨行）
            order_no_match = re.search(r'ORDER\s*[#:]\s*([A-Z0-9]+)', group_text)
            if order_no_match:
                group_order_no = order_no_match.group(1).strip()
            else:
                # 如果没有"团单客户单号是"前缀，尝试从开头直接提取订单号（格式如 "，  FW25049,1RZ011"）
                order_no_match = re.match(r'^\s*[，,]\s*([A-Z0-9]+),', group_text.strip())
                if order_no_match:
                    group_order_no = order_no_match.group(1).strip()
                else:
                    # 再尝试直接匹配开头的订单号（不带逗号前缀）
                    order_no_match = re.match(r'^\s*([A-Z0-9]+),', group_text.strip())
                    if order_no_match:
                        group_order_no = order_no_match.group(1).strip()
                    else:
                        group_order_no = ""
        
        # 提取当前订单组的面料货号（支持中文和英文格式）
        fabric_match = re.search(r'面料货号[是为：:]([\w\-\./]+)', group_text)
        if not fabric_match:
            fabric_match = re.search(r'面料[是为：:]([\w\-\./]+)', group_text)
        if not fabric_match:
            # 尝试英文格式 "ARTICLE NUMBER"（支持跨行）
            fabric_match = re.search(r'ARTICLE NUMBER[\s:\n]+([\w\-\./]+)', group_text)
        if not fabric_match:
            # 尝试英文格式 "ARTICLE NO"（支持跨行）
            fabric_match = re.search(r'ARTICLE NO[\s:\n]+([\w\-\./]+)', group_text)
        fabric = fabric_match.group(1).strip() if fabric_match else ""
        
        # 提取面料供应
        fabric_supply_match = re.search(r'面料供应[是为：:]([\u4e00-\u9fa5]+)', group_text)
        fabric_supply = fabric_supply_match.group(1).strip() if fabric_supply_match else "面料客供"
        
        # 提取面料标
        fabric_mark_match = re.search(r'面料标[是为：:]([\w\-\./]+)', group_text)
        fabric_mark = fabric_mark_match.group(1).strip() if fabric_mark_match else ""
        
        # 提取面料产地
        fabric_origin_match = re.search(r'面料产地[是为：:]([\u4e00-\u9fa5]+)', group_text)
        fabric_origin = fabric_origin_match.group(1).strip() if fabric_origin_match else ""
        
        # 提取里布（支持中英文格式）
        lining = ""
        jacket_lining = ""
        trouser_lining = ""
        
        lining_match = re.search(r'里布[是为：:]([\w\-\./]+)', group_text)
        if lining_match:
            lining = lining_match.group(1).strip()
            jacket_lining = lining
            trouser_lining = lining
        else:
            # 尝试英文格式 - 分别提取上衣和西裤的里布
            jacket_lining_match = re.search(r'JACKET LINING[\s:\n]+([^\n]+)', group_text)
            trouser_lining_match = re.search(r'TROUSERS LINING[\s:\n]+([^\n]+)', group_text)
            
            if jacket_lining_match:
                jacket_lining = jacket_lining_match.group(1).strip()
            if trouser_lining_match:
                trouser_lining = trouser_lining_match.group(1).strip()
        
        # 如果没有分别提取到，则使用通用值
        if not jacket_lining and not trouser_lining:
            lining_match = re.search(r'LINING[\s:\n]+([^\n]+)', group_text)
            lining = lining_match.group(1).strip() if lining_match else ""
            jacket_lining = lining
            trouser_lining = lining
        
        # 提取纽扣（支持字母、数字和中文组合，支持中英文格式）
        button_match = re.search(r'纽扣[是为：:]([\w\-]+[\u4e00-\u9fa5]*)', group_text)
        if not button_match:
            # 尝试英文格式 "JACKET BUTTON"
            button_match = re.search(r'JACKET BUTTON[\s:\n]+([\w\-]+)', group_text)
        if not button_match:
            # 尝试英文格式 "TROUSER BUTTON"
            button_match = re.search(r'TROUSER BUTTON[\s:\n]+([\w\-]+)', group_text)
        if not button_match:
            # 尝试英文格式 "BUTTONS"（支持多行文本，只取一行，用前瞻限制）
            button_match = re.search(r'BUTTONS[\s:\n]+([^\n]+?)(?=\s*[A-Z]+\s*$)', group_text)
        if not button_match:
            # 尝试英文格式 "BUTTONS"（简化版本，只取一行）
            button_match = re.search(r'BUTTONS[\s:\n]+([^\n]+)', group_text)
        if not button_match:
            # 尝试通用英文格式 "BUTTON"（但要排除"BUTTON"在其他词里的情况）
            button_match = re.search(r'(?<![A-Z])BUTTON[\s:\n]+([\w\-]+)', group_text)
        button = button_match.group(1).strip() if button_match else ""
        
        # 提取面料成分（支持包含空格的内容，支持中英文格式）
        composition_match = re.search(r'面料成分[是为：:]([\w\-\./%\s]+?)(?=，|。|纽扣|面料标|里布|$)', group_text)
        if not composition_match:
            # 尝试英文格式 "COMPOSITION"（只取一行）
            composition_match = re.search(r'COMPOSITION[\s:\n]+([^\n]+)', group_text)
        composition = composition_match.group(1).strip() if composition_match else ""
        
        # 提取门襟贡针
        placket_needle_match = re.search(r'门襟贡针[是为：:]([\u4e00-\u9fa5]+)', group_text)
        placket_needle = placket_needle_match.group(1).strip() if placket_needle_match else ""
        
        # 提取英文成衣尺寸测量数据（PASSPORT测量）
        # 映射关系：英文字段 -> 系统字段
        english_size_mapping = {
            r'SHOULDERS[\s:\n]+([\d.]+)': 'shoulderWidth',
            r'CHEST[\s:\n]+([\d.]+)': 'fullBust',
            r'UPPER WAIST[\s:\n]+([\d.]+)': 'fullWaistWidth',
            r'HIP[\s:\n]+([\d.]+)': 'fullHipWidth',
            r'BACK LENGTH[\s:\n]+([\d.]+)': 'shortRegularTall',
            r'SLEEVE LENGTH RIGHT[\s:\n]+([\d.]+)': 'sleeveLength',
            r'SLEEVE LENGTH LEFT[\s:\n]+([\d.]+)': 'sleeveLengthLeft',
            r'BICEPS[\s:\n]+([\d.]+)': 'sleeveWidth',
            r'SLEEVE OPENING[\s:\n]+([\d.]+)': 'wrisband',
            r'FRONT LENGTH[\s:\n]+([\d.-]+)': 'frontLength',
            # 西裤尺寸
            r'WAIST[\s:\n]+([\d.]+)': 'fullWaistWidth',
            r'FRONT RISE[\s:\n]+([\d.]+)': 'frontRise',
            r'BACK RISE[\s:\n]+([\d.]+)': 'backRise',
            r'THIGH[\s:\n]+([\d.]+)': 'thigh',
            r'CALF[\s:\n]+([\d.]+)': 'calf',
            r'LEG OPENING[\s:\n]+([\d.]+)': 'legOpening',
            r'INSEAM[\s:\n]+([\d.]+)': 'inseam'
        }
        
        net_size = {}
        for pattern, field_name in english_size_mapping.items():
            match = re.search(pattern, group_text)
            if match:
                try:
                    value = float(match.group(1))
                    net_size[field_name] = value
                except ValueError:
                    pass
        
        # 处理前长的特殊格式 "FRONT LENGTH - 1.0 cm: shorter"
        front_length_match = re.search(r'FRONT LENGTH\s*[-–]\s*([\d.]+)', group_text)
        if front_length_match:
            try:
                value = float(front_length_match.group(1))
                # 如果是负数，表示缩短
                net_size['frontLengthAdjust'] = -value
            except ValueError:
                pass
        
        # 提取当前订单组的版型编码和尺码（支持带R/C后缀的尺码如48R码）
        pattern_matches = re.findall(r'([A-Z0-9]+)的(\d+[RCrc]?码)', group_text)
        pattern_matches += re.findall(r'([A-Z0-9]+)\s+(\d+[RCrc]?码)', group_text)
        
        # 初始化落差变量
        drop = ""
        
        # 如果没有找到中文格式的版型编码，尝试英文格式（支持分行格式）
        if not pattern_matches:
            # 尝试英文格式 "JACKET PATTERN xxx"（支持跨行匹配）
            jacket_pattern_match = re.search(r'JACKET PATTERN[\s:\n]+([A-Z0-9]+)', group_text, re.MULTILINE)
            trouser_pattern_match = re.search(r'TROUSERS PATTERN[\s:\n]+([A-Z0-9]+)', group_text, re.MULTILINE)
            # 尝试通用英文格式 "PATTERN xxx"
            general_pattern_match = re.search(r'PATTERN[\s:\n]+([A-Z0-9]+)', group_text, re.MULTILINE)
            
            # 解析尺码格式 "BASE SIZE 38R (US) / 48 (EU)"（支持跨行匹配）
            size_match = re.search(r'BASE SIZE[\s:\n]+\d+[RCrc\-]?.*?/ (\d+[RCrc\-]?)', group_text, re.DOTALL)
            if not size_match:
                size_match = re.search(r'BASE SIZE[\s:\n]+(\d+[RCrc\-]?)', group_text, re.MULTILINE)
            # 尝试西裤尺码格式 "W42 L34"
            if not size_match:
                size_match = re.search(r'BASE SIZE[\s:\n]+W(\d+)\s+L(\d+)', group_text, re.MULTILINE)
            
            if size_match:
                # 检查是否是西裤尺码格式
                if size_match.groups() and len(size_match.groups()) == 2:
                    final_size = size_match.group(1)  # 使用W后面的数字
                    final_drop = 'R'
                else:
                    size_str = size_match.group(1).strip()
                    # 分离尺码数字和落差（- 是第三种落差，不是R）
                    size_num = re.search(r'(\d+)', size_str)
                    final_size = size_num.group(1) if size_num else ''
                    # 确定落差：R=常规，C=舒适，-=第三种落差
                    if '-' in size_str:
                        final_drop = '-'  # 保留 - 作为第三种落差
                    elif re.search(r'([RCrc])', size_str):
                        final_drop = re.search(r'([RCrc])', size_str).group(1).upper()
                    else:
                        final_drop = 'R'  # 默认常规
                
                # 优先使用特定版型编码
                if jacket_pattern_match:
                    pattern_matches.append((jacket_pattern_match.group(1), final_size + '码'))
                if trouser_pattern_match:
                    pattern_matches.append((trouser_pattern_match.group(1), final_size + '码'))
                if general_pattern_match and not pattern_matches:
                    pattern_matches.append((general_pattern_match.group(1), final_size + '码'))
                # 设置drop，只要有pattern_match就设置
                if final_drop and (jacket_pattern_match or trouser_pattern_match or general_pattern_match):
                    drop = final_drop
        
        # 提取落差（如果还没有从尺码中提取）
        drop_match = None
        if not drop:
            drop_match = re.search(r'落差[是为：:]*([RCrc])', group_text)
            if not drop_match:
                drop_match = re.search(r'落差[是为：:]*([Rr]常规|[Cc]舒适)', group_text)
            if not drop_match:
                drop_match = re.search(r'([Rr]常规|[Cc]舒适)', group_text)
        
        if drop_match:
            match_str = drop_match.group(1).strip().upper()
            if 'R' in match_str or '常规' in match_str:
                drop = 'R'
            elif 'C' in match_str or '舒适' in match_str:
                drop = 'C'
        
        if not drop:
            num_match = re.search(r'落差[是为：:]*(\d+)', group_text)
            if not num_match:
                num_match = re.search(r'落\s*(\d+)', group_text)
            if num_match:
                num_val = int(num_match.group(1))
                drop = 'R' if num_val in (0, 6) else 'C'
        
        # 提取当前订单组的定制选项
        sy_attr = {}
        dy_attr = {}
        xk_attr = {}
        xk_net_size = {}
        placket_needle = ""
        modify_words = r'(?:改成|改为|调整|换|变|改)'
        
        # 工艺
        craft_match = re.search(r'工艺' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if craft_match:
            sy_attr["SY_craft"] = map_custom_option("SY_craft", craft_match.group(1).strip())
        
        # 面大袋（支持中文和字母）
        pocket_match = re.search(r'上衣面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', group_text)
        if not pocket_match:
            pocket_match = re.search(r'面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', group_text)
        if pocket_match:
            sy_attr["SY_jacketPockets"] = map_custom_option("SY_jacketPockets", pocket_match.group(1).strip())
        
        # 袖弹
        elastic_match = re.search(r'袖弹' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if elastic_match:
            sy_attr["SY_sleeveElastic"] = map_custom_option("SY_sleeveElastic", elastic_match.group(1).strip())
        
        # 右垫肩
        right_shoulder_pad_match = re.search(r'右垫肩' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if right_shoulder_pad_match:
            sy_attr["SY_ydj"] = map_custom_option("SY_ydj", right_shoulder_pad_match.group(1).strip())
        
        # 左垫肩
        left_shoulder_pad_match = re.search(r'左垫肩' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if left_shoulder_pad_match:
            sy_attr["SY_jacketShoulderPads"] = map_custom_option("SY_jacketShoulderPads", left_shoulder_pad_match.group(1).strip())
        
        # 驳头锁眼
        lapel_buttonhole_match = re.search(r'驳头锁眼' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if lapel_buttonhole_match:
            sy_attr["SY_jacketButtonhole"] = map_custom_option("SY_jacketButtonhole", lapel_buttonhole_match.group(1).strip())
        
        # 米兰眼颜色
        milan_eye_color_match = re.search(r'米兰眼颜色' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if milan_eye_color_match:
            sy_attr["SY_jacketButtonholeColor"] = map_custom_option("SY_jacketButtonholeColor", milan_eye_color_match.group(1).strip())
        
        # 半里
        half_lining_match = re.search(r'半里' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if half_lining_match:
            sy_attr["SY_halfAMile"] = map_custom_option("SY_halfAMile", half_lining_match.group(1).strip())
        
        # 半里里布风格
        half_lining_style_match = re.search(r'半里里布风格' + modify_words + r'([\u4e00-\u9fa5]+)', group_text)
        if half_lining_style_match:
            sy_attr["SY_halfMileLiningStyle"] = map_custom_option("SY_halfMileLiningStyle", half_lining_style_match.group(1).strip())
        
        # 西裤脚口
        hem_match = re.search(r'西裤脚口' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', group_text)
        if hem_match:
            xk_attr["XK_hemOpening"] = map_custom_option("XK_hemOpening", hem_match.group(1).strip())
        
        # 脚口反撬数值
        hem_value_match = re.search(r'脚口反撬' + modify_words + r'([\d.]+)', group_text)
        if hem_value_match:
            xk_attr["XK_footOpeningReversed"] = map_custom_option("XK_footOpeningReversed", hem_value_match.group(1).strip())
        
        # 腰款式
        waist_style_match = re.search(r'腰款式' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', group_text)
        if waist_style_match:
            xk_attr["XK_yks"] = map_custom_option("XK_yks", waist_style_match.group(1).strip())
        
        # 裤腰样式
        waist_strap_match = re.search(r'裤腰样式' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', group_text)
        if waist_strap_match:
            xk_attr["XK_waistStyle"] = map_custom_option("XK_waistStyle", waist_strap_match.group(1).strip())
        
        # 构建订单明细
        for pattern_code, size in pattern_matches:
            # 分离尺码和落差（如48R码 -> 尺码48，落差R）
            size_value = size.replace("码", "")
            drop_value = drop
            # 如果尺码末尾是R或C，分离出来作为落差
            if size_value and size_value[-1] in ('R', 'C', 'r', 'c'):
                drop_value = size_value[-1].upper()
                size_value = size_value[:-1]
            
            # 根据版型类型选择正确的里布值
            item_lining = lining
            if pattern_code.startswith("1") and jacket_lining:
                item_lining = jacket_lining
            elif pattern_code.startswith("6") and trouser_lining:
                item_lining = trouser_lining
            
            item = {
                "patternCode": pattern_code,
                "fabric": fabric,
                "size": size_value,
                "drop": drop_value,  # 使用解析到的落差值，为空时系统会从规格单获取默认值
                "itemKsOrderNo": group_order_no,  # 使用当前订单组的团单客户单号
                "itemKhName": result.get("khName", ""),  # 添加团单客户名称到明细
                "fabricSupply": fabric_supply,  # 面料供应
                "fabricMark": fabric_mark,      # 面料标
                "fabricOrigin": fabric_origin,  # 面料产地
                "lining": item_lining,          # 里布
                "button": button,              # 纽扣
                "composition": composition     # 面料成分
            }
            
            # 添加英文成衣尺寸测量数据（PASSPORT测量数据，放到ksMadeSize字段）
            if net_size:
                item["ksMadeSize"] = net_size
            
            # 添加贡针（如果有）
            if placket_needle:
                item["placketNeedle"] = placket_needle
            
            # 判断版型类型
            # 上衣版型（以1开头，除了1SF是猎装）
            if pattern_code.startswith("1") and not pattern_code.startswith("1SF"):
                item["patternTypeCode"] = "SY"
                # 使用特殊标记告知create_order需要合并默认属性和用户修改
                if sy_attr:
                    item["customPatternAttr"] = sy_attr
            elif pattern_code.startswith("2K") or pattern_code.startswith("3K"):
                item["patternTypeCode"] = "SY"
                if sy_attr:
                    item["customPatternAttr"] = sy_attr
            elif pattern_code.startswith("4"):
                item["patternTypeCode"] = "DY"
                if dy_attr:
                    item["customPatternAttr"] = dy_attr
            elif pattern_code.startswith("5"):
                item["patternTypeCode"] = "MJ"
                if sy_attr:
                    item["customPatternAttr"] = sy_attr
            elif pattern_code.startswith("6") or pattern_code.startswith("7"):
                item["patternTypeCode"] = "XK"
                if xk_attr:
                    item["customPatternAttr"] = xk_attr
                if xk_net_size:
                    item["netSize"] = xk_net_size
            elif pattern_code.startswith("1SF") or pattern_code.startswith("8") or pattern_code.startswith("9"):
                item["patternTypeCode"] = "LZ"
                if sy_attr:
                    item["customPatternAttr"] = sy_attr
            elif pattern_code.startswith("0"):
                item["patternTypeCode"] = "MJ"
                if sy_attr:
                    item["customPatternAttr"] = sy_attr
            
            result["items"].append(item)
    
    # 生成备注 - 只有明确的备注内容才添加到这里
    remarks = []
    
    # 只有"手工套结"需要添加到备注，定制选项已经通过ksPatternAttr处理
    if "手工套结" in text:
        remarks.append("手工套结")
    
    if remarks:
        result["orderRemarks"] = "，".join(remarks)
    
    # 判断是否团单
    if "团单" in text or "团购" in text or "团体" in text:
        result["isGroupOrder"] = True
    
    # 提取团单客户单号（支持中文和英文格式）
    group_order_no_match = re.search(r'团单客户单号[是为：:]([\w\-]+)', text)
    if group_order_no_match:
        order_no = group_order_no_match.group(1).strip()
        result["ksOrderNo"] = order_no           # 订单级别客商单号
        result["itemKsOrderNo"] = order_no       # 明细级别客商单号
    else:
        # 尝试英文格式 "ORDER #xxx"
        order_no_match = re.search(r'ORDER\s*[#:]\s*([A-Z0-9]+)', text)
        if order_no_match:
            order_no = order_no_match.group(1).strip()
            result["ksOrderNo"] = order_no       # 订单级别客商单号
            result["itemKsOrderNo"] = order_no   # 明细级别客商单号
    
    return {
        "success": True,
        "data": result
    }

def get_standard_size_from_specs(specs_code, size, drop):
    """
    根据规格单编码、尺码和落差获取标准尺码
    """
    # 获取规格单详情
    specs_result = api_get_specs_info_by_code(specs_code)
    if not specs_result["success"] or not specs_result.get("data"):
        return {}
    
    specs_data = specs_result["data"]
    size_table = specs_data.get("sizeTable", [])
    
    # 根据尺码和落差筛选尺寸数据
    standard_size = {}
    for item in size_table:
        if item.get("size") == size and item.get("drop") == drop:
            massing_code = item.get("massingCode")
            value = item.get("value")
            
            # 转换massingCode到对应的字段名
            field_mapping = {
                "fullBust": "fullBust",
                "fullWaistWidth": "fullWaistWidth",
                "fullHipWidth": "fullHipWidth",
                "lowerHem": "lowerHem",
                "shoulderWidth": "shoulderWidth",
                "sleeveLength": "sleeveLength",
                "frontLength": "frontLength",
                "shortRegularTall": "shortRegularTall",
                "wrisband": "wrisband",
                "sleeveWidth": "sleeveWidth",
                "backWidth": "backWidth"
            }
            
            field_name = field_mapping.get(massing_code)
            if field_name:
                # 转换值类型（数字字段）
                try:
                    if isinstance(value, str):
                        if '.' in value:
                            standard_size[field_name] = float(value)
                        else:
                            standard_size[field_name] = int(value)
                    else:
                        standard_size[field_name] = value
                except ValueError:
                    standard_size[field_name] = value
    
    return standard_size

def create_order_items(order_id, items_list):
    """为订单添加多个明细"""
    for item_data in items_list:
        item_data["orderId"] = order_id
        items_result = api_add_order_items(item_data)
        if not items_result["success"]:
            return {"success": False, "message": f"添加明细失败: {items_result.get('message')}"}
    return {"success": True, "message": "所有明细添加成功"}

def build_order_item(params, pattern_info):
    """构建单个订单明细数据"""
    # 设置默认值 - 包含所有必填字段，确保类型正确
    params["patternTypeCode"] = str(params.get("patternTypeCode", "SY"))
    params["patternCode"] = str(params.get("patternCode", ""))
    params["fabric"] = str(params.get("fabric", ""))
    params["fabricSupply"] = str(params.get("fabricSupply", "面料客供"))
    params["fabricMark"] = str(params.get("fabricMark", ""))
    params["lining"] = str(params.get("lining", ""))
    params["composition"] = str(params.get("composition", ""))
    params["fabricOrigin"] = str(params.get("fabricOrigin", ""))
    params["placketNeedle"] = str(params.get("placketNeedle", ""))
    params["button"] = str(params.get("button", ""))
    params["isSample"] = bool(params.get("isSample", False))
    params["ksRemark"] = str(params.get("ksRemark", ""))
    params["size"] = str(params.get("size", ""))
    # 落差确保为字符串类型，支持数字0
    drop_val = params.get("drop", "")
    params["drop"] = str(drop_val) if drop_val is not None else ""
    params["isEmbroider"] = bool(params.get("isEmbroider", False))
    params["embroiderText"] = str(params.get("embroiderText", ""))
    params["embroiderTypeface"] = str(params.get("embroiderTypeface", ""))
    params["embroiderColor"] = str(params.get("embroiderColor", ""))
    params["embroiderPic"] = str(params.get("embroiderPic", ""))
    params["ksSpecialBodyRemark"] = str(params.get("ksSpecialBodyRemark", ""))
    
    # 处理单个版型属性参数，组合成ksPatternAttr字段
    pattern_attr_mapping = {
        "syJag": "SY_jag",
        "syYdj": "SY_ydj",
        "syCraft": "SY_craft",
        "syJacketVent": "SY_jacketVent",
        "syCuffKeyhole": "SY_cuffKeyhole",
        "syJacketPockets": "SY_jacketPockets",
        "sySleeveElastic": "SY_sleeveElastic",
        "syJacketTowelBag": "SY_jacketTowelBag",
        "syPlacketKeyhole": "SY_placketKeyhole",
        "syJacketButtonhole": "SY_jacketButtonhole",
        "syJacketSleeveType": "SY_jacketSleeveType",
        "syJacketChestLining": "SY_jacketChestLining",
        "syJacketShoulderPads": "SY_jacketShoulderPads",
        "syJacketSleeveButton": "SY_jacketSleeveButton",
        "syHalfMileLiningStyle": "SY_halfMileLiningStyle",
        "syJacketButtonholeColor": "SY_jacketButtonholeColor",
        "syHalfLining": "SY_halfLining",
        "xkYks": "XK_yks",
        "xkSlide": "XK_Slide",
        "xkJkjzd": "XK_jkjzd",
        "xkHemOpening": "XK_hemOpening",
        "xkPantsPocket": "XK_pantsPocket",
        "xkStrapBuckle": "XK_waistStyle",
        "xkPantFrontFly": "XK_pantFrontFly",
        "xkPantBackPocket": "XK_pantBackPocket",
        "xkPantsWaistStyle": "XK_pantsWaistStyle",
        "xkTrouserFrontPockets": "XK_trouserFrontPockets"
    }
    if "ksPatternAttr" not in params:
        params["ksPatternAttr"] = {}
    for arg_name, field_name in pattern_attr_mapping.items():
        if arg_name in params and params[arg_name]:
            params["ksPatternAttr"][field_name] = params[arg_name]
    
    # 处理单个版型结构参数，组合成ksPatternStructure字段
    pattern_structure_mapping = {
        "lapelType": "lapelType",
        "lapelWidth": "lapelWidth",
        "buttonNumber": "buttonNumber",
        "liningConstructions": "liningConstructions",
        "ph": "ph",
        "xb": "xb",
        "xzks": "xzks",
        "pleat": "pleat"
    }
    if "ksPatternStructure" not in params:
        params["ksPatternStructure"] = {}
    for arg_name, field_name in pattern_structure_mapping.items():
        if arg_name in params and params[arg_name]:
            params["ksPatternStructure"][field_name] = params[arg_name]
    
    # 构建订单明细数据 - 包含所有必填字段
    order_items_data = {
        "patternTypeCode": params["patternTypeCode"],
        "patternCode": params["patternCode"],
        "fabricSupply": params["fabricSupply"],
        "fabricMark": params["fabricMark"],
        "lining": params["lining"],
        "fabric": params["fabric"],
        "composition": params["composition"],
        "fabricOrigin": params["fabricOrigin"],
        "placketNeedle": params["placketNeedle"],
        "button": params["button"],
        "isSample": params["isSample"],
        "ksRemark": params["ksRemark"],
        "patternImgurl": params.get("patternImgurl", pattern_info.get("imgurl", "")),
        "ksMassingCodes": parse_massing_codes(params.get("ksMassingCodes", [])),
        "specsCode": params.get("specsCode", ""),
        "size": params["size"],
        "drop": params["drop"],
        "isEmbroider": params["isEmbroider"],
        "embroiderText": params["embroiderText"],
        "embroiderTypeface": params["embroiderTypeface"],
        "embroiderColor": params["embroiderColor"],
        "embroiderPic": params["embroiderPic"],
        "ksOrderSize": None
    }
    
    # 只有当 isSample 为 True 时才添加试样相关字段
    if params["isSample"]:
        order_items_data["halfDeliveryDate"] = params.get("halfDeliveryDate", "")
        order_items_data["sampleFabric"] = params.get("sampleFabric", "")
    
    # 从规格单获取量体字段
    specs_data = None
    if params.get("specsCode"):
        specs_result = api_get_specs_info_by_code(params["specsCode"])
        if specs_result["success"] and specs_result.get("data"):
            specs_data = specs_result["data"]
            specs_massing_codes = specs_data.get("massingCodes", [])
            # 设置 ksMassingCodes，这个字段是系统需要的
            if "ksMassingCodes" in params and params["ksMassingCodes"]:
                order_items_data["ksMassingCodes"] = parse_massing_codes(params["ksMassingCodes"])
            else:
                order_items_data["ksMassingCodes"] = specs_massing_codes
            # massingCodes 可以不设置，让系统自动处理
    
    # 添加版型属性 - 合并默认属性和用户修改的选项
    custom_attr = params.get("customPatternAttr", {})
    default_attr = pattern_info.get("patternAttr", {})
    
    # 合并：默认属性作为基础，用户修改的选项覆盖默认值
    merged_attr = {}
    if default_attr:
        merged_attr.update(default_attr)
    if custom_attr:
        merged_attr.update(custom_attr)
    
    # 处理条件性字段 - 根据版型类型分别处理
    pattern_type_code = params.get("patternTypeCode", "")
    
    if pattern_type_code == "SY":
        # 上衣处理
        # 1. 米兰眼颜色 - 只有当驳头锁眼是手工米兰眼等选项时才保留，否则删除
        lapel_buttonhole = merged_attr.get("SY_jacketButtonhole", "")
        if lapel_buttonhole not in ["SY_jacketButtonhole_sgmly", "SY_jacketButtonhole_sbmly", "SY_jacketButtonhole_qxytsy"]:
            if "SY_jacketButtonholeColor" in merged_attr:
                del merged_attr["SY_jacketButtonholeColor"]
        # 2. 艾伦眼颜色 - 只有当驳头锁眼是艾伦眼等选项时才保留，否则删除
        if lapel_buttonhole not in ["SY_jacketButtonhole_aly"]:
            if "SY_curvedHandmadeColor" in merged_attr:
                del merged_attr["SY_curvedHandmadeColor"]
        # 确保不出现西裤字段
        if "XK_footOpeningReversed" in merged_attr:
            del merged_attr["XK_footOpeningReversed"]
        if "XK_Slide" in merged_attr:
            del merged_attr["XK_Slide"]
    elif pattern_type_code == "XK":
        # 西裤处理
        # 1. 脚口反撬值 - 只有当脚口是反撬时才保留，否则删除
        hem_opening = merged_attr.get("XK_hemOpening", "")
        if hem_opening != "XK_hemOpening_fq":
            if "XK_footOpeningReversed" in merged_attr:
                del merged_attr["XK_footOpeningReversed"]
        # 2. 脚口平撬值 - 只有当脚口是平撬时才保留，否则删除
        if hem_opening != "XK_hemOpening_pq":
            if "XK_Slide" in merged_attr:
                del merged_attr["XK_Slide"]
        # 确保不出现上衣字段
        if "SY_jacketButtonholeColor" in merged_attr:
            del merged_attr["SY_jacketButtonholeColor"]
        if "SY_curvedHandmadeColor" in merged_attr:
            del merged_attr["SY_curvedHandmadeColor"]
    
    if merged_attr:
        order_items_data["ksPatternAttr"] = merged_attr
    
    # 添加版型结构 - 只使用版型实际有的结构
    if "ksPatternStructure" in params and params["ksPatternStructure"]:
        order_items_data["ksPatternStructure"] = params["ksPatternStructure"]
    else:
        default_structure = pattern_info.get("patternStructure", {})
        if default_structure:
            order_items_data["ksPatternStructure"] = default_structure
    
    # 添加成衣尺寸 - 客户提供的PASSPORT测量数据放到这里
    if "ksMadeSize" in params and params["ksMadeSize"]:
        order_items_data["ksMadeSize"] = params["ksMadeSize"]
    
    # 添加套码尺寸 - 从规格单的 sizeTable 获取真实数据
    if "standardSize" in params and params["standardSize"]:
        order_items_data["standardSize"] = params["standardSize"]
    else:
        if specs_data:
            size_table = specs_data.get("sizeTable", [])
            target_size = params.get("size", "")
            target_drop = params.get("drop", "")
            size_dict = {}
            for item in size_table:
                if item.get("size") == target_size and item.get("drop") == target_drop:
                    code = item.get("massingCode")
                    value = item.get("value")
                    if code and value is not None:
                        try:
                            if "." in str(value):
                                size_dict[code] = float(value)
                            else:
                                size_dict[code] = int(value)
                        except:
                            size_dict[code] = value
            if size_dict:
                order_items_data["standardSize"] = size_dict
    
    # 添加净尺寸 - 确保数值类型正确
    if "netSize" in params and params["netSize"]:
        # 确保净尺寸值为数值类型
        net_size = params["netSize"]
        for key, value in net_size.items():
            if value is not None and value != "":
                try:
                    if "." in str(value):
                        net_size[key] = float(value)
                    else:
                        net_size[key] = int(value)
                except:
                    pass
        order_items_data["netSize"] = net_size
    else:
        order_items_data["netSize"] = {
            "fullBust": params.get("fullBust", ""),
            "fullHipWidth": params.get("fullHipWidth", "")
        }
    
    # 添加客商特体尺码
    if "ksSpecialSize" in params and params["ksSpecialSize"]:
        order_items_data["ksSpecialSize"] = params["ksSpecialSize"]
    else:
        order_items_data["ksSpecialSize"] = {
            "syFlatShoulder": params.get("syFlatShoulder", 0)
        }
    
    # 添加特体备注
    order_items_data["ksSpecialBodyRemark"] = params["ksSpecialBodyRemark"]
    
    # 添加团单客商单号
    order_items_data["itemKsOrderNo"] = params.get("itemKsOrderNo", "")
    
    # 添加团单客户名称到明细
    order_items_data["itemKhName"] = params.get("itemKhName", "")
    
    return order_items_data

def create_order(params):
    """创建新订单（支持完整的订单字段和明细字段）"""
    # 如果提供了自然语言文本，先解析它
    if "text" in params and params["text"]:
        parse_result = parse_text_order(params["text"])
        if parse_result["success"]:
            # 将解析结果合并到params中
            params.update(parse_result["data"])
            items_list = parse_result["data"].get("items", [])
        else:
            return parse_result
    else:
        # 支持多个明细的情况
        items_list = params.get("items", [])
    
    # 自动上传图片（如果提供了本地图片路径）
    image_path = params.get("image_path", "")
    if image_path and not image_path.startswith("http://") and not image_path.startswith("https://"):
        upload_result = api_upload_image(image_path)
        if upload_result["success"]:
            params["khImgurls"] = upload_result["data"]["url"]
            print(f"图片上传成功: {params['khImgurls']}")
        else:
            print(f"图片上传失败: {upload_result['message']}")
            # 图片上传失败不影响订单创建，使用默认图片
            if not params.get("khImgurls"):
                params["khImgurls"] = "https://example.com/photo.jpg"
    
    # 订单必填字段验证
    order_required_fields = [
        ("khName", "客户姓名"),
        ("khImgurls", "客户照片"),
        ("isManualOrder", "是否手工单")
    ]
    
    # 订单明细必填字段验证
    order_items_required_fields = [
        ("patternTypeCode", "款式类型编码"),
        ("patternCode", "版型编码"),
        ("fabricSupply", "面料供应"),
        ("fabricMark", "面料标/面料品牌"),
        ("lining", "里布"),
        ("fabric", "面料编号"),
        ("composition", "面料成分"),
        ("fabricOrigin", "面料产地"),
        ("placketNeedle", "门襟贡针"),
        ("button", "纽扣"),
        ("isSample", "是否试样"),
        ("ksRemark", "客商备注"),
        ("patternImgurl", "版型图片"),
        ("ksMassingCodes", "客商_量体部位"),
        ("specsCode", "规格单编码"),
        ("size", "尺码"),
        ("drop", "落差"),
        ("isEmbroider", "是否绣花"),
        ("embroiderText", "绣花文字"),
        ("embroiderTypeface", "绣花字体"),
        ("embroiderColor", "绣花颜色"),
        ("embroiderPic", "绣花图案")
    ]
    
    # 设置默认值（在验证之前设置）
    # 体型默认正常体
    params["khShapeCode"] = params.get("khShapeCode", "正常体")
    # 手机号默认1
    params["khMtel"] = str(params.get("khMtel", "1"))
    # 地址默认1
    params["khAddress"] = str(params.get("khAddress", "1"))
    # 交货日期默认下单当日15天之后
    if not params.get("deliveryDate"):
        default_delivery_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        params["deliveryDate"] = default_delivery_date
    params["deliveryDate"] = str(params.get("deliveryDate", ""))
    # 面料供应默认面料客供
    params["fabricSupply"] = str(params.get("fabricSupply", "面料客供"))
    # 以下字段默认值为空，确保类型正确
    params["lining"] = str(params.get("lining", ""))                  # 里布
    params["tradeMarkName"] = str(params.get("tradeMarkName", ""))    # 商标名
    params["ksOrderNo"] = str(params.get("ksOrderNo", ""))            # 客商单号
    params["fabricMark"] = str(params.get("fabricMark", ""))          # 面料标
    params["fabricOrigin"] = str(params.get("fabricOrigin", ""))      # 面料产地
    params["button"] = str(params.get("button", ""))                  # 纽扣
    params["composition"] = str(params.get("composition", ""))        # 面料成分
    params["placketNeedle"] = str(params.get("placketNeedle", ""))    # 门襟贡针
    params["isSample"] = bool(params.get("isSample", False))           # 是否试样（布尔值，默认否）
    params["orderRemarks"] = str(params.get("orderRemarks", ""))      # 订单备注
    
    # 提前获取版型信息（用于版型图片等默认值）
    pattern_info = {}
    if params.get("patternCode"):
        pattern_info = get_pattern_info(params["patternCode"])
    
    # 版型图片从版型API获取（字段名是imgurl）
    if not params.get("patternImgurl") and pattern_info:
        params["patternImgurl"] = pattern_info.get("imgurl", "")
    
    # 如果没有提供落差，从规格单获取第一个可用的落差作为默认值
    if (params.get("drop") is None or params.get("drop") == "") and params.get("specsCode"):
        specs_result = api_get_specs_info_by_code(params["specsCode"])
        if specs_result["success"] and specs_result.get("data"):
            size_table = specs_result["data"].get("sizeTable", [])
            # 获取所有不重复的落差值
            drops = list(set(item.get("drop") for item in size_table if item.get("drop")))
            if drops:
                params["drop"] = drops[0]  # 默认选第一个落差
    
    missing_fields = []
    
    # 验证订单字段
    for field, desc in order_required_fields:
        if field == "isManualOrder":
            if field not in params:
                missing_fields.append(desc)
        else:
            if field not in params or params.get(field) is None:
                missing_fields.append(desc)
    
    # 如果没有提供多个明细，则验证订单明细字段
    if not items_list:
        for field, desc in order_items_required_fields:
            if field in ["isSample", "isEmbroider"]:
                if field not in params:
                    missing_fields.append(desc)
            else:
                if field not in params or params.get(field) is None:
                    missing_fields.append(desc)
    
    if missing_fields:
        return {"success": False, "message": f"缺少必填字段: {', '.join(missing_fields)}"}
    
    # 构建订单数据
    order_data = {
        "ksOrderNo": params["ksOrderNo"],
        "tradeMarkName": params["tradeMarkName"],
        "khName": params["khName"],
        "khMtel": params["khMtel"],
        "khAddress": params["khAddress"],
        "khShapeCode": params["khShapeCode"],
        "khImgurls": params["khImgurls"],
        "deliveryDate": params["deliveryDate"],
        "orderRemarks": params["orderRemarks"],
        "isManualOrder": params["isManualOrder"],
        "manualOrderhImgurls": params.get("manualOrderhImgurls", ""),
        "isGroupOrder": params.get("isGroupOrder", False)
    }
    
    # 如果没有提供多个明细，则使用当前参数作为单个明细
    if not items_list:
        # 如果是团单且明细没有提供itemKsOrderNo，使用解析到的团单客户单号或订单号
        if params.get("isGroupOrder") and not params.get("itemKsOrderNo"):
            params["itemKsOrderNo"] = params.get("itemKsOrderNo", params.get("ksOrderNo", ""))
        order_items_data = build_order_item(params, pattern_info)
    
    # 尝试调用API创建订单
    api_result = api_add_order(order_data)
    
    if api_result["success"]:
        order_id = api_result["data"].get("id", api_result["data"].get("orderId", ""))
        
        if order_id:
            # 调用订单明细新增API
            # 如果有多个明细，使用批量添加
            if items_list:
                # 处理每个明细
                all_items_data = []
                for item_params in items_list:
                    # 获取版型信息
                    pattern_info = {}
                    if item_params.get("patternCode"):
                        pattern_info = get_pattern_info(item_params["patternCode"])
                    
                    # 如果用户没有提供规格单编码，从版型信息获取
                    if not item_params.get("specsCode") and pattern_info.get("specsCode"):
                        item_params["specsCode"] = pattern_info["specsCode"]
                    
                    # 如果明细没有提供落差，从规格单获取第一个可用的落差作为默认值
                    if (item_params.get("drop") is None or item_params.get("drop") == "") and item_params.get("specsCode"):
                        specs_result = api_get_specs_info_by_code(item_params["specsCode"])
                        if specs_result["success"] and specs_result.get("data"):
                            size_table = specs_result["data"].get("sizeTable", [])
                            # 按规格单中的顺序获取落差值（不使用set保持顺序）
                            drops = []
                            seen_drops = set()
                            for item in size_table:
                                drop = item.get("drop")
                                if drop and item.get("size") == item_params.get("size") and drop not in seen_drops:
                                    drops.append(drop)
                                    seen_drops.add(drop)
                            if drops:
                                item_params["drop"] = drops[0]  # 默认选第一个落差
                    
                    # 如果是团单且明细没有提供itemKsOrderNo，使用解析到的团单客户单号
                    if params.get("isGroupOrder") and not item_params.get("itemKsOrderNo"):
                        item_params["itemKsOrderNo"] = params.get("itemKsOrderNo", params.get("ksOrderNo", ""))
                    
                    item_data = build_order_item(item_params, pattern_info)
                    all_items_data.append(item_data)
                
                # 添加所有明细
                items_result = create_order_items(order_id, all_items_data)
            else:
                # 添加订单ID到明细数据
                order_items_data["orderId"] = order_id
                # 添加单个明细
                items_result = api_add_order_items(order_items_data)
            
            if items_result["success"]:
                # 查询订单详情获取生产单号
                order_info = api_query_order_info(order_id)
                prod_no = order_info.get("data", {}).get("prodNo", order_id)
                
                return {
                    "success": True,
                    "message": "订单和明细创建成功",
                    "data": {
                        "生产单号": prod_no,
                        "order": order_data,
                        "order_items": all_items_data if items_list else order_items_data
                    }
                }
            else:
                return items_result
        
        return {
            "success": True,
            "message": "订单创建成功（明细未创建）",
            "data": {
                "order_id": order_id,
                **order_data
            }
        }
    else:
        # API调用失败，使用本地存储作为降级方案
        print(f"API调用失败，使用本地存储: {api_result['message']}")
        
        order_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        order = {
            "order_id": order_id,
            **order_data,
            "order_items": order_items_data,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
            "api_error": api_result["message"]
        }
        
        orders = load_orders()
        orders[order_id] = order
        save_orders(orders)
        
        return {
            "success": True,
            "message": "订单创建成功（使用本地存储）",
            "data": order
        }

def api_query_order_info(order_id):
    """
    调用订单详情API（使用POST方法）
    :param order_id: 订单ID
    :return: API响应结果
    """
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    request_data = {"id": order_id}
    
    try:
        response = requests.post(API_CONFIG["order_info_url"], headers=headers, json=request_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                data = result.get("data", {})
                # 验证是否返回了真实数据
                if str(data.get("id")) == str(order_id):
                    # 单独调用订单明细列表API获取明细
                    items_result = api_query_order_items(order_id)
                    if items_result["success"]:
                        order_items = items_result.get("data", [])
                        # 为每个订单明细补充规格单信息
                        for item in order_items:
                            specs_code = item.get("specsCode")
                            if specs_code:
                                specs_result = api_get_specs_info_by_code(specs_code)
                                if specs_result["success"] and specs_result.get("data"):
                                    specs_data = specs_result["data"]
                                    # 添加规格单信息到明细
                                    item["specsInfo"] = specs_data
                                    # 添加 tableColumns（量体项目列表）
                                    item["tableColumns"] = specs_data.get("massingCodes", [])
                    else:
                        order_items = []
                    
                    # 将明细添加到订单数据中
                    data["orderItems"] = order_items
                    return {"success": True, "message": "订单详情查询成功", "data": data}
                else:
                    return {"success": False, "message": "订单详情查询失败: 返回的是测试数据"}
            else:
                return {"success": False, "message": f"订单详情查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"订单详情查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"订单详情查询请求异常: {str(e)}"}

def api_query_order_page(page=1, size=10, khName=None, orderNo=None):
    """
    调用订单分页API（使用POST方法）
    :param page: 页码
    :param size: 每页数量
    :param khName: 客户姓名（可选）
    :param orderNo: 订单号（可选）
    :return: API响应结果
    """
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    request_data = {
        "page": page,
        "size": size
    }
    
    if khName:
        request_data["khName"] = khName
    if orderNo:
        request_data["orderNo"] = orderNo
    
    try:
        response = requests.post(API_CONFIG["order_page_url"], headers=headers, json=request_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "订单分页查询成功", "data": result.get("data")}
            else:
                return {"success": False, "message": f"订单分页查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"订单分页查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"订单分页查询请求异常: {str(e)}"}

def api_query_order_items(order_id):
    """
    调用订单明细列表API（使用POST方法）
    :param order_id: 订单ID
    :return: API响应结果
    """
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    request_data = {"orderId": order_id}
    
    try:
        response = requests.post(API_CONFIG["order_items_list_url"], headers=headers, json=request_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                order_items = result.get("data", [])
                
                # 获取量体信息列表并创建映射
                massing_map = {}
                massing_result = api_get_massing_list()
                if massing_result["success"]:
                    massing_list = massing_result.get("data", [])
                    massing_map = {item["code"]: item for item in massing_list}
                
                # 为每个订单明细补充规格单信息和tableColumns
                for item in order_items:
                    specs_code = item.get("specsCode")
                    if specs_code:
                        specs_result = api_get_specs_info_by_code(specs_code)
                        if specs_result["success"] and specs_result.get("data"):
                            specs_data = specs_result["data"].copy()
                            
                            # 添加规格单信息到明细
                            item["specsInfo"] = specs_data
                            
                            # 添加 tableColumns（量体项目列表）
                            massing_codes = specs_data.get("massingCodes", [])
                            item["tableColumns"] = massing_codes
                            
                            # 修复规格单中可能的拼写错误
                            corrected_massing_codes = []
                            for code in massing_codes:
                                # 修复常见拼写错误
                                corrected_code = code
                                if code == "shouldeWidth":
                                    corrected_code = "shoulderWidth"
                                elif code == "backwidth":
                                    corrected_code = "backWidth"
                                corrected_massing_codes.append(corrected_code)
                            
                            # 添加详细的量体项目信息（包含中文名称）
                            massing_info = []
                            for code in corrected_massing_codes:
                                if code in massing_map:
                                    massing_info.append(massing_map[code])
                                else:
                                    # 如果找不到，使用编码作为中文名称
                                    massing_info.append({
                                        "code": code,
                                        "cnName": code,
                                        "enName": code,
                                        "rusName": code
                                    })
                            item["massingList"] = massing_info
                            
                            # 在规格单信息中也添加量体项目的中文名称映射
                            specs_data["massingCodeNames"] = {code: massing_map.get(code, {}).get("cnName", code) 
                                                             for code in corrected_massing_codes}
                            
                            # 如果明细没有 massingCodes，从规格单补充
                            if not item.get("massingCodes"):
                                item["massingCodes"] = corrected_massing_codes
                            
                            # 如果明细没有 massingRuleSize，从规格单的 sizeTable 中提取
                            if not item.get("massingRuleSize"):
                                size_table = specs_data.get("sizeTable", [])
                                size = item.get("size", "")
                                drop = item.get("drop", "")
                                massing_rule_size = {}
                                for size_item in size_table:
                                    if size_item.get("size") == size and size_item.get("drop") == drop:
                                        massing_code = size_item.get("massingCode")
                                        value = size_item.get("value")
                                        if massing_code and value:
                                            try:
                                                if '.' in str(value):
                                                    massing_rule_size[massing_code] = float(value)
                                                else:
                                                    massing_rule_size[massing_code] = int(value)
                                            except:
                                                massing_rule_size[massing_code] = value
                                item["massingRuleSize"] = massing_rule_size
                return {"success": True, "message": "订单明细查询成功", "data": order_items}
            else:
                return {"success": False, "message": f"订单明细查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"订单明细查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"订单明细查询请求异常: {str(e)}"}

# ========== 基础信息API调用函数 ==========

def api_get_pattern_type_list():
    """获取款式分类列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_type_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "款式分类列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"款式分类列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"款式分类列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"款式分类列表查询请求异常: {str(e)}"}

def api_get_pattern_list():
    """获取版型列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "版型列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"版型列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"版型列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"版型列表查询请求异常: {str(e)}"}

def api_get_massing_list():
    """获取量体信息列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["massing_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "量体信息列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"量体信息列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"量体信息列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"量体信息列表查询请求异常: {str(e)}"}

def api_get_pattern_attr_list():
    """获取定制选项列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_attr_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "定制选项列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"定制选项列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"定制选项列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"定制选项列表查询请求异常: {str(e)}"}

def api_get_pattern_attr_type_list():
    """获取定制选项分类列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_attr_type_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "定制选项分类列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"定制选项分类列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"定制选项分类列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"定制选项分类列表查询请求异常: {str(e)}"}

def api_get_pattern_structure_list():
    """获取版型结构列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_structure_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "版型结构列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"版型结构列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"版型结构列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"版型结构列表查询请求异常: {str(e)}"}

def api_get_pattern_structure_type_list():
    """获取版型结构分类列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["pattern_structure_type_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "版型结构分类列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"版型结构分类列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"版型结构分类列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"版型结构分类列表查询请求异常: {str(e)}"}

def api_get_special_massing_list():
    """获取特体信息列表"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(API_CONFIG["special_massing_list_url"], headers=headers, json={}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "特体信息列表查询成功", "data": result.get("data", [])}
            else:
                return {"success": False, "message": f"特体信息列表查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"特体信息列表查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"特体信息列表查询请求异常: {str(e)}"}

def api_get_specs_info_by_code(specs_code):
    """根据规格单编码获取规格单信息"""
    token = get_token()
    if not token:
        return {"success": False, "message": "无法获取token"}
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    request_data = {"code": specs_code}
    
    try:
        response = requests.post(API_CONFIG["specs_info_by_code_url"], headers=headers, json=request_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                return {"success": True, "message": "规格单信息查询成功", "data": result.get("data", {})}
            else:
                return {"success": False, "message": f"规格单信息查询失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"规格单信息查询请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"规格单信息查询请求异常: {str(e)}"}

def api_upload_image(image_path):
    """上传图片到服务器，返回图片URL"""
    try:
        if not os.path.exists(image_path):
            return {"success": False, "message": f"图片文件不存在: {image_path}"}
        
        token = get_api_token()
        headers = {"Authorization": token}
        
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_CONFIG["upload_url"], headers=headers, files=files, timeout=30)
        
        print(f"图片上传URL: {API_CONFIG['upload_url']}")
        print(f"图片上传响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 1000:
                image_url = result.get("data", {}).get("url", "")
                if image_url:
                    return {"success": True, "message": "图片上传成功", "data": {"url": image_url}}
                else:
                    return {"success": False, "message": f"图片上传失败: 返回数据中没有URL"}
            else:
                return {"success": False, "message": f"图片上传失败: {result.get('message', '未知错误')}"}
        else:
            return {"success": False, "message": f"图片上传请求失败，状态码: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"图片上传请求异常: {str(e)}"}

def upload_image(params):
    """上传图片（支持OpenClaw）"""
    image_path = params.get("image_path")
    
    if not image_path:
        return {"success": False, "message": "图片路径为必填项"}
    
    return api_upload_image(image_path)

def query_order(params):
    """查询订单状态（优先调用API）"""
    order_id = params.get("order_id")
    
    if not order_id:
        return {"success": False, "message": "订单ID为必填项"}
    
    # 尝试调用API查询
    api_result = api_query_order_info(order_id)
    
    if api_result["success"]:
        return api_result
    else:
        # API查询失败，使用本地存储
        print(f"API查询失败，使用本地存储: {api_result['message']}")
        
        orders = load_orders()
        
        if order_id not in orders:
            return {"success": False, "message": f"订单 {order_id} 不存在"}
        
        return {
            "success": True,
            "message": "订单查询成功（本地存储）",
            "data": orders[order_id]
        }

def update_order(params):
    """修改订单信息"""
    order_id = params.get("order_id")
    
    if not order_id:
        return {"success": False, "message": "订单ID为必填项"}
    
    orders = load_orders()
    
    if order_id not in orders:
        return {"success": False, "message": f"订单 {order_id} 不存在"}
    
    order = orders[order_id]
    
    # 只允许修改未发货状态的订单
    if order["status"] != "pending":
        return {"success": False, "message": "只能修改未发货状态的订单"}
    
    # 更新可修改的字段
    if "customer_name" in params:
        order["customer_name"] = params["customer_name"]
    if "product" in params:
        order["product"] = params["product"]
    if "quantity" in params:
        order["quantity"] = params["quantity"]
    if "amount" in params:
        order["amount"] = params["amount"]
    
    order["updated_at"] = datetime.now().isoformat()
    save_orders(orders)
    
    return {
        "success": True,
        "message": "订单修改成功",
        "data": order
    }

def cancel_order(params):
    """取消订单"""
    order_id = params.get("order_id")
    
    if not order_id:
        return {"success": False, "message": "订单ID为必填项"}
    
    orders = load_orders()
    
    if order_id not in orders:
        return {"success": False, "message": f"订单 {order_id} 不存在"}
    
    order = orders[order_id]
    
    # 只允许取消未发货状态的订单
    if order["status"] != "pending":
        return {"success": False, "message": "只能取消未发货状态的订单"}
    
    order["status"] = "cancelled"
    order["updated_at"] = datetime.now().isoformat()
    save_orders(orders)
    
    return {
        "success": True,
        "message": "订单已取消",
        "data": order
    }

def describe():
    """
    OpenClaw 技能描述函数（必需）
    :return: 技能描述信息
    """
    return {
        "name": "客商订单管理技能",
        "description": "支持创建订单、查询订单状态、修改订单信息、取消订单等功能",
        "version": "1.0",
        "actions": [
            {
                "name": "create",
                "description": "创建新订单",
                "parameters": {
                    "khName": {"type": "string", "required": True, "description": "客户姓名"},
                    "items": {"type": "array", "required": True, "description": "订单明细列表"}
                }
            },
            {
                "name": "query",
                "description": "查询订单",
                "parameters": {
                    "order_id": {"type": "string", "required": True, "description": "订单ID"}
                }
            },
            {
                "name": "update",
                "description": "修改订单",
                "parameters": {
                    "order_id": {"type": "string", "required": True, "description": "订单ID"}
                }
            },
            {
                "name": "cancel",
                "description": "取消订单",
                "parameters": {
                    "order_id": {"type": "string", "required": True, "description": "订单ID"}
                }
            }
        ]
    }

def handle(action, params):
    """
    OpenClaw 技能处理函数（必需）
    :param action: 操作类型
    :param params: 参数对象
    :return: 处理结果
    """
    actions = {
        "create": create_order,
        "query": query_order,
        "update": update_order,
        "cancel": cancel_order,
        "upload": upload_image
    }
    
    if action not in actions:
        return {"success": False, "message": f"不支持的操作类型: {action}"}
    
    return actions[action](params)

def handler(input_data, context=None):
    """
    OpenClaw Agent 调用入口函数（兼容旧版）
    :param input_data: 输入参数对象
    :param context: 上下文信息
    :return: 输出结果对象
    """
    # 认证检查（使用真实API认证）
    auth_success, auth_message, token = authenticate()
    if not auth_success:
        return {"success": False, "message": auth_message, "data": {}}
    
    action = input_data.get("action")
    
    # 如果没有指定action但有text参数，默认使用create操作
    if not action and "text" in input_data and input_data["text"]:
        action = "create"
    
    if not action:
        return {"success": False, "message": "请指定操作类型 (create/query/update/cancel)"}
    
    return handle(action, input_data)

def str2bool(v):
    """自定义布尔类型解析"""
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return False

def main():
    """命令行入口 - 支持多种输入方式"""
    parser = argparse.ArgumentParser(description="客商订单管理技能")
    
    # JSON输入方式
    parser.add_argument('--json', type=str, help='JSON格式的订单数据')
    parser.add_argument('--json-file', type=str, help='包含订单数据的JSON文件路径')
    parser.add_argument('--text', type=str, help='自然语言描述的订单数据（如：客户姓名是张三，1KN002的50码）')
    
    # 命令行参数方式（保持兼容）
    parser.add_argument("--action", choices=["create", "query", "update", "cancel", "upload"],
                        help="操作类型")
    parser.add_argument("--image_path", help="图片文件路径（用于上传）")
    parser.add_argument("--order_id", help="订单ID")
    
    # 订单新增必填字段
    parser.add_argument("--ksOrderNo", help="客商单号")
    parser.add_argument("--tradeMarkName", help="商标名")
    parser.add_argument("--khName", help="客户姓名")
    parser.add_argument("--khMtel", help="手机号码")
    parser.add_argument("--khAddress", help="收货地址")
    parser.add_argument("--khShapeCode", help="体型")
    parser.add_argument("--khImgurls", help="客户照片URL")
    parser.add_argument("--deliveryDate", help="成品交货日期 (YYYY-MM-DD)")
    parser.add_argument("--orderRemarks", help="订单备注")
    parser.add_argument("--isManualOrder", type=str2bool, default=False, help="是否手工单 (true/false)")
    parser.add_argument("--manualOrderhImgurls", help="手工单图片URL")
    parser.add_argument("--isGroupOrder", type=str2bool, default=False, help="是否团单 (true/false)")
    
    # 订单明细必填字段
    parser.add_argument("--patternTypeCode", help="款式类型编码")
    parser.add_argument("--patternCode", help="版型编码")
    parser.add_argument("--fabricSupply", help="面料供应")
    parser.add_argument("--fabricMark", help="面料标/面料品牌")
    parser.add_argument("--lining", help="里布")
    parser.add_argument("--fabric", help="面料编号")
    parser.add_argument("--composition", help="面料成分")
    parser.add_argument("--fabricOrigin", help="面料产地")
    parser.add_argument("--placketNeedle", help="门襟贡针")
    parser.add_argument("--button", help="纽扣")
    parser.add_argument("--isSample", type=str2bool, default=False, help="是否试样 (true/false)")
    parser.add_argument("--halfDeliveryDate", help="半成品交货日期 (YYYY-MM-DD)")
    parser.add_argument("--sampleFabric", help="试样面料")
    parser.add_argument("--ksRemark", help="客商备注")
    parser.add_argument("--patternImgurl", help="版型图片")
    parser.add_argument("--ksMassingCodes", help="客商_量体部位 (逗号分隔)")
    parser.add_argument("--specsCode", help="规格单编码")
    parser.add_argument("--size", help="尺码")
    parser.add_argument("--drop", help="落差")
    parser.add_argument("--isEmbroider", type=str2bool, default=False, help="是否绣花 (true/false)")
    parser.add_argument("--embroiderText", help="绣花文字")
    parser.add_argument("--embroiderTypeface", help="绣花字体")
    parser.add_argument("--embroiderColor", help="绣花颜色")
    parser.add_argument("--embroiderPic", help="绣花图案")
    
    # 版型属性 - 西装上衣
    parser.add_argument("--syJag", help="版型属性-加放量")
    parser.add_argument("--syYdj", help="版型属性-衣袋件")
    parser.add_argument("--syCraft", help="版型属性-工艺")
    parser.add_argument("--syJacketVent", help="版型属性-开叉")
    parser.add_argument("--syCuffKeyhole", help="版型属性-袖克夫钥匙孔")
    parser.add_argument("--syJacketPockets", help="版型属性-口袋")
    parser.add_argument("--sySleeveElastic", help="版型属性-袖松紧")
    parser.add_argument("--syJacketTowelBag", help="版型属性-毛巾袋")
    parser.add_argument("--syPlacketKeyhole", help="版型属性-门襟钥匙孔")
    parser.add_argument("--syJacketButtonhole", help="版型属性-扣眼")
    parser.add_argument("--syJacketSleeveType", help="版型属性-袖型")
    parser.add_argument("--syJacketChestLining", help="版型属性-胸衬")
    parser.add_argument("--syJacketShoulderPads", help="版型属性-肩垫")
    parser.add_argument("--syJacketSleeveButton", help="版型属性-袖扣")
    parser.add_argument("--syHalfMileLiningStyle", help="版型属性-半里款式")
    
    # 版型属性 - 西裤
    parser.add_argument("--xkYks", help="版型属性-腰头松紧")
    parser.add_argument("--xkSlide", help="版型属性-滑扣")
    parser.add_argument("--xkJkjzd", help="版型属性-裤脚加固")
    parser.add_argument("--xkHemOpening", help="版型属性-脚口")
    parser.add_argument("--xkPantsPocket", help="版型属性-裤口袋")
    parser.add_argument("--xkStrapBuckle", help="版型属性-松紧带")
    parser.add_argument("--xkPantFrontFly", help="版型属性-门襟")
    parser.add_argument("--xkPantBackPocket", help="版型属性-后袋")
    parser.add_argument("--xkPantsWaistStyle", help="版型属性-裤腰款式")
    parser.add_argument("--xkTrouserFrontPockets", help="版型属性-前插袋")
    
    # 版型结构
    parser.add_argument("--lapelType", help="版型结构-领型")
    parser.add_argument("--lapelWidth", help="版型结构-领宽")
    parser.add_argument("--buttonNumber", help="版型结构-扣数")
    parser.add_argument("--liningConstructions", help="版型结构-里布结构")
    parser.add_argument("--ph", help="版型结构-裤厚")
    parser.add_argument("--xb", help="版型结构-西裤")
    parser.add_argument("--xzks", help="版型结构-下装款式")
    parser.add_argument("--pleat", help="版型结构-褶裥")
    
    # 客商成衣尺寸
    parser.add_argument("--fullBust", type=int, help="成衣尺寸-胸围")
    parser.add_argument("--fullWaistWidth", type=int, help="成衣尺寸-腰围")
    parser.add_argument("--fullHipWidth", type=int, help="成衣尺寸-臀围")
    parser.add_argument("--lowerHem", type=int, help="成衣尺寸-下摆")
    parser.add_argument("--shoulderWidth", type=float, help="成衣尺寸-肩宽")
    parser.add_argument("--sleeveLength", type=int, help="成衣尺寸-袖长")
    parser.add_argument("--frontLength", type=int, help="成衣尺寸-前长")
    parser.add_argument("--shortRegularTall", type=int, help="成衣尺寸-长短")
    parser.add_argument("--wrisband", type=float, help="成衣尺寸-腕围")
    parser.add_argument("--sleeveWidth", type=float, help="成衣尺寸-袖宽")
    parser.add_argument("--backWidth", type=int, help="成衣尺寸-背宽")
    
    # 套码尺寸
    parser.add_argument("--stdFullBust", type=int, help="套码尺寸-胸围")
    parser.add_argument("--stdFullWaistWidth", type=int, help="套码尺寸-腰围")
    parser.add_argument("--stdFullHipWidth", type=int, help="套码尺寸-臀围")
    parser.add_argument("--stdLowerHem", type=int, help="套码尺寸-下摆")
    parser.add_argument("--stdShoulderWidth", type=float, help="套码尺寸-肩宽")
    parser.add_argument("--stdSleeveLength", type=int, help="套码尺寸-袖长")
    parser.add_argument("--stdFrontLength", type=int, help="套码尺寸-前长")
    parser.add_argument("--stdShortRegularTall", type=int, help="套码尺寸-长短")
    parser.add_argument("--stdWrisband", type=float, help="套码尺寸-腕围")
    parser.add_argument("--stdSleeveWidth", type=float, help="套码尺寸-袖宽")
    parser.add_argument("--stdBackWidth", type=int, help="套码尺寸-背宽")
    
    # 净尺寸（完整支持所有量体项目）
    parser.add_argument("--netFullBust", type=int, help="净尺寸-胸围")
    parser.add_argument("--netFullHipWidth", type=int, help="净尺寸-臀围")
    parser.add_argument("--netFullWaistWidth", type=int, help="净尺寸-腰围")
    parser.add_argument("--netLowerHem", type=int, help="净尺寸-下摆")
    parser.add_argument("--netShoulderWidth", type=float, help="净尺寸-肩宽")
    parser.add_argument("--netSleeveLength", type=int, help="净尺寸-袖长")
    parser.add_argument("--netFrontLength", type=int, help="净尺寸-前长")
    parser.add_argument("--netBackWidth", type=int, help="净尺寸-背宽")
    parser.add_argument("--netShortRegularTall", type=int, help="净尺寸-长短")
    parser.add_argument("--netWrisband", type=float, help="净尺寸-腕围")
    parser.add_argument("--netSleeveWidth", type=float, help="净尺寸-袖宽")
    
    # 特体尺码
    parser.add_argument("--syFlatShoulder", type=int, help="特体尺码-平肩")
    parser.add_argument("--ksSpecialBodyRemark", help="特体备注")
    
    # 兼容旧参数
    parser.add_argument("--customer_name", help="客户名称（兼容旧参数）")
    parser.add_argument("--phone", help="客户手机号（兼容旧参数）")
    parser.add_argument("--product", help="商品名称")
    parser.add_argument("--quantity", type=int, default=1, help="商品数量")
    parser.add_argument("--amount", type=float, default=0.0, help="订单金额")
    
    args = parser.parse_args()
    
    # 自然语言输入方式（优先级最高）
    if args.text:
        # 解析自然语言订单描述
        try:
            parse_result = parse_text_order(args.text)
            if parse_result["success"]:
                input_data = parse_result["data"]
                input_data["action"] = "create"
                result = handler(input_data)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(parse_result, ensure_ascii=False, indent=2))
            return
        except Exception as e:
            print(f"文本解析错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return
    
    # JSON输入方式
    elif args.json:
        # 从命令行参数获取JSON数据
        try:
            input_data = json.loads(args.json)
            # 自动添加action为create
            if "action" not in input_data:
                input_data["action"] = "create"
            result = handler(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            return
    
    elif args.json_file:
        # 从文件读取JSON数据
        try:
            with open(args.json_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            # 自动添加action为create
            if "action" not in input_data:
                input_data["action"] = "create"
            result = handler(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        except FileNotFoundError:
            print(f"文件不存在: {args.json_file}")
            return
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            return
    
    # 命令行参数方式（保持兼容）
    input_data = {k: v for k, v in vars(args).items() if v is not None}
    
    # 处理数组类型参数
    if "ksMassingCodes" in input_data and input_data["ksMassingCodes"]:
        input_data["ksMassingCodes"] = input_data["ksMassingCodes"].split(",")
    
    # 处理净尺寸参数，组合成netSize字段
    net_size = {}
    net_size_mapping = {
        "netFullBust": "fullBust",
        "netFullHipWidth": "fullHipWidth",
        "netFullWaistWidth": "fullWaistWidth",
        "netLowerHem": "lowerHem",
        "netShoulderWidth": "shoulderWidth",
        "netSleeveLength": "sleeveLength",
        "netFrontLength": "frontLength",
        "netBackWidth": "backWidth",
        "netShortRegularTall": "shortRegularTall",
        "netWrisband": "wrisband",
        "netSleeveWidth": "sleeveWidth"
    }
    for arg_name, field_name in net_size_mapping.items():
        if arg_name in input_data:
            net_size[field_name] = input_data.pop(arg_name)
    if net_size:
        input_data["netSize"] = net_size
    
    # 处理版型属性参数，组合成ksPatternAttr字段
    pattern_attr = {}
    pattern_attr_mapping = {
        "syJag": "SY_jag",
        "syYdj": "SY_ydj",
        "syCraft": "SY_craft",
        "syJacketVent": "SY_jacketVent",
        "syCuffKeyhole": "SY_cuffKeyhole",
        "syJacketPockets": "SY_jacketPockets",
        "sySleeveElastic": "SY_sleeveElastic",
        "syJacketTowelBag": "SY_jacketTowelBag",
        "syPlacketKeyhole": "SY_placketKeyhole",
        "syJacketButtonhole": "SY_jacketButtonhole",
        "syJacketSleeveType": "SY_jacketSleeveType",
        "syJacketChestLining": "SY_jacketChestLining",
        "syJacketShoulderPads": "SY_jacketShoulderPads",
        "syJacketSleeveButton": "SY_jacketSleeveButton",
        "syHalfMileLiningStyle": "SY_halfMileLiningStyle",
        "syMilanEyeColor": "SY_milanEyeColor",
        "syHalfLining": "SY_halfLining",
        "xkYks": "XK_yks",
        "xkSlide": "XK_Slide",
        "xkJkjzd": "XK_jkjzd",
        "xkHemOpening": "XK_hemOpening",
        "xkPantsPocket": "XK_pantsPocket",
        "xkStrapBuckle": "XK_waistStyle",
        "xkPantFrontFly": "XK_pantFrontFly",
        "xkPantBackPocket": "XK_pantBackPocket",
        "xkPantsWaistStyle": "XK_pantsWaistStyle",
        "xkTrouserFrontPockets": "XK_trouserFrontPockets"
    }
    for arg_name, field_name in pattern_attr_mapping.items():
        if arg_name in input_data:
            pattern_attr[field_name] = input_data.pop(arg_name)
    if pattern_attr:
        input_data["ksPatternAttr"] = pattern_attr
    
    # 处理版型结构参数，组合成ksPatternStructure字段
    pattern_structure = {}
    pattern_structure_mapping = {
        "lapelType": "lapelType",
        "lapelWidth": "lapelWidth",
        "buttonNumber": "buttonNumber",
        "liningConstructions": "liningConstructions",
        "ph": "ph",
        "xb": "xb",
        "xzks": "xzks",
        "pleat": "pleat"
    }
    for arg_name, field_name in pattern_structure_mapping.items():
        if arg_name in input_data:
            pattern_structure[field_name] = input_data.pop(arg_name)
    if pattern_structure:
        input_data["ksPatternStructure"] = pattern_structure
    
    # 调用处理函数
    result = handler(input_data)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
