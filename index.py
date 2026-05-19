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
    "access_key_id": "Er2Utq8yHCOIt4b2",
    "access_key_secret": "7d3d4047913cc6465d9ad36ac807cac9",
    "cached_token": None
}

# 模拟订单存储（实际应用中应使用数据库）
ORDERS_STORAGE = "orders.json"

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
    """解析自然语言描述的订单数据"""
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
    name_match = re.search(r'客户姓名[是为：:]([\u4e00-\u9fa5A-Za-z0-9]+)', text)
    if name_match:
        result["khName"] = name_match.group(1).strip()
    
    # 提取图片路径（支持本地文件路径或URL）
    image_path_match = re.search(r'图片[是为：:]([^，。、\n]+)', text)
    if image_path_match:
        image_path = image_path_match.group(1).strip()
        result["image_path"] = image_path
        # 如果是URL，直接使用；如果是本地路径，后续会自动上传
        if image_path.startswith("http://") or image_path.startswith("https://"):
            result["khImgurls"] = image_path
    
    # 提取面料货号（支持特殊字符如 - / .）
    fabric_match = re.search(r'面料货号[是为：:]([\w\-\./]+)', text)
    if not fabric_match:
        fabric_match = re.search(r'面料[是为：:]([\w\-\./]+)', text)
    fabric = fabric_match.group(1).strip() if fabric_match else ""
    
    # 提取版型编码和尺码（支持多个版型）
    # 先匹配"XX的XX码"格式
    pattern_matches = re.findall(r'([A-Z0-9]+)的(\d+码)', text)
    # 再补充匹配"XX XX码"格式（空格分隔）
    pattern_matches += re.findall(r'([A-Z0-9]+)\s+(\d+码)', text)
    
    # 提取落差（支持多种表达方式）
    # 系统支持的落差值为 R(常规) 和 C(舒适)
    drop = ""
    
    # 支持用户输入"落差R"、"落差C"、"常规"、"舒适"等
    drop_match = re.search(r'落差[是为：:]*([RCrc])', text)
    if not drop_match:
        drop_match = re.search(r'落差[是为：:]*([Rr]常规|[Cc]舒适)', text)
    if not drop_match:
        drop_match = re.search(r'([Rr]常规|[Cc]舒适)', text)
    
    if drop_match:
        match_str = drop_match.group(1).strip().upper()
        if 'R' in match_str or '常规' in match_str:
            drop = 'R'
        elif 'C' in match_str or '舒适' in match_str:
            drop = 'C'
    
    # 如果用户输入数字，尝试映射到系统支持的值（通常数字0或6对应R，其他对应C）
    if not drop:
        num_match = re.search(r'落差[是为：:]*(\d+)', text)
        if not num_match:
            num_match = re.search(r'落\s*(\d+)', text)
        if num_match:
            num_val = int(num_match.group(1))
            # 数字0或6通常对应常规(R)，其他值可能对应舒适(C)
            drop = 'R' if num_val in (0, 6) else 'C'
    
    # 提取上衣定制选项（支持"改"、"改成"、"调整"、"换"、"变"等动词）
    sy_attr = {}
    modify_words = r'(?:改成|改为|调整|换|变|改)'
    

    # 定制选项映射表 - 将用户输入的简短选项映射到系统期望的完整值（从版型属性数据表格导入）
    custom_option_mappings = {
        "DY_coatPockets": {
            "无": "DY_coatPockets_wu",  # 无
            "4KN1075斜双支线袋": "DY_coatPockets_xszxd",  # 4KN1075斜双支线袋
            "A款 直斜插袋": "DY_coatPockets_zxcd",  # A款 直斜插袋
            "B款 明袋": "DY_coatPockets_bkmd",  # B款 明袋
            "C款 两袋盖": "DY_coatPockets_dg",  # C款 两袋盖
            "D款 明袋加袋盖": "DY_coatPockets_mdjdg",  # D款 明袋加袋盖
            "E款 明袋加西装袋盖": "DY_coatPockets_ekmdjxzdg",  # E款 明袋加西装袋盖
            "F款 单开线加袋盖": "DY_coatPockets_fkdkxjdg",  # F款 单开线加袋盖
            "G款 弧型斜插袋": "DY_coatPockets_gkhxxcd",  # G款 弧型斜插袋
            "H款 袋盖斜插袋": "DY_coatPockets_dgxcd",  # H款 袋盖斜插袋
            "I款 袋盖斜插袋": "DY_coatPockets_ikdgjxd",  # I款 袋盖斜插袋
            "专用口袋": "DY_coatPockets_zymd",  # 专用口袋
            "J款 斜袋袋盖小料": "DY_coatPockets_jkxddg",  # J款 斜袋袋盖小料
            "K款 斜插明袋": "DY_coatPockets_kkxcmd",  # K款 斜插明袋
            "L款 三袋盖": "DY_coatPockets_lksdg",  # L款 三袋盖
            "M款 明袋加斜袋盖": "DY_coatPockets_mdjxdg",  # M款 明袋加斜袋盖
            "双支线": "DY_coatPockets_szx",  # 双支线
            "N款 可侧插明袋加袋盖": "DY_coatPockets_Nk",  # N款 可侧插明袋加袋盖
            "O款 加大版 明袋加袋盖": "DY_coatPockets_jdbmdjdg",  # O款 加大版 明袋加袋盖
            "P款 明袋袋盖 加斜插袋": "DY_coatPockets_pkkd",  # P款 明袋袋盖 加斜插袋
            "Q款：立体明袋袋盖 加斜插袋": "DY_coatPockets_ltmdjxcd",  # Q款：立体明袋袋盖 加斜插袋
            "拼接明袋": "DY_coatPockets_pjmd",  # 拼接明袋
        },
        "DY_coatSleeveButton": {
            "一扣": "DY_coatSleeveButton_oneBuckle",  # 一扣
            "叠扣": "DY_coatSleeveButton_dk",  # 叠扣
            "袖袢": "DY_coatSleeveButton_xb",  # 袖袢
            "翻折6CM": "DY_coattSleeveButton_bz6cm",  # 翻折6CM
            "平扣": "DY_coatSleeveButton_flatBuckle",  # 平扣
            "斜扣	": "DY_coatSleeveButton_diagonalBuckle",  # 斜扣	
            "斜眼叠扣": "DY_coatSleeveButton_slantBuckle",  # 斜眼叠扣
            "斜眼平扣": "DY_coatSleeveButton_flatFoldingBuckle",  # 斜眼平扣
            "翻折 7.5cm": "DY_coatSleeveButton_fz7.5",  # 翻折 7.5cm
            "翻折9.5cm": "DY_coatSleeveButton_xkfb9.5",  # 翻折9.5cm
            "无": "DY_coatSleeveButton_wu",  # 无
            "翻折10.8cm": "DY_coatSleeveButton_fz10.8",  # 翻折10.8cm
            "专用袖扣": "DY_coatSleeveButton_zyxk",  # 专用袖扣
        },
        "DY_craft": {
            "半麻衬": "DY_craft_bmc",  # 半麻衬
            "全麻衬": "DY_craft_fullCanvas",  # 全麻衬
            "粘合衬": "DY_craft_adhesionCanvas",  # 粘合衬
        },
        "DY_cuffKeyhole": {
            "一扣": "DY_cuffKeyhole_oneButton ",  # 一扣
            "二扣": "DY_cuffKeyhole_twoBuckles",  # 二扣
            "三扣": "DY_cuffKeyhole_threeBuckles",  # 三扣
            "四扣": "DY_cuffKeyhole_fourBuckles",  # 四扣
            "五扣": "DY_cuffKeyhole_fiveBuckles",  # 五扣
            "无": "DY_cuffKeyhole_wu",  # 无
        },
        "DY_curvedHandmadeColor": {
            "顺色": "DY_curvedHandmadeColor_matchFabric",  # 顺色
            "000": "DY_curvedHandmadeColor_000",  # 000
            "46": "DY_curvedHandmadeColor_46",  # 46
            "130": "DY_curvedHandmadeColor_130",  # 130
            "131": "DY_curvedHandmadeColor_131",  # 131
            "155": "DY_curvedHandmadeColor_155",  # 155
            "174": "DY_curvedHandmadeColor_174",  # 174
            "196": "DY_curvedHandmadeColor_196",  # 196
            "214": "DY_curvedHandmadeColor_214",  # 214
            "247": "DY_curvedHandmadeColor_247",  # 247
            "339": "DY_curvedHandmadeColor_339",  # 339
            "367": "DY_curvedHandmadeColor_367",  # 367
            "387": "DY_curvedHandmadeColor_387",  # 387
            "412": "DY_curvedHandmadeColor_412",  # 412
            "440": "DY_curvedHandmadeColor_440",  # 440
            "454": "DY_curvedHandmadeColor_454",  # 454
            "540": "DY_curvedHandmadeColor_540",  # 540
            "542": "DY_curvedHandmadeColor_542",  # 542
            "665": "DY_curvedHandmadeColor_665",  # 665
            "697": "DY_curvedHandmadeColor_697",  # 697
            "701": "DY_curvedHandmadeColor_701",  # 701
            "702": "DY_curvedHandmadeColor_702",  # 702
            "769": "DY_curvedHandmadeColor_769",  # 769
            "800": "DY_curvedHandmadeColor_800",  # 800
            "802": "DY_curvedHandmadeColor_802",  # 802
            "810": "DY_curvedHandmadeColor_810",  # 810
            "812": "DY_curvedHandmadeColor_812",  # 812
            "889": "DY_curvedHandmadeColor_889",  # 889
            "909": "DY_curvedHandmadeColor_909",  # 909
            "925": "DY_curvedHandmadeColor_925",  # 925
            "964": "DY_curvedHandmadeColor_964",  # 964
        },
        "DY_halfAMile": {
            "锁边翘边": "DY_halfAMile_lockingAndWarping	",  # 锁边翘边
            "半里包边	": "DY_halfAMile_halfMileEdging",  # 半里包边	
        },
        "DY_hbks": {
            "A款": "DY_hbks_akzy",  # A款
            "4KN042 A款": "DY_hbks_ak042",  # 4KN042 A款
            "4KN041 A款": "DY_hbks_ak",  # 4KN041 A款
            "B款": "DY_hbks_bk",  # B款
            "4KN041无腰带款": "DY_hbks_ak041",  # 4KN041无腰带款
            "C款": "DY_hbks_ck",  # C款
            "4KN993 A款": "DY_hbks_dazhonak",  # 4KN993 A款
            "4KN045无叉款": "DY_hbks_wck045",  # 4KN045无叉款
            "4KN993 B款": "DY_hbks_dazhobk",  # 4KN993 B款
            "4KN045中开叉": "DY_hbks_zkc045",  # 4KN045中开叉
            "4KN042 A腰带款": "DY_hbks_ak042yyd",  # 4KN042 A腰带款
        },
        "DY_jacketButtonholeColor": {
            "顺色": "DY_jacketButtonholeColor_matchFabric",  # 顺色
            "000": "DY_jacketButtonholeColor_000",  # 000
            "46": "DY_jacketButtonholeColor_46",  # 46
            "130": "DY_jacketButtonholeColor_130",  # 130
            "131": "DY_jacketButtonholeColor_131",  # 131
            "155": "DY_jacketButtonholeColor_155",  # 155
            "174": "DY_jacketButtonholeColor_174",  # 174
            "196": "DY_jacketButtonholeColor_196",  # 196
            "214": "DY_jacketButtonholeColor_214",  # 214
            "247": "DY_jacketButtonholeColor_247",  # 247
            "339": "DY_jacketButtonholeColor_339",  # 339
            "367": "DY_jacketButtonholeColor_367",  # 367
            "387": "DY_jacketButtonholeColor_387",  # 387
            "412": "DY_jacketButtonholeColor_412",  # 412
            "440": "DY_jacketButtonholeColor_440",  # 440
            "454": "DY_jacketButtonholeColor_454",  # 454
            "540": "DY_jacketButtonholeColor_540",  # 540
            "542": "DY_jacketButtonholeColor_542",  # 542
            "665": "DY_jacketButtonholeColor_665",  # 665
            "697": "DY_jacketButtonholeColor_697",  # 697
            "701": "DY_jacketButtonholeColor_701",  # 701
            "702": "DY_jacketButtonholeColor_702",  # 702
            "769": "DY_jacketButtonholeColor_769",  # 769
            "800": "DY_jacketButtonholeColor_800",  # 800
            "802": "DY_jacketButtonholeColor_802",  # 802
            "810": "DY_jacketButtonholeColor_810",  # 810
            "812": "DY_jacketButtonholeColor_812",  # 812
            "889": "DY_jacketButtonholeColor_889",  # 889
            "909": "DY_jacketButtonholeColor_909",  # 909
            "925": "DY_jacketButtonholeColor_925",  # 925
            "964": "DY_jacketButtonholeColor_964",  # 964
        },
        "DY_overcoatButtonHole": {
            "艾伦眼": "DY_overcoatButtonHole_curvedHandmade",  # 艾伦眼
            "机器锁眼": "DY_overcoatButtonHole_machineMade ",  # 机器锁眼
            "手工米兰眼": "DY_overcoatButtonHole_milanese",  # 手工米兰眼
            "双边米兰眼": "DY_overcoatButtonHole_sbly",  # 双边米兰眼
            "取消驳头锁眼": "DY_overcoatButtonHole_cancelLapelButtonhole",  # 取消驳头锁眼
        },
        "DY_placketKeyhole": {
            "一明扣三暗扣": "DY_placketKeyhole_ymksaks",  # 一明扣三暗扣
            "一明扣四暗扣": "DY_placketKeyhole_ymksak",  # 一明扣四暗扣
            "一扣": "DY_placketKeyhole_oneButton ",  # 一扣
            "二扣": "DY_placketKeyhole_twoBuckles",  # 二扣
            "二扣半": "DY_placketKeyhole_twoAndAHalfBuckles",  # 二扣半
            "三扣": "DY_placketKeyhole_sq",  # 三扣
            "四扣": "DY_placketKeyhole_4b",  # 四扣
            "四扣二": "DY_placketKeyhole_fourBucklesAndWwo",  # 四扣二
            "四扣一": "DY_placketKeyhole_fourBucklesAndone",  # 四扣一
            "六扣三": "DY_placketKeyhole_lks",  # 六扣三
            "六扣二": "DY_placketKeyhole_sixBucklesAndTwo",  # 六扣二
            "六扣一": "DY_placketKeyhole_sixBucklesAndOne",  # 六扣一
            "八扣四": "DY_placketKeyhole_bks",  # 八扣四
            "十扣三": "DY_placketKeyhole_sksnk",  # 十扣三
            "十扣五": "DY_placketKeyhole_sbkw",  # 十扣五
        },
        "DY_safariSuit": {
            "腰带款": "DY_safariSuit_beltStyle",  # 腰带款
            "抽绳款": "DY_safariSuit_pullOutPayment",  # 抽绳款
        },
        "DY_sjd": {
            "无": "DY_sjd_wu",  # 无
            "直手巾袋": "DY_sjd_zsjd",  # 直手巾袋
            "弧手巾袋": "DY_sjd_hsjd",  # 弧手巾袋
            "弧形小明袋": "DY_sjd_hxxmd",  # 弧形小明袋
            "两个打褶圆角明袋加袋盖": "DY_sjd_dzyjmdjdg",  # 两个打褶圆角明袋加袋盖
            "上两直手巾袋": "DY_sjd_slzsjd",  # 上两直手巾袋
            "小酒杯明袋": "DY_sjd_xjbmd",  # 小酒杯明袋
            "小明袋": "DY_sjd_xmd",  # 小明袋
            "两个打褶直角明袋加袋盖": "DY_sjd_dzjjmdjdg",  # 两个打褶直角明袋加袋盖
            "双支线加袋盖": "DY_sjd_szxjdg",  # 双支线加袋盖
            "一个圆角打褶明袋加斜袋盖": "DY_sjd_yjdzmdjxdg",  # 一个圆角打褶明袋加斜袋盖
            "船型手巾袋": "DY_sjd_CXSJD",  # 船型手巾袋
            "斜插双支线袋": "DY_sjd_xcszxd",  # 斜插双支线袋
        },
        "LZ_bl": {
            "半里包边": "LZ_bl_blbb",  # 半里包边
            "锁边翘边": "LZ_bl_sbqb",  # 锁边翘边
        },
        "LZ_bllbfg": {
            "一字后里": "LZ_bllbfg_yzhl",  # 一字后里
            "交叉后里": "LZ_bllbfg_jchl",  # 交叉后里
            "前全里后半里": "LZ_bllbfg_qqlhbl",  # 前全里后半里
        },
        "LZ_btsy": {
            "艾伦眼": "LZ_btsy_aly",  # 艾伦眼
            "机器锁眼": "LZ_btsy_yqsy",  # 机器锁眼
            "手工米兰眼": "LZ_btsy_sgmly",  # 手工米兰眼
            "手工圆头锁眼": "LZ_btsy_sgytsy",  # 手工圆头锁眼
            "圆头锁眼": "LZ_btsy_ytsy",  # 圆头锁眼
            "双边米兰眼": "LZ_btsy_sbmly",  # 双边米兰眼
            "取消驳头锁眼": "LZ_btsy_qxbtsy",  # 取消驳头锁眼
            "手工圆头1.5圆头锁眼": "LZ_btsy_sgyt",  # 手工圆头1.5圆头锁眼
        },
        "LZ_gy": {
            "半麻衬": "LZ_gy_bmc",  # 半麻衬
            "全麻衬": "LZ_gy_qmc",  # 全麻衬
            "无结构": "LZ_gy_wjg",  # 无结构
        },
        "LZ_lz": {
            "抽绳款": "LZ_lz_csk",  # 抽绳款
            "腰带款": "LZ_lz_ydk",  # 腰带款
        },
        "LZ_mjsy": {
            "一明扣四暗扣": "LZ_mjsy_1mksak",  # 一明扣四暗扣
            "一扣": "LZ_mjsy_1b",  # 一扣
            "二扣": "LZ_mjsy_2B",  # 二扣
            "二扣半": "LZ_mjsy_2KB",  # 二扣半
            "二扣一": "LZ_mjsy_2ky",  # 二扣一
            "三扣": "LZ_mjsy_3sk",  # 三扣
            "三扣二": "LZ_mjsy_3kr",  # 三扣二
            "四扣": "LZ_mjsy_4b",  # 四扣
            "四扣二": "LZ_mjsy_4skr",  # 四扣二
            "四扣一": "LZ_mjsy_4ky",  # 四扣一
            "五扣": "LZ_mjsy_5k",  # 五扣
            "六扣": "LZ_mjsy_lk",  # 六扣
            "六扣二": "LZ_mjsy_6kr",  # 六扣二
            "六扣一": "LZ_mjsy_6ky",  # 六扣一
            "对扣": "LZ_mjsy_dk",  # 对扣
            "一暗扣两明扣": "LZ_mjsy_yaklmk",  # 一暗扣两明扣
        },
        "LZ_sjd": {
            "弧手巾袋": "LZ_sjd_hsjd",  # 弧手巾袋
            "SA立体": "LZ_sjd_SAlt",  # SA立体
            "SA": "LZ_sjd_SA",  # SA
            "SB": "LZ_sjd_SB",  # SB
            "SC立体": "LZ_sjd_sclt",  # SC立体
            "SC": "LZ_sjd_SC",  # SC
            "SD": "LZ_sjd_SD",  # SD
            "SE": "LZ_sjd_SE",  # SE
            "SF": "LZ_sjd_SF",  # SF
            "SH": "LZ_sjd_SH",  # SH
            "SI立体": "LZ_sjd_silt",  # SI立体
            "SI": "LZ_sjd_SI",  # SI
            "SJ": "LZ_sjd_SJ",  # SJ
            "SK": "LZ_sjd_SK",  # SK
            "SL": "LZ_sjd_SL",  # SL
            "SM立体": "LZ_sjd_smltmdjdg",  # SM立体
            "SM": "LZ_sjd_SM",  # SM
            "ST": "LZ_sjd_st",  # ST
            "SS": "LZ_sjd_ss",  # SS
            "SN": "LZ_sjd_sn",  # SN
            "MG口袋": "LZ_sjd_mgkd",  # MG口袋
            "1SF024专用口袋": "LZ_sjd_1SF024zy",  # 1SF024专用口袋
            "Y款 圆角打褶明袋": "LZ_sjd_yk",  # Y款 圆角打褶明袋
            "1SF028专用口袋": "LZ_sjd_1SF028",  # 1SF028专用口袋
            "1SF014专用口袋": "LZ_sjd_1sf014zykd",  # 1SF014专用口袋
            "1JAS03专用口袋": "LZ_sjd_jaszykd",  # 1JAS03专用口袋
        },
        "LZ_syhc": {
            "双开叉": "LZ_syhc_skc",  # 双开叉
            "中开叉": "LZ_syhc_zkc",  # 中开叉
            "不开叉": "LZ_syhc_bkc",  # 不开叉
        },
        "LZ_symdd": {
            "MA立体": "LZ_symdd_MAlt",  # MA立体
            "MA": "LZ_symdd_MA",  # MA
            "MB": "LZ_symdd_MB",  # MB
            "MC立体": "LZ_symdd_mclt",  # MC立体
            "MC": "LZ_symdd_MC",  # MC
            "MD": "LZ_symdd_MD",  # MD
            "ME": "LZ_symdd_ME",  # ME
            "MG三明袋": "LZ_symdd_MG",  # MG三明袋
            "MH": "LZ_symdd_MH",  # MH
            "MI立体": "LZ_symdd_milt",  # MI立体
            "MI": "LZ_symdd_MI",  # MI
            "MJ": "LZ_symdd_MJ",  # MJ
            "MK": "LZ_symdd_MK",  # MK
            "ML": "LZ_symdd_ML",  # ML
            "MM立体": "LZ_symdd_mmltmd",  # MM立体
            "MM": "LZ_symdd_MM",  # MM
            "MN": "LZ_symdd_MN",  # MN
            "MO": "LZ_symdd_MO",  # MO
            "MP": "LZ_symdd_mpkd",  # MP
            "MQ": "LZ_symdd_mq",  # MQ
            "MR": "LZ_symdd_mr",  # MR
            "MS": "LZ_symdd_mskd",  # MS
            "MT": "LZ_symdd_mtkd",  # MT
            "A款 两直袋盖": "LZ_symdd_lzdg",  # A款 两直袋盖
            "B款 两明袋": "LZ_symdd_bklmd",  # B款 两明袋
            "C款 双支线": "LZ_symdd_szx",  # C款 双支线
            "Y款 圆角打褶明袋": "LZ_symdd_yk",  # Y款 圆角打褶明袋
            "1SF044": "LZ_symdd_zykd1sf044",  # 1SF044
            "1SF035专用口袋": "LZ_symdd_zykd035",  # 1SF035专用口袋
            "1SF006专用口袋": "LZ_symdd_sf006",  # 1SF006专用口袋
            "1SF012专用口袋": "LZ_symdd_1sf012zykd",  # 1SF012专用口袋
            "1SF019专用口袋": "LZ_symdd_1sf019md",  # 1SF019专用口袋
            "1SF014专用口袋": "LZ_symdd_1sf014zykd",  # 1SF014专用口袋
            "1SF024专用口袋": "LZ_symdd_1SF024",  # 1SF024专用口袋
            "1SF021专用口袋": "LZ_symdd_zymd",  # 1SF021专用口袋
            "1JAS03专用口袋": "LZ_symdd_jaszyd",  # 1JAS03专用口袋
            "同工艺书": "LZ_symdd_tgys",  # 同工艺书
        },
        "LZ_syxk": {
            "一扣": "LZ_syxk_xxyk",  # 一扣
            "平扣": "LZ_syxk_pk",  # 平扣
            "贴边": "LZ_syxk_tb",  # 贴边
            "叠扣": "LZ_syxk_dk",  # 叠扣
            "斜扣": "LZ_syxk_xk",  # 斜扣
            "斜眼叠扣": "LZ_syxk_xdk",  # 斜眼叠扣
            "斜眼平扣": "LZ_syxk_xpk",  # 斜眼平扣
            "袖克夫圆头": "LZ_syxk_xkfyt",  # 袖克夫圆头
            "袖克夫尖头": "LZ_syxk_xkfjt",  # 袖克夫尖头
        },
        "LZ_xc": {
            "无胸衬": "LZ_xc_wxc",  # 无胸衬
            "二层胸衬": "LZ_xc_ecxc",  # 二层胸衬
            "三层胸衬": "LZ_xc_scxc",  # 三层胸衬
            "四层胸衬": "LZ_xc_scxc4",  # 四层胸衬
            "五层胸衬": "LZ_xc_wcxc",  # 五层胸衬
        },
        "LZ_xksy": {
            "一扣": "LZ_xksy_1b",  # 一扣
            "二扣": "LZ_xksy_2b",  # 二扣
            "三扣": "LZ_xksy_3b",  # 三扣
            "四扣": "LZ_xksy_4B",  # 四扣
            "五扣": "LZ_xksy_5B",  # 五扣
            "六扣": "LZ_xksy_6B",  # 六扣
        },
        "LZ_xt": {
            "有袖弹": "LZ_xt_yxt",  # 有袖弹
            "袖弹一层棉": "LZ_xt_xtycm",  # 袖弹一层棉
            "无袖弹": "LZ_xt_wxt",  # 无袖弹
        },
        "LZ_xz": {
            "1SF035无袖里专用袖": "LZ_xz_1SF035wxlzyx",  # 1SF035无袖里专用袖
            "1SF035有袖里专用袖": "LZ_xz_1sf035wxl",  # 1SF035有袖里专用袖
            "A款袖克夫1扣": "LZ_xz_typec",  # A款袖克夫1扣
            "B款袖开叉1扣": "LZ_xz_typea",  # B款袖开叉1扣
            "C款无袖里袖克夫1扣": "LZ_xz_typeb",  # C款无袖里袖克夫1扣
            "D款无袖里开叉一扣": "LZ_xz_akwxl",  # D款无袖里开叉一扣
            "专用袖": "LZ_xz_zyx",  # 专用袖
        },
        "LZ_ydj": {
            "无垫肩": "LZ_ydj_wdj",  # 无垫肩
            "0.2cm": "LZ_ydj_0.2",  # 0.2cm
            "0.5cm": "LZ_ydj_0.5",  # 0.5cm
            "0.7cm": "LZ_ydj_0.7",  # 0.7cm
            "1cm": "LZ_ydj_1",  # 1cm
            "1.5cm": "LZ_ydj_1.5",  # 1.5cm
        },
        "LZ_zdj": {
            "无垫肩": "LZ_zdj_wdj",  # 无垫肩
            "0.2cm": "LZ_zdj_0.2",  # 0.2cm
            "0.5cm": "LZ_zdj_0.5",  # 0.5cm
            "0.7cm": "LZ_zdj_0.7",  # 0.7cm
            "1cm": "LZ_zdj_1",  # 1cm
            "1.5cm": "LZ_zdj_1.5",  # 1.5cm
        },
        "MJ_mjhx": {
            "中开叉": "MJ_mjhx_zkc",  # 中开叉
            "不开叉": "MJ_mjhx_bkc",  # 不开叉
            "侧开叉": "MJ_mjhx_ckx",  # 侧开叉
            "侧面和后中都开叉": "MJ_mjhx_czkc",  # 侧面和后中都开叉
        },
        "MJ_sjd": {
            "无": "MJ_sjd_wu",  # 无
            "直手巾袋": "MJ_sjd_zsjd",  # 直手巾袋
            "弧手巾袋": "MJ_sjd_hsjd",  # 弧手巾袋
            "弧形小明袋": "MJ_sjd_hxxmd",  # 弧形小明袋
            "上两直手巾袋": "MJ_sjd_slzsjd",  # 上两直手巾袋
            "专用明袋": "MJ_sjd_zymd",  # 专用明袋
        },
        "MJ_waistBack": {
            "里布": "MJ_waistBack_lb",  # 里布
            "本料": "MJ_waistBack_bl",  # 本料
        },
        "MJ_xkd": {
            "无": "MJ_xkd_wu",  # 无
            "双支线开袋": "MJ_xkd_szxkd",  # 双支线开袋
            "两斜袋盖": "MJ_xkd_lxdg",  # 两斜袋盖
            "下两明袋": "MJ_xkd_xlmd",  # 下两明袋
            "手巾袋": "MJ_xkd_sjd",  # 手巾袋
            "单支线开袋": "MJ_xkd_dzxkd",  # 单支线开袋
            "双支线加袋盖": "MJ_xkd_szxjdg",  # 双支线加袋盖
            "斜双支线开袋": "MJ_xkd_slantJetted",  # 斜双支线开袋
            "专用明袋": "MJ_xkd_zymd",  # 专用明袋
            "弧形手巾袋": "MJ_xkd_barchetta",  # 弧形手巾袋
        },
        "SY_craft": {
            "全麻衬": "SY_craft_qmc",  # 全麻衬
            "半麻衬": "SY_craft_bmc",  # 半麻衬
            "无结构": "SY_craft_wjg",  # 无结构
        },
        "SY_cuffKeyhole": {
            "一扣	": "SY_cuffKeyhole_oneButton",  # 一扣	
            "二扣	 ": "SY_cuffKeyhole_twoBuckles",  # 二扣	 
            "三扣": "SY_cuffKeyhole_threeBuckles",  # 三扣
            "四扣": "SY_cuffKeyhole_fourBuckles",  # 四扣
            "五扣": "SY_cuffKeyhole_fiveBuckles",  # 五扣
            "六扣": "SY_cuffKeyhole_6b",  # 六扣
        },
        "SY_curvedHandmadeColor": {
            "顺色": "SY_curvedHandmadeColor_matchFabric",  # 顺色
            "000": "SY_curvedHandmadeColor_000",  # 000
            "46": "SY_curvedHandmadeColor_46",  # 46
            "130": "SY_curvedHandmadeColor_130",  # 130
            "131": "SY_curvedHandmadeColor_131",  # 131
            "155": "SY_curvedHandmadeColor_155",  # 155
            "174": "SY_curvedHandmadeColor_174",  # 174
            "196": "SY_curvedHandmadeColor_196",  # 196
            "214": "SY_curvedHandmadeColor_214",  # 214
            "247": "SY_curvedHandmadeColor_247",  # 247
            "339": "SY_curvedHandmadeColor_339",  # 339
            "367": "SY_curvedHandmadeColor_367",  # 367
            "387": "SY_curvedHandmadeColor_387",  # 387
            "412": "SY_curvedHandmadeColor_412",  # 412
            "440": "SY_curvedHandmadeColor_440",  # 440
            "454": "SY_curvedHandmadeColor_454",  # 454
            "540": "SY_curvedHandmadeColor_540",  # 540
            "542": "SY_curvedHandmadeColor_542",  # 542
            "665": "SY_curvedHandmadeColor_665",  # 665
            "697": "SY_curvedHandmadeColor_697",  # 697
            "701": "SY_curvedHandmadeColor_701",  # 701
            "702": "SY_curvedHandmadeColor_702",  # 702
            "769": "SY_curvedHandmadeColor_769",  # 769
            "800": "SY_curvedHandmadeColor_800",  # 800
            "802": "SY_curvedHandmadeColor_802",  # 802
            "810": "SY_curvedHandmadeColor_810",  # 810
            "812": "SY_curvedHandmadeColor_812",  # 812
            "889": "SY_curvedHandmadeColor_889",  # 889
            "909": "SY_curvedHandmadeColor_909",  # 909
            "925": "SY_curvedHandmadeColor_925",  # 925
            "964": "SY_curvedHandmadeColor_964",  # 964
        },
        "SY_halfAMile": {
            "锁边翘边": "SY_halfAMile_lockingAndWarping",  # 锁边翘边
            "半里包边": "SY_halfAMile_halfMileEdging",  # 半里包边
        },
        "SY_halfMileLiningStyle": {
            "一字后里": "SY_halfMileLiningStyle_yzhl",  # 一字后里
            "交叉后里": "SY_halfMileLiningStyle_jxhl",  # 交叉后里
            "前全里后半里": "SY_halfMileLiningStyle_qqlhbl",  # 前全里后半里
        },
        "SY_jacketButtonhole": {
            "艾伦眼": "SY_jacketButtonhole_aly",  # 艾伦眼
            "机器锁眼": "SY_jacketButtonhole_jqsy",  # 机器锁眼
            "手工米兰眼": "SY_jacketButtonhole_sgmly",  # 手工米兰眼
            "不开口手工米兰眼": "SY_jacketButtonhole_bkksgmly",  # 不开口手工米兰眼
            "取消驳头锁眼": "SY_jacketButtonhole_qxbtsy",  # 取消驳头锁眼
            "圆头锁眼": "SY_jacketButtonhole_ytsy",  # 圆头锁眼
            "手工圆头锁眼": "SY_jacketButtonhole_qxytsy",  # 手工圆头锁眼
            "双边米兰眼": "SY_jacketButtonhole_sbmly",  # 双边米兰眼
            "手工圆头1.5cm圆头锁眼": "SY_jacketButtonhole_sgytsy1.5",  # 手工圆头1.5cm圆头锁眼
            "手工圆头2cm圆头锁眼": "SY_jacketButtonhole_sgytsy2",  # 手工圆头2cm圆头锁眼
            "双边手工圆头锁眼": "SY_jacketButtonhole_sbsgytsy",  # 双边手工圆头锁眼
        },
        "SY_jacketButtonholeColor": {
            "顺色": "SY_jacketButtonholeColor_matchFabric",  # 顺色
            "000": "SY_jacketButtonholeColor_000",  # 000
            "46": "SY_jacketButtonholeColor_46",  # 46
            "130": "SY_jacketButtonholeColor_130",  # 130
            "131": "SY_jacketButtonholeColor_131",  # 131
            "155": "SY_jacketButtonholeColor_155",  # 155
            "174": "SY_jacketButtonholeColor_174",  # 174
            "196": "SY_jacketButtonholeColor_196",  # 196
            "214": "SY_jacketButtonholeColor_214",  # 214
            "247": "SY_jacketButtonholeColor_247",  # 247
            "310": "SY_jacketButtonholeColor_310",  # 310
            "339": "SY_jacketButtonholeColor_339",  # 339
            "367": "SY_jacketButtonholeColor_367",  # 367
            "387": "SY_jacketButtonholeColor_387",  # 387
            "412": "SY_jacketButtonholeColor_412",  # 412
            "440": "SY_jacketButtonholeColor_440",  # 440
            "454": "SY_jacketButtonholeColor_454",  # 454
            "540": "SY_jacketButtonholeColor_540",  # 540
            "542": "SY_jacketButtonholeColor_542",  # 542
            "665": "SY_jacketButtonholeColor_665",  # 665
            "697": "SY_jacketButtonholeColor_697",  # 697
            "701": "SY_jacketButtonholeColor_701",  # 701
            "702": "SY_jacketButtonholeColor_702",  # 702
            "707": "SY_jacketButtonholeColor_707",  # 707
            "769": "SY_jacketButtonholeColor_769",  # 769
            "800": "SY_jacketButtonholeColor_800",  # 800
            "802": "SY_jacketButtonholeColor_802",  # 802
            "810": "SY_jacketButtonholeColor_810",  # 810
            "812": "SY_jacketButtonholeColor_812",  # 812
            "889": "SY_jacketButtonholeColor_889",  # 889
            "909": "SY_jacketButtonholeColor_909",  # 909
            "925": "SY_jacketButtonholeColor_925",  # 925
            "964": "SY_jacketButtonholeColor_964",  # 964
        },
        "SY_jacketChestLining": {
            "无胸衬": "SY_jacketChestLining_wxc",  # 无胸衬
            "一层胸衬": "SY_jacketChestLining_ycxc",  # 一层胸衬
            "二层胸衬": "SY_jacketChestLining_ecxc",  # 二层胸衬
            "三层胸衬": "SY_jacketChestLining_threeLayerChestLining",  # 三层胸衬
            "四层胸衬": "SY_jacketChestLining_scxc",  # 四层胸衬
            "五层胸衬": "SY_jacketChestLining_fiveLayerChestLining",  # 五层胸衬
        },
        "SY_jacketPockets": {
            "无": "SY_jacketPockets_wu",  # 无
            "A款 两直袋盖": "SY_jacketPockets_gd",  # A款 两直袋盖
            "B款 两明袋": "SY_jacketPockets_md",  # B款 两明袋
            "C款 双支线": "SY_jacketPockets_szx",  # C款 双支线
            "D款 两弧形明袋": "SY_jacketPockets_lhxmd",  # D款 两弧形明袋
            "E款 两明袋加袋盖": "SY_jacketPockets_mdjgd",  # E款 两明袋加袋盖
            "F款 下三明袋": "SY_jacketPockets_xsmd",  # F款 下三明袋
            "G款 下三双支线": "SY_jacketPockets_xszx",  # G款 下三双支线
            "H款 两弧形双支线袋": "SY_jacketPockets_hklhxszxd",  # H款 两弧形双支线袋
            "I款 酒杯明袋": "SY_jacketPockets_jbmd",  # I款 酒杯明袋
            "J款 水滴明袋": "SY_jacketPockets_sdmd",  # J款 水滴明袋
            "K款 三直袋盖": "SY_jacketPockets_sxdg",  # K款 三直袋盖
            "L款 两斜袋盖": "SY_jacketPockets_lxdg",  # L款 两斜袋盖
            "M款 两斜双支线袋": "SY_jacketPockets_lxszxd",  # M款 两斜双支线袋
            "N款 三斜袋盖": "SY_jacketPockets_tripleInclinedBagCover",  # N款 三斜袋盖
            "O款 三弧形明袋": "SY_jacketPockets_xshxmd",  # O款 三弧形明袋
            "P款 两袋盖加小双支线": "SY_jacketPockets_xldgjszx",  # P款 两袋盖加小双支线
            "Q款 圆角打褶明袋加直袋盖": "SY_jacketPockets_yjdzmdjzdg",  # Q款 圆角打褶明袋加直袋盖
            "R款 打褶直角明袋加袋盖": "SY_jacketPockets_dzzjmdjgd",  # R款 打褶直角明袋加袋盖
            "S款 梯型袋盖加打褶明袋": "SY_jacketPockets_txdgjdzmd",  # S款 梯型袋盖加打褶明袋
            "T款 圆角风琴袋加袋盖": "SY_jacketPockets_yjfqzjgd",  # T款 圆角风琴袋加袋盖
            "U款 立体明袋加袋盖": "SY_jacketPockets_ltmdjgd",  # U款 立体明袋加袋盖
            "V款 圆角打褶明袋加斜袋盖": "SY_jacketPockets_yjdzmdjxdg",  # V款 圆角打褶明袋加斜袋盖
            "W款 单支线": "SY_jacketPockets_dzx",  # W款 单支线
            "X款 下三水滴明袋": "SY_jacketPockets_xssdmd",  # X款 下三水滴明袋
            "Y款 圆角打褶明袋": "SY_jacketPockets_yjdzmd",  # Y款 圆角打褶明袋
            "Z款 直角打褶明袋": "SY_jacketPockets_zjdzmd",  # Z款 直角打褶明袋
            "AA款 立体直角明袋加直角袋盖": "SY_jacketPockets_ltzjmdjzjdg",  # AA款 立体直角明袋加直角袋盖
            "AB款 切角拼接明袋": "SY_jacketPockets_abkqjpjmd",  # AB款 切角拼接明袋
            "AC款 切角拼接三明袋": "SY_jacketPockets_ackqjpjsmd",  # AC款 切角拼接三明袋
            "AD款": "SY_jacketPockets_aekkd",  # AD款
            "AE款 风琴袋": "SY_jacketPockets_fqd",  # AE款 风琴袋
            "AF款 三斜双支线袋": "SY_jacketPockets_SlidePocketJetted",  # AF款 三斜双支线袋
            "AG款 上口压线两明袋": "SY_jacketPockets_agskyxlmd",  # AG款 上口压线两明袋
            "AH款 斜插袋": "SY_jacketPockets_xcd",  # AH款 斜插袋
            "AI款": "SY_jacketPockets_ahkkd",  # AI款
            "AJ款 单支线袋盖": "SY_jacketPockets_singleBranchBagCover",  # AJ款 单支线袋盖
            "AK下三明袋": "SY_jacketPockets_akxsmd",  # AK下三明袋
            "AK专用打褶明袋": "SY_jacketPockets_dzmd",  # AK专用打褶明袋
            "AK款 明袋": "SY_jacketPockets_akmd",  # AK款 明袋
            "AL款 两斜袋盖加斜双支线": "SY_jacketPockets_xlxdgjxszx",  # AL款 两斜袋盖加斜双支线
            "AM款 弧形明袋加袋盖": "SY_jacketPockets_amkhxlmdjdg",  # AM款 弧形明袋加袋盖
            "AN款": "SY_jacketPockets_ank",  # AN款
            "AO款 两袋盖加小单支线袋": "SY_jacketPockets_aokldgjxdzxq",  # AO款 两袋盖加小单支线袋
            "AP款 斜单支线袋": "SY_jacketPockets_apkxszxd",  # AP款 斜单支线袋
            "月牙双支线": "SY_jacketPockets_yyszx",  # 月牙双支线
            "MM款": "SY_jacketPockets_MM",  # MM款
            "1SF012专用口袋": "SY_jacketPockets_zykd",  # 1SF012专用口袋
            "专用袋": "SY_jacketPockets_zyd",  # 专用袋
            "MK": "SY_jacketPockets_mk",  # MK
            "省道隐形拉链插袋": "SY_jacketPockets_sdyxlld",  # 省道隐形拉链插袋
            "前侧缝插袋": "SY_jacketPockets_qcfxd",  # 前侧缝插袋
        },
        "SY_jacketShoulderPads": {
            "无垫肩": "SY_jacketShoulderPads_wdk",  # 无垫肩
            "0.2cm": "SY_jacketShoulderPads_0.2",  # 0.2cm
            "0.5cm": "SY_jacketShoulderPads_0.5",  # 0.5cm
            "0.7cm": "SY_jacketShoulderPads_0.7",  # 0.7cm
            "1cm": "SY_jacketShoulderPads_1",  # 1cm
            "1.5cm": "SY_jacketShoulderPads_1.5",  # 1.5cm
            "2cm硬的": "SY_jacketShoulderPads_2yd",  # 2cm硬的
            "2cm": "SY_jacketShoulderPads_2",  # 2cm
        },
        "SY_jacketSleeveButton": {
            "贴边": "SY_jacketSleeveButton_tb",  # 贴边
            "叠扣": "SY_jacketSleeveButton_dk",  # 叠扣
            "斜眼叠扣": "SY_jacketSleeveButton_slantBuckle",  # 斜眼叠扣
            "斜扣": "SY_jacketSleeveButton_diagonalBuckle",  # 斜扣
            "平扣": "SY_jacketSleeveButton_pk",  # 平扣
            "袖克夫圆头": "SY_jacketSleeveButton_xfkjt",  # 袖克夫圆头
            "袖克夫尖头": "SY_jacketSleeveButton_xkf",  # 袖克夫尖头
            "斜眼平扣": "SY_jacketSleeveButton_xpk",  # 斜眼平扣
        },
        "SY_jacketSleeveType": {
            "正常袖": "SY_jacketSleeveType_normal",  # 正常袖
            "自然肩": "SY_jacketSleeveType_naturalShoulder",  # 自然肩
            "衬衫肩": "SY_jacketSleeveType_shirtShoulder",  # 衬衫肩
            "KN翘袖": "SY_jacketSleeveType_knqx",  # KN翘袖
            "衬衫肩+反上肩": "SY_jacketSleeveType_csjfsj",  # 衬衫肩+反上肩
            "自然肩+反上肩": "SY_jacketSleeveType_fsj",  # 自然肩+反上肩
            "无袖里自然肩": "SY_jacketSleeveType_wxlzrj",  # 无袖里自然肩
            "无袖里衬衫肩": "SY_jacketSleeveType_wxlcsj",  # 无袖里衬衫肩
            "斜袖一扣自然肩": "SY_jacketSleeveType_xxykzrj",  # 斜袖一扣自然肩
            "斜袖一扣正常袖": "SY_jacketSleeveType_xxyk",  # 斜袖一扣正常袖
            "AK溜肩袖": "SY_jacketSleeveType_ljx",  # AK溜肩袖
            "AK翘袖": "SY_jacketSleeveType_akqjsc",  # AK翘袖
            "无袖里袖山分缝": "SY_jacketSleeveType_wxlxsff",  # 无袖里袖山分缝
            "专用袖": "SY_jacketSleeveType_zyx",  # 专用袖
            "AK无袖里自然肩": "SY_jacketSleeveType_akwxlzrj",  # AK无袖里自然肩
            "斜三角袖正常袖": "SY_jacketSleeveType_xsjx",  # 斜三角袖正常袖
            "斜三角袖自然肩": "SY_jacketSleeveType_xsjxzrj",  # 斜三角袖自然肩
            "瑞典自然袖": "SY_jacketSleeveType_rdzrx",  # 瑞典自然袖
            "TF翘袖": "SY_jacketSleeveType_tfqx",  # TF翘袖
            "袖山分缝": "SY_jacketSleeveType_xsff",  # 袖山分缝
        },
        "SY_jacketTowelBag": {
            "无": "SY_jacketTowelBag_wu",  # 无
            "A款 弧手巾袋": "SY_jacketTowelBag_hxsjd",  # A款 弧手巾袋
            "B款 直手巾袋": "SY_jacketTowelBag_zxsjd",  # B款 直手巾袋
            "C款 小明袋": "SY_jacketTowelBag_xmd",  # C款 小明袋
            "D款 弧形小明袋": "SY_jacketTowelBag_md",  # D款 弧形小明袋
            "E款 小酒杯明袋": "SY_jacketTowelBag_xjbmd",  # E款 小酒杯明袋
            "F款 两个打褶圆角明袋加袋盖": "SY_jacketTowelBag_dzyjmdjdg",  # F款 两个打褶圆角明袋加袋盖
            "G款 两个打褶直角明袋加袋盖": "SY_jacketTowelBag_dzmdjdg",  # G款 两个打褶直角明袋加袋盖
            "H款 两个圆角打褶明袋加斜袋盖": "SY_jacketTowelBag_lgyjdzmdjxdg",  # H款 两个圆角打褶明袋加斜袋盖
            "I款 圆角拼接两明袋": "SY_jacketTowelBag_yjpjmd",  # I款 圆角拼接两明袋
            "J款 小水滴明袋": "SY_jacketTowelBag_xsdmd",  # J款 小水滴明袋
            "L款 双支线袋": "SY_jacketTowelBag_lkszxd",  # L款 双支线袋
            "K款 弧形小明袋加袋盖": "SY_jacketTowelBag_kkhxxmdjdg",  # K款 弧形小明袋加袋盖
            "M款": "SY_jacketTowelBag_mk",  # M款
            "AK小明袋": "SY_jacketTowelBag_akxmd",  # AK小明袋
            "AK弧手巾袋": "SY_jacketTowelBag_aksjd",  # AK弧手巾袋
            "猎装手巾袋": "SY_jacketTowelBag_lzsjd",  # 猎装手巾袋
            "可抽拉手巾袋": "SY_jacketTowelBag_kclsjd",  # 可抽拉手巾袋
            "圆角打褶明袋": "SY_jacketTowelBag_yjdzmdbag",  # 圆角打褶明袋
            "MG口袋": "SY_jacketTowelBag_mgkd",  # MG口袋
            "AK专用打褶明袋": "SY_jacketTowelBag_dzmd",  # AK专用打褶明袋
            "1KN333专用明袋": "SY_jacketTowelBag_zymd",  # 1KN333专用明袋
            "一个圆角打褶明袋加斜袋盖": "SY_jacketTowelBag_yjdzmd",  # 一个圆角打褶明袋加斜袋盖
            "明袋加袋盖": "SY_jacketTowelBag_mdjdg",  # 明袋加袋盖
            "AK 打褶明袋加斜袋盖": "SY_jacketTowelBag_akdzmdjxdg",  # AK 打褶明袋加斜袋盖
            "SM": "SY_jacketTowelBag_smkd",  # SM
            "SK": "SY_jacketTowelBag_sk",  # SK
        },
        "SY_jacketVent": {
            "双开叉": "SY_jacketVent_doubleFork",  # 双开叉
            "中开叉": "SY_jacketVent_singleFork",  # 中开叉
            "不开叉": "SY_jacketVent_notForked",  # 不开叉
        },
        "SY_placketKeyhole": {
            "一扣半": "SY_placketKeyhole_1.5b",  # 一扣半
            "一扣": "SY_placketKeyhole_oneButton ",  # 一扣
            "二扣一": "SY_placketKeyhole_erkouyi",  # 二扣一
            "二扣	": "SY_placketKeyhole_twoBuckles",  # 二扣	
            "两扣半": "SY_placketKeyhole_twoAndAHalfButtons",  # 两扣半
            "三扣半": "SY_placketKeyhole_skb",  # 三扣半
            "三扣": "SY_placketKeyhole_sankou",  # 三扣
            "三扣二": "SY_placketKeyhole_ske",  # 三扣二
            "四暗扣": "SY_placketKeyhole_sak",  # 四暗扣
            "四扣": "SY_placketKeyhole_sk",  # 四扣
            "四扣二": "SY_placketKeyhole_fourBucklesAndWwo",  # 四扣二
            "四扣一": "SY_placketKeyhole_fourBucklesAndone",  # 四扣一
            "五扣": "SY_placketKeyhole_wlk",  # 五扣
            "六扣": "SY_placketKeyhole_mjsy6k",  # 六扣
            "六扣三": "SY_placketKeyhole_6bno3",  # 六扣三
            "六扣二": "SY_placketKeyhole_sixBucklesAndTwo	",  # 六扣二
            "六扣一": "SY_placketKeyhole_sixBucklesAndOne",  # 六扣一
            "八扣三": "SY_placketKeyhole_bks",  # 八扣三
            "对扣": "SY_placketKeyhole_mjsydk",  # 对扣
        },
        "SY_safariSuit": {
            "腰带款": "SY_safariSuit_beltStyle",  # 腰带款
            "抽绳款": "SY_safariSuit_pullOutPayment",  # 抽绳款
        },
        "SY_sleeveElastic": {
            "袖弹一层棉": "SY_sleeveElastic_sleevePlaysALayerOfCotton",  # 袖弹一层棉
            "有袖弹": "SY_sleeveElastic_sleevedBullet",  # 有袖弹
            "无袖弹": "SY_sleeveElastic_wxt",  # 无袖弹
            "一层黑炭": "SY_sleeveElastic_ycht",  # 一层黑炭
        },
        "SY_ydj": {
            "无垫肩": "SY_ydj_wdj",  # 无垫肩
            "0.2cm": "SY_ydj_0.2",  # 0.2cm
            "0.5cm": "SY_ydj_0.5",  # 0.5cm
            "0.7cm": "SY_ydj_0.7cm",  # 0.7cm
            "1cm": "SY_ydj_1cm",  # 1cm
            "1.5cm": "SY_ydj_1.5cm",  # 1.5cm
            "2cm": "SY_ydj_2",  # 2cm
            "2cm硬的": "SY_ydj_2y",  # 2cm硬的
        },
        "XK_Slide": {
            "2": "XK_Slide_2",  # 2
            "3": "XK_Slide_pqs",  # 3
            "4": "XK_Slide_4",  # 4
            "5": "XK_Slide_5",  # 5
            "6": "XK_Slide_6",  # 6
        },
        "XK_curvedHem": {
            "是": "XK_curvedHem_1",  # 是
        },
        "XK_footOpeningReversed": {
            "2": "XK_footOpeningReversed_2",  # 2
            "3.5": "XK_footOpeningReversed_3.5",  # 3.5
            "3": "XK_footOpeningReversed_3",  # 3
            "4.5": "XK_footOpeningReversed_4.5",  # 4.5
            "4": "XK_footOpeningReversed_4",  # 4
            "5": "XK_footOpeningReversed_5",  # 5
            "6": "XK_footOpeningReversed_6",  # 6
        },
        "XK_hemOpening": {
            "平撬": "XK_hemOpening_pq",  # 平撬
            "反撬": "XK_hemOpening_fq",  # 反撬
            "斜裤脚": "XK_hemOpening_diagonalHem",  # 斜裤脚
            "松紧拉链": "XK_hemOpening_elasticZipper",  # 松紧拉链
            "裤子毛长": "XK_hemOpening_mc",  # 裤子毛长
            "同工艺书": "XK_hemOpening_ptys",  # 同工艺书
        },
        "XK_jkjzd": {
            "织带": "XK_jkjzd_you",  # 织带
            "无": "XK_jkjzd_wu",  # 无
            "本料": "XK_jkjzd_fabric",  # 本料
            "面料布边织带": "XK_jkjzd_mlbbzd",  # 面料布边织带
        },
        "XK_jkyx": {
            "4": "XK_jkyx_4",  # 4
        },
        "XK_pantBackPocket": {
            "双支线": "XK_pantBackPocket_szx",  # 双支线
            "单支线": "XK_pantBackPocket_dzx",  # 单支线
            "双支线加袋盖": "XK_pantBackPocket_dg",  # 双支线加袋盖
            "双支线口袋，口袋锁眼取消": "XK_pantBackPocket_szxkd",  # 双支线口袋，口袋锁眼取消
            "后袋取消": "XK_pantBackPocket_hdqx",  # 后袋取消
            "明袋": "XK_pantBackPocket_md",  # 明袋
            "后口袋锁眼取消": "XK_pantBackPocket_hdsyqx",  # 后口袋锁眼取消
            "右边单口袋": "XK_pantBackPocket_ybdkd",  # 右边单口袋
            "牛仔袋": "XK_pantBackPocket_nzd",  # 牛仔袋
            "同工艺书": "XK_pantBackPocket_tgys",  # 同工艺书
        },
        "XK_pantFrontFly": {
            "拉链": "XK_pantFrontFly_ll",  # 拉链
            "纽扣": "XK_pantFrontFly_nk",  # 纽扣
        },
        "XK_pantsPocket": {
            "普通表袋": "XK_pantsPocket_ptbd",  # 普通表袋
            "袋盖": "XK_pantsPocket_dg",  # 袋盖
            "无表袋": "XK_pantsPocket_wbd",  # 无表袋
            "表袋袢": "XK_pantsPocket_bdp",  # 表袋袢
        },
        "XK_strapBuckle": {
            "无": "XK_strapBuckle_notHave",  # 无
            "有": "XK_strapBuckle_have",  # 有
        },
        "XK_trouserFrontPockets": {
            "直插袋": "XK_trouserFrontPockets_straightPocket",  # 直插袋
            "斜插袋": "XK_trouserFrontPockets_xcd",  # 斜插袋
            "牛仔袋": "XK_trouserFrontPockets_nzd",  # 牛仔袋
            "弧形斜插袋": "XK_trouserFrontPockets_hxxcd",  # 弧形斜插袋
            "双支线袋": "XK_trouserFrontPockets_szxd",  # 双支线袋
            "单支线": "XK_trouserFrontPockets_dzx",  # 单支线
            "斜插拉链袋": "XK_trouserFrontPockets_xclld",  # 斜插拉链袋
            "直插拉链袋": "XK_trouserFrontPockets_zclld",  # 直插拉链袋
            "侧缝隐形拉链袋": "XK_trouserFrontPockets_cfyxldd",  # 侧缝隐形拉链袋
        },
        "XK_waistStyle": {
            "裤袢": "XK_waistStyle_kp",  # 裤袢
            "腰袢": "XK_waistStyle_yp",  # 腰袢
            "松紧": "XK_waistStyle_sj",  # 松紧
            "后中开叉": "XK_waistStyle_hzkc",  # 后中开叉
            "后中开叉两侧松紧": "XK_waistStyle_hzkclcsj",  # 后中开叉两侧松紧
            "不开叉两侧松紧": "XK_waistStyle_bkc",  # 不开叉两侧松紧
            "连腰": "XK_waistStyle_lyk",  # 连腰
            "全松紧": "XK_waistStyle_qsj",  # 全松紧
            "裤袢+腰袢": "XK_waistStyle_kpjyp",  # 裤袢+腰袢
        },
        "XK_yks": {
            "A款:腰头长5CM，腰面宽3.5CM": "XK_yks_ak",  # A款:腰头长5CM，腰面宽3.5CM
            "B款:腰头长12CM，腰面宽5CM": "XK_yks_bkym",  # B款:腰头长12CM，腰面宽5CM
            "C款:无宝剑头，腰面宽3.5CM": "XK_yks_ckym",  # C款:无宝剑头，腰面宽3.5CM
            "D款:腰头长22CM，腰面宽3.5CM": "XK_yks_dkym",  # D款:腰头长22CM，腰面宽3.5CM
            "E款:腰头长26CM，腰面宽5CM": "XK_yks_ekym",  # E款:腰头长26CM，腰面宽5CM
            "F款:交叉腰，腰头长25CM 腰面宽6CM": "XK_yks_fkym",  # F款:交叉腰，腰头长25CM 腰面宽6CM
            "G款:腰头长6CM，腰面宽3.5CM": "XK_yks_gkym",  # G款:腰头长6CM，腰面宽3.5CM
            "H款:腰头长12CM，腰面款3.5CM": "XK_yks_hkym",  # H款:腰头长12CM，腰面款3.5CM
            "I款:腰头长12CM，腰宽3.5CM": "XK_yks_ikym",  # I款:腰头长12CM，腰宽3.5CM
            "J款:双宝剑头，腰宽6CM": "XK_yks_jkym",  # J款:双宝剑头，腰宽6CM
            "K款:双宝剑头，双扣袢，腰宽6CM": "XK_yks_kkym",  # K款:双宝剑头，双扣袢，腰宽6CM
            "L款:腰头长11CM，腰宽5CM": "XK_yks_lkym",  # L款:腰头长11CM，腰宽5CM
            "M款:腰头长10CM，腰宽3.5CM": "XK_yks_mkym",  # M款:腰头长10CM，腰宽3.5CM
            "P款:腰头长26CM，腰宽5CM": "XK_yks_pkym",  # P款:腰头长26CM，腰宽5CM
            "Q款:腰头长14CM，腰宽4CM": "XK_yks_qkym",  # Q款:腰头长14CM，腰宽4CM
            "S款:腰头长5CM，腰宽4CM": "XK_yks_skym",  # S款:腰头长5CM，腰宽4CM
            "T款:腰头长16CM，腰宽5CM": "XK_yks_tkym",  # T款:腰头长16CM，腰宽5CM
            "U款:腰头长25CM，腰宽6CM": "XK_yks_ukym",  # U款:腰头长25CM，腰宽6CM
            "V款:腰袢，腰头长14CM，腰头处加一个裤袢，腰面宽5CM": "XK_yks_rdy",  # V款:腰袢，腰头长14CM，腰头处加一个裤袢，腰面宽5CM
            "W款：腰袢，长7公分三角宝剑头，腰宽3.5CM": "XK_yks_rdak",  # W款：腰袢，长7公分三角宝剑头，腰宽3.5CM
            "X款：腰袢，长12公分三角宝剑头，腰头处加一个裤袢，腰宽3.5CM": "XK_yks_rdyak",  # X款：腰袢，长12公分三角宝剑头，腰头处加一个裤袢，腰宽3.5CM
            "Y款：腰头长12CM，腰面宽5CM": "XK_yks_YK",  # Y款：腰头长12CM，腰面宽5CM
            "Z款：腰头长15CM，腰面宽3.5CM": "XK_yks_zk",  # Z款：腰头长15CM，腰面宽3.5CM
            "AB款：腰面宽4CM;加腰带款": "XK_yks_aby",  # AB款：腰面宽4CM;加腰带款
            "AC款:无宝剑头，腰面宽4.5CM": "XK_yks_ackwbjt",  # AC款:无宝剑头，腰面宽4.5CM
            "AD款：无宝剑头，腰面宽5CM": "XK_yks_adkwbjt",  # AD款：无宝剑头，腰面宽5CM
            "AE款:宝剑头长14CM，腰面宽4.5CM": "XK_yks_aek",  # AE款:宝剑头长14CM，腰面宽4.5CM
            "AF款：无宝剑头，腰面宽3.5CM": "XK_yks_afk",  # AF款：无宝剑头，腰面宽3.5CM
            "AG款：无宝剑头，腰面宽4CM": "XK_yks_agk",  # AG款：无宝剑头，腰面宽4CM
            "AH款:交叉腰，宝剑头长28CM 腰面宽7CM": "XK_yks_ah",  # AH款:交叉腰，宝剑头长28CM 腰面宽7CM
            "AI款：宝剑头长15CM，腰面宽4CM": "XK_yks_aik",  # AI款：宝剑头长15CM，腰面宽4CM
            "AJ款:宝剑头长5CM，腰面宽3.5CM": "XK_yks_ajkyt",  # AJ款:宝剑头长5CM，腰面宽3.5CM
            "两侧松紧腰": "XK_yks_lcsjy",  # 两侧松紧腰
            "专用腰": "XK_yks_zyy",  # 专用腰
            "无腰款": "XK_yks_wyk",  # 无腰款
            "全松紧腰": "XK_yks_wsjy",  # 全松紧腰
            "活动腰": "XK_yks_hdy",  # 活动腰
        },
    }
    
    def map_custom_option(field_key, value):
        """根据字段名和输入值，返回映射后的系统值"""
        if field_key in custom_option_mappings:
            mappings = custom_option_mappings[field_key]
            # 如果完全匹配映射表中的键，直接返回映射值
            if value in mappings:
                return mappings[value]
            # 如果部分匹配（如用户输入"B款"，查找以"B款 "开头的键）
            for key in mappings:
                if key.startswith(value + " "):
                    return mappings[key]
            # 如果部分匹配（如用户输入"B款"，查找以"B款:"开头的键）
            for key in mappings:
                if key.startswith(value + ":"):
                    return mappings[key]
            # 如果部分匹配（如用户输入"B款 两明袋"已经是完整值），保持原值
        return value
    
    # 工艺
    craft_match = re.search(r'工艺' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if craft_match:
        sy_attr["SY_craft"] = map_custom_option("SY_craft", craft_match.group(1).strip())
    
    # 后叉/开叉
    vent_match = re.search(r'上衣后叉' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not vent_match:
        vent_match = re.search(r'开叉' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if vent_match:
        sy_attr["SY_jacketVent"] = map_custom_option("SY_jacketVent", vent_match.group(1).strip())
    
    # 手巾袋（支持中文和字母）
    towel_bag_match = re.search(r'手巾袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if towel_bag_match:
        sy_attr["SY_jacketTowelBag"] = map_custom_option("SY_jacketTowelBag", towel_bag_match.group(1).strip())
    
    # 面大袋（支持中文和字母）
    pocket_match = re.search(r'上衣面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if not pocket_match:
        pocket_match = re.search(r'面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if pocket_match:
        sy_attr["SY_jacketPockets"] = map_custom_option("SY_jacketPockets", pocket_match.group(1).strip())
    
    # 袖口锁眼
    buttonhole_match = re.search(r'袖口锁眼' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if buttonhole_match:
        sy_attr["SY_jacketButtonhole"] = buttonhole_match.group(1).strip()
    
    # 袖扣
    sleeve_button_match = re.search(r'上衣袖扣' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not sleeve_button_match:
        sleeve_button_match = re.search(r'袖扣' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if sleeve_button_match:
        sy_attr["SY_jacketSleeveButton"] = sleeve_button_match.group(1).strip()
    
    # 袖子/肩型
    sleeve_type_match = re.search(r'上衣袖子' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not sleeve_type_match:
        sleeve_type_match = re.search(r'袖子' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if sleeve_type_match:
        sy_attr["SY_jacketSleeveType"] = sleeve_type_match.group(1).strip()
    
    # 袖弹
    elastic_match = re.search(r'袖弹' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if elastic_match:
        sy_attr["SY_sleeveElastic"] = map_custom_option("SY_sleeveElastic", elastic_match.group(1).strip())
    
    # 胸衬
    chest_lining_match = re.search(r'胸衬' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if chest_lining_match:
        sy_attr["SY_jacketChestLining"] = chest_lining_match.group(1).strip()
    
    # 右垫肩（支持数字和文字描述）
    shoulder_pad_match = re.search(r'右垫肩' + modify_words + r'([\d.]+cm)', text)
    if not shoulder_pad_match:
        shoulder_pad_match = re.search(r'右垫肩' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if shoulder_pad_match:
        value = shoulder_pad_match.group(1).strip()
        # 如果是数字描述（如0.5cm），保持原值；否则使用映射
        if not re.match(r'[\d.]+cm', value):
            value = map_custom_option("SY_ydj", value)
        sy_attr["SY_ydj"] = value
    
    # 左垫肩
    left_shoulder_pad_match = re.search(r'左垫肩' + modify_words + r'([\d.]+cm)', text)
    if not left_shoulder_pad_match:
        left_shoulder_pad_match = re.search(r'左垫肩' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if left_shoulder_pad_match:
        value = left_shoulder_pad_match.group(1).strip()
        # 如果是数字描述（如0.5cm），保持原值；否则使用映射
        if not re.match(r'[\d.]+cm', value):
            value = map_custom_option("SY_jacketShoulderPads", value)
        sy_attr["SY_jacketShoulderPads"] = value
    
    # 驳头锁眼
    lapel_buttonhole_match = re.search(r'驳头锁眼' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if lapel_buttonhole_match:
        sy_attr["SY_jacketButtonhole"] = map_custom_option("SY_jacketButtonhole", lapel_buttonhole_match.group(1).strip())
    
    # 米兰眼颜色
    milan_eye_color_match = re.search(r'米兰眼颜色' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if milan_eye_color_match:
        sy_attr["SY_jacketButtonholeColor"] = map_custom_option("SY_jacketButtonholeColor", milan_eye_color_match.group(1).strip())
    
    # 半里
    half_lining_match = re.search(r'半里' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if half_lining_match:
        sy_attr["SY_halfLining"] = map_custom_option("SY_halfAMile", half_lining_match.group(1).strip())
    
    # 半里里布风格
    half_lining_style_match = re.search(r'半里里布风格' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if half_lining_style_match:
        sy_attr["SY_halfMileLiningStyle"] = map_custom_option("SY_halfMileLiningStyle", half_lining_style_match.group(1).strip())
    
    # 手工套结
    if "手工套结" in text:
        result["orderRemarks"] = "手工套结"
    
    # 提取大衣定制选项
    dy_attr = {}
    
    # 大衣面大袋
    dy_pocket_match = re.search(r'面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if dy_pocket_match:
        dy_attr["DY_coatPockets"] = dy_pocket_match.group(1).strip()
    
    # 提取贡针（门襟贡针）
    placket_needle_match = re.search(r'贡针([\d.]+cm)', text)
    placket_needle = placket_needle_match.group(1).strip() if placket_needle_match else ""
    
    # 提取西裤定制选项
    xk_attr = {}
    xk_net_size = {}
    
    # 全臀围（支持多种表达方式）
    hip_match = re.search(r'西裤全臀围[做做到](\d+)', text)
    if not hip_match:
        hip_match = re.search(r'全臀围[做做到](\d+)', text)
    if not hip_match:
        hip_match = re.search(r'全臀围[\u4e00-\u9fa5]*(\d+)', text)
    if hip_match:
        xk_net_size["fullHipWidth"] = int(hip_match.group(1))
    
    # 脚口（支持中文和字母）
    hem_match = re.search(r'脚口' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    is_hem_fanqiao = False
    if hem_match:
        hem_value = hem_match.group(1).strip()
        mapped_hem = map_custom_option("XK_hemOpening", hem_value)
        xk_attr["XK_hemOpening"] = mapped_hem
        # 判断是否为反撬
        if mapped_hem == "XK_hemOpening_fq" or "反撬" in hem_value:
            is_hem_fanqiao = True
    
    # 脚口反撬数值（如：脚口反撬改5，脚口反撬改3.5）
    hem_value_match = re.search(r'脚口反撬' + modify_words + r'([\d.]+)', text)
    if hem_value_match and (is_hem_fanqiao or (xk_attr.get("XK_hemOpening") == "XK_hemOpening_fq")):
        xk_attr["XK_footOpeningReversed"] = hem_value_match.group(1).strip()
    
    # 腰款式（支持字母）
    waist_style_match = re.search(r'腰款式' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    if not waist_style_match:
        waist_style_match = re.search(r'腰款' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    if waist_style_match:
        mapped_value = map_custom_option("XK_yks", waist_style_match.group(1).strip())
        xk_attr["XK_pantsWaistStyle"] = mapped_value
        xk_attr["XK_yks"] = mapped_value
    
    # 裤腰样式
    waist_strap_match = re.search(r'裤腰样式' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    if waist_strap_match:
        xk_attr["XK_waistStyle"] = map_custom_option("XK_waistStyle", waist_strap_match.group(1).strip())
    
    # 前口袋
    front_pocket_match = re.search(r'裤子前口袋' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not front_pocket_match:
        front_pocket_match = re.search(r'前口袋' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if front_pocket_match:
        xk_attr["XK_trouserFrontPockets"] = map_custom_option("XK_trouserFrontPockets", front_pocket_match.group(1).strip())
    
    # 手巾袋（用于西裤）
    towel_bag_xk_match = re.search(r'西裤手巾袋' + modify_words + r'([\u4e00-\u9fa5\s]+?)(?=、|，|$)', text)
    if towel_bag_xk_match:
        xk_attr["XK_pantsPocket"] = towel_bag_xk_match.group(1).strip()
    
    # 构建订单明细
    for pattern_code, size in pattern_matches:
        item = {
            "patternCode": pattern_code,
            "fabric": fabric,
            "size": size.replace("码", ""),
            "drop": drop  # 使用解析到的落差值，为空时系统会从规格单获取默认值
        }
        
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
    
    # 提取团单客户单号
    group_order_no_match = re.search(r'团单客户单号[是为：:]([\w\-]+)', text)
    if group_order_no_match:
        result["itemKsOrderNo"] = group_order_no_match.group(1).strip()
    
    return result

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
    
    # 添加净尺寸 - 客户修改的尺寸放到这里
    if "ksMadeSize" in params and params["ksMadeSize"]:
        order_items_data["netSize"] = params["ksMadeSize"]
    
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
    
    return order_items_data

def create_order(params):
    """创建新订单（支持完整的订单字段和明细字段）"""
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
            input_data = parse_text_order(args.text)
            # 自动添加action为create
            input_data["action"] = "create"
            result = handler(input_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
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
