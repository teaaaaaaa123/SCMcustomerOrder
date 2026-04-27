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
    "access_key_id": "XX",
    "access_key_secret": "XX",
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
        "isManualOrder": True,
        "items": [],
        "orderRemarks": ""
    }
    
    # 提取客户姓名
    name_match = re.search(r'客户姓名[是为：:]([\u4e00-\u9fa5]+)', text)
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
    
    # 提取面料货号（支持特殊字符如 - /）
    fabric_match = re.search(r'面料货号[是为：:]([\w\-/]+)', text)
    if not fabric_match:
        fabric_match = re.search(r'面料[是为：:]([\w\-/]+)', text)
    fabric = fabric_match.group(1).strip() if fabric_match else ""
    
    # 提取版型编码和尺码（支持多个版型）
    pattern_matches = re.findall(r'([A-Z0-9]+)的(\d+码)', text)
    if not pattern_matches:
        pattern_matches = re.findall(r'([A-Z0-9]+)\s*(\d+码)', text)
    
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
    
    # 工艺
    craft_match = re.search(r'工艺' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if craft_match:
        sy_attr["SY_craft"] = craft_match.group(1).strip()
    
    # 后叉/开叉
    vent_match = re.search(r'上衣后叉' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not vent_match:
        vent_match = re.search(r'开叉' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if vent_match:
        sy_attr["SY_jacketVent"] = vent_match.group(1).strip()
    
    # 手巾袋（支持中文和字母）
    towel_bag_match = re.search(r'手巾袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if towel_bag_match:
        sy_attr["SY_jacketTowelBag"] = towel_bag_match.group(1).strip()
    
    # 面大袋（支持中文和字母）
    pocket_match = re.search(r'上衣面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if not pocket_match:
        pocket_match = re.search(r'面大袋' + modify_words + r'([\u4e00-\u9fa5\sA-Za-z]+?)(?=、|，|$)', text)
    if pocket_match:
        sy_attr["SY_jacketPockets"] = pocket_match.group(1).strip()
    
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
        sy_attr["SY_sleeveElastic"] = elastic_match.group(1).strip()
    
    # 胸衬
    chest_lining_match = re.search(r'胸衬' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if chest_lining_match:
        sy_attr["SY_jacketChestLining"] = chest_lining_match.group(1).strip()
    
    # 垫肩
    shoulder_pad_match = re.search(r'右垫肩' + modify_words + r'([\d.]+cm)', text)
    if shoulder_pad_match:
        sy_attr["SY_jacketShoulderPads"] = shoulder_pad_match.group(1).strip()
    
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
    if hem_match:
        xk_attr["XK_hemOpening"] = hem_match.group(1).strip()
    
    # 脚口反撬数值（如：脚口反撬改5）
    hem_value_match = re.search(r'脚口反撬' + modify_words + r'(\d+)', text)
    if hem_value_match:
        xk_attr["XK_hemOpeningValue"] = hem_value_match.group(1).strip()
    
    # 腰款式（支持字母）
    waist_style_match = re.search(r'腰款式' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    if not waist_style_match:
        waist_style_match = re.search(r'腰款' + modify_words + r'([\u4e00-\u9fa5A-Za-z]+)', text)
    if waist_style_match:
        xk_attr["XK_pantsWaistStyle"] = waist_style_match.group(1).strip()
    
    # 前口袋
    front_pocket_match = re.search(r'裤子前口袋' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if not front_pocket_match:
        front_pocket_match = re.search(r'前口袋' + modify_words + r'([\u4e00-\u9fa5]+)', text)
    if front_pocket_match:
        xk_attr["XK_trouserFrontPockets"] = front_pocket_match.group(1).strip()
    
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
            if sy_attr:
                item["ksPatternAttr"] = sy_attr
        elif pattern_code.startswith("2K") or pattern_code.startswith("3K"):
            item["patternTypeCode"] = "SY"
            if sy_attr:
                item["ksPatternAttr"] = sy_attr
        elif pattern_code.startswith("4"):
            item["patternTypeCode"] = "DY"
            if dy_attr:
                item["ksPatternAttr"] = dy_attr
        elif pattern_code.startswith("5"):
            item["patternTypeCode"] = "MJ"
            if sy_attr:
                item["ksPatternAttr"] = sy_attr
        elif pattern_code.startswith("6") or pattern_code.startswith("7"):
            item["patternTypeCode"] = "XK"
            if xk_attr:
                item["ksPatternAttr"] = xk_attr
            if xk_net_size:
                item["netSize"] = xk_net_size
        elif pattern_code.startswith("1SF") or pattern_code.startswith("8") or pattern_code.startswith("9"):
            item["patternTypeCode"] = "LZ"
            if sy_attr:
                item["ksPatternAttr"] = sy_attr
        elif pattern_code.startswith("0"):
            item["patternTypeCode"] = "MJ"
            if sy_attr:
                item["ksPatternAttr"] = sy_attr
        
        result["items"].append(item)
    
    # 生成备注
    remarks = []
    if "手工套结" in text:
        remarks.append("手工套结")
    if remarks:
        result["orderRemarks"] = "，".join(remarks)
    
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
        "xkYks": "XK_yks",
        "xkSlide": "XK_Slide",
        "xkJkjzd": "XK_jkjzd",
        "xkHemOpening": "XK_hemOpening",
        "xkPantsPocket": "XK_pantsPocket",
        "xkStrapBuckle": "XK_strapBuckle",
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
    
    # 添加版型属性 - 只使用版型实际有的定制选项，使用编码
    if "ksPatternAttr" in params and params["ksPatternAttr"]:
        order_items_data["ksPatternAttr"] = params["ksPatternAttr"]
    else:
        default_attr = pattern_info.get("patternAttr", {})
        if default_attr:
            order_items_data["ksPatternAttr"] = default_attr
    
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
        "manualOrderhImgurls": params.get("manualOrderhImgurls", "")
    }
    
    # 如果没有提供多个明细，则使用当前参数作为单个明细
    if not items_list:
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
        "xkYks": "XK_yks",
        "xkSlide": "XK_Slide",
        "xkJkjzd": "XK_jkjzd",
        "xkHemOpening": "XK_hemOpening",
        "xkPantsPocket": "XK_pantsPocket",
        "xkStrapBuckle": "XK_strapBuckle",
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
