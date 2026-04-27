---
name: customer-order
displayName: 客商下单
version: 1.0.0
description: 客商订单管理技能，支持创建订单、查询订单状态、修改订单信息等功能
author: OpenClaw User
license: MIT
tags:
  - order
  - business
  - customer
requires:
  env:
    - ACCESS_KEY_ID
    - ACCESS_KEY_SECRET
  tools:
    - exec
  commands:
    - python3
---

# 客商订单管理技能 - 完整使用指南

## 功能特性

- ✅ 创建新的客商订单（支持完整字段和多明细）
- ✅ 查询订单状态
- ✅ 修改订单信息
- ✅ 取消订单
- ✅ 支持 JSON 文件输入
- ✅ 自动获取版型默认选项
- ✅ 自动填充规格单尺寸
- ✅ 支持上衣、西裤、大衣、衬衫等多种版型类型
- ✅ 完整支持所有量体尺寸和定制选项

## 快速开始

### 方法 1：使用 JSON 文件（推荐）

**步骤 1：填写订单信息**

编辑 `customer_order.json` 文件：

```json
{
    "khName": "客户姓名",
    "khImgurls": "客户照片 URL",
    "items": [
        {
            "patternCode": "版型编码",
            "fabric": "面料编号",
            "size": "尺码"
        }
    ]
}
```

**步骤 2：运行订单**

```bash
python index.py --json-file customer_order.json
```

### 方法 2：使用 JSON 字符串

```powershell
$json = @'
{
    "khName": "张三",
    "khImgurls": "https://example.com/photo.jpg",
    "items": [
        {"patternCode": "1KN002", "fabric": "22038-3/3", "size": "50"}
    ]
}
'@
python index.py --json $json
```

### 方法 3：命令行参数方式

```bash
python index.py --action create ^
    --khName "张三" ^
    --khImgurls "https://example.com/photo.jpg" ^
    --patternCode "1KN002" ^
    --fabric "22038-3/3" ^
    --size "50"
```

## JSON 字段详细说明

### 订单基本信息

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| khName | ✅ 是 | - | 客户姓名 |
| khImgurls | ✅ 是 | - | 客户照片 URL |
| khMtel | ❌ 否 | "1" | 手机号码 |
| khAddress | ❌ 否 | "1" | 收货地址 |
| khShapeCode | ❌ 否 | "正常体" | 体型 |
| orderRemarks | ❌ 否 | "" | 订单备注 |
| isManualOrder | ❌ 否 | false | 是否手工单 |
| deliveryDate | ❌ 否 | 15天后 | 交货日期 (YYYY-MM-DD) |

### 订单明细（items 数组）

每个明细项包含：

#### 必填字段

| 字段 | 说明 |
|------|------|
| patternTypeCode | 版型类型（SY=上衣，XK=西裤，DY=大衣，CS=衬衫） |
| patternCode | 版型编码（如：1KN002） |
| fabric | 面料编号 |
| size | 尺码 |

#### 定制选项（可选）

**上衣（SY）定制选项：**
| 字段 | 说明 |
|------|------|
| SY_jag | 加放量 |
| SY_ydj | 衣袋件 |
| SY_craft | 工艺（如："半麻衬"） |
| SY_jacketVent | 开叉 |
| SY_cuffKeyhole | 袖克夫钥匙孔 |
| SY_jacketPockets | 面大袋（如："B 款 两明袋"） |
| SY_sleeveElastic | 袖松紧 |
| SY_jacketTowelBag | 手巾袋（如："C 款 小明袋"） |
| SY_placketKeyhole | 门襟钥匙孔 |
| SY_jacketButtonhole | 扣眼 |
| SY_jacketSleeveType | 袖型 |
| SY_jacketChestLining | 胸衬 |
| SY_jacketShoulderPads | 肩垫 |
| SY_jacketSleeveButton | 袖扣 |
| SY_halfMileLiningStyle | 半里款式 |

**西裤（XK）定制选项：**
| 字段 | 说明 |
|------|------|
| XK_yks | 腰头松紧 |
| XK_Slide | 滑扣 |
| XK_jkjzd | 裤脚加固 |
| XK_hemOpening | 脚口（如："反撬"、"平撬"） |
| XK_pantsPocket | 裤口袋 |
| XK_strapBuckle | 松紧带 |
| XK_pantFrontFly | 门襟 |
| XK_pantBackPocket | 裤后袋 |
| XK_pantsWaistStyle | 裤腰款式 |
| XK_trouserFrontPockets | 裤前袋 |

**版型结构：**
| 字段 | 说明 |
|------|------|
| lapelType | 领型 |
| lapelWidth | 领宽 |
| buttonNumber | 扣数 |
| liningConstructions | 里布结构 |
| ph | 裤厚 |
| xb | 西裤 |
| xzks | 下装款式 |
| pleat | 褶裥 |

#### 客户净尺寸（netSize）

客户自定义尺寸填写在 `netSize` 对象中：

**上衣尺寸：**
| 字段 | 说明 |
|------|------|
| fullBust | 胸围 |
| fullWaistWidth | 腰围 |
| fullHipWidth | 臀围 |
| lowerHem | 下摆 |
| shoulderWidth | 肩宽 |
| sleeveLength | 袖长 |
| frontLength | 前长 |
| shortRegularTall | 长短 |
| wrisband | 腕围 |
| sleeveWidth | 袖宽 |
| backWidth | 背宽 |

**西裤尺寸：**
| 字段 | 说明 |
|------|------|
| fullWaistWidth | 腰围 |
| fullHipWidth | 臀围 |
| longPants | 裤长 |
| thigh | 大腿围 |
| calf | 小腿围 |
| upperleg | 上腿围 |
| innerPants | 内裆长 |
| forewave | 前浪 |
| wholewave | 后浪 |
| risingWaves | 起浪 |
| foodwith | 脚口宽 |

## 使用示例

### 示例 1：简单订单（使用默认值）

```json
{
    "khName": "张三",
    "khImgurls": "https://example.com/photo.jpg",
    "items": [
        {
            "patternCode": "1KN002",
            "fabric": "22038-3/3",
            "size": "50"
        }
    ]
}
```

### 示例 2：带定制选项的订单

```json
{
    "khName": "李四",
    "khImgurls": "https://example.com/photo.jpg",
    "items": [
        {
            "patternCode": "1KN002",
            "fabric": "22038-3/3",
            "size": "50",
            "ksPatternAttr": {
                "SY_jacketTowelBag": "C 款 小明袋"
            },
            "ksRemark": "手巾袋 C 款，手工套结"
        }
    ]
}
```

### 示例 3：带客户净尺寸的订单

```json
{
    "khName": "王五",
    "khImgurls": "https://example.com/photo.jpg",
    "items": [
        {
            "patternCode": "1KN002",
            "fabric": "22038-3/3",
            "size": "50",
            "netSize": {
                "fullBust": 115,
                "fullWaistWidth": 95,
                "fullHipWidth": 105
            }
        }
    ]
}
```

### 示例 4：多明细订单（上衣 + 西裤）

```json
{
    "khName": "赵六",
    "khImgurls": "https://example.com/photo.jpg",
    "items": [
        {
            "patternTypeCode": "SY",
            "patternCode": "1KN002",
            "fabric": "22038-3/3",
            "size": "50",
            "ksPatternAttr": {
                "SY_jacketTowelBag": "C 款 小明袋"
            }
        },
        {
            "patternTypeCode": "XK",
            "patternCode": "6KN358",
            "fabric": "22038-3/3",
            "size": "50",
            "ksPatternAttr": {
                "XK_hemOpening": "反撬"
            },
            "netSize": {
                "fullHipWidth": 90
            }
        }
    ]
}
```

### 示例 5：完整字段订单

```json
{
    "khName": "费好好",
    "khImgurls": "https://example.com/photo.jpg",
    "khMtel": "13800138000",
    "khAddress": "北京市朝阳区某某路 100 号",
    "khShapeCode": "正常体",
    "orderRemarks": "加急订单，请尽快处理",
    "isManualOrder": true,
    "deliveryDate": "2026-05-12",
    "items": [
        {
            "patternTypeCode": "SY",
            "patternCode": "1KN003",
            "fabric": "2ddd3",
            "size": "50",
            "drop": "0",
            "ksRemark": "手巾袋改成C款 小明袋，手工套结",
            "ksPatternAttr": {
                "SY_jacketTowelBag": "小明袋",
                "SY_craft": "手工套结"
            },
            "netSize": {
                "fullBust": 90,
                "fullHipWidth": 90,
                "fullWaistWidth": 96
            }
        },
        {
            "patternTypeCode": "XK",
            "patternCode": "6KN358",
            "fabric": "2ddd3",
            "size": "50",
            "drop": "0",
            "ksRemark": "脚口改成反撬，全臀围做到90",
            "ksPatternAttr": {
                "XK_hemOpening": "反撬"
            },
            "netSize": {
                "fullBust": 90,
                "fullHipWidth": 90,
                "fullWaistWidth": 96
            }
        }
    ]
}
```

## 命令行参数完整列表

### 订单基本信息
| 参数 | 说明 |
|------|------|
| --khName | 客户姓名（必填） |
| --khImgurls | 客户照片 URL（必填） |
| --khMtel | 手机号码 |
| --khAddress | 收货地址 |
| --khShapeCode | 体型 |
| --orderRemarks | 订单备注 |
| --isManualOrder | 是否手工单 (true/false) |
| --deliveryDate | 交货日期 (YYYY-MM-DD) |

### 订单明细
| 参数 | 说明 |
|------|------|
| --patternTypeCode | 版型类型编码 |
| --patternCode | 版型编码 |
| --fabricSupply | 面料供应 |
| --fabricMark | 面料标/面料品牌 |
| --lining | 里布 |
| --fabric | 面料编号 |
| --composition | 面料成分 |
| --fabricOrigin | 面料产地 |
| --placketNeedle | 门襟贡针 |
| --button | 纽扣 |
| --isSample | 是否试样 (true/false) |
| --ksRemark | 客商备注 |
| --specsCode | 规格单编码 |
| --size | 尺码 |
| --drop | 落差 |

### 绣花信息
| 参数 | 说明 |
|------|------|
| --isEmbroider | 是否绣花 (true/false) |
| --embroiderText | 绣花文字 |
| --embroiderTypeface | 绣花字体 |
| --embroiderColor | 绣花颜色 |
| --embroiderPic | 绣花图案 |

### 净尺寸
| 参数 | 说明 |
|------|------|
| --netFullBust | 净尺寸-胸围 |
| --netFullHipWidth | 净尺寸-臀围 |
| --netFullWaistWidth | 净尺寸-腰围 |
| --netLowerHem | 净尺寸-下摆 |
| --netShoulderWidth | 净尺寸-肩宽 |
| --netSleeveLength | 净尺寸-袖长 |
| --netFrontLength | 净尺寸-前长 |
| --netBackWidth | 净尺寸-背宽 |
| --netShortRegularTall | 净尺寸-长短 |
| --netWrisband | 净尺寸-腕围 |
| --netSleeveWidth | 净尺寸-袖宽 |

### 版型属性 - 西装上衣（SY）
| 参数 | 说明 |
|------|------|
| --syJag | 加放量 |
| --syYdj | 衣袋件 |
| --syCraft | 工艺 |
| --syJacketVent | 开叉 |
| --syCuffKeyhole | 袖克夫钥匙孔 |
| --syJacketPockets | 口袋 |
| --sySleeveElastic | 袖松紧 |
| --syJacketTowelBag | 毛巾袋 |
| --syPlacketKeyhole | 门襟钥匙孔 |
| --syJacketButtonhole | 扣眼 |
| --syJacketSleeveType | 袖型 |
| --syJacketChestLining | 胸衬 |
| --syJacketShoulderPads | 肩垫 |
| --syJacketSleeveButton | 袖扣 |
| --syHalfMileLiningStyle | 半里款式 |

### 版型属性 - 西裤（XK）
| 参数 | 说明 |
|------|------|
| --xkYks | 腰头松紧 |
| --xkSlide | 滑扣 |
| --xkJkjzd | 裤脚加固 |
| --xkHemOpening | 脚口 |
| --xkPantsPocket | 裤口袋 |
| --xkStrapBuckle | 松紧带 |
| --xkPantFrontFly | 门襟 |
| --xkPantBackPocket | 后袋 |
| --xkPantsWaistStyle | 裤腰款式 |
| --xkTrouserFrontPockets | 前插袋 |

### 版型结构
| 参数 | 说明 |
|------|------|
| --lapelType | 领型 |
| --lapelWidth | 领宽 |
| --buttonNumber | 扣数 |
| --liningConstructions | 里布结构 |
| --ph | 裤厚 |
| --xb | 西裤 |
| --xzks | 下装款式 |
| --pleat | 褶裥 |

### 特体信息
| 参数 | 说明 |
|------|------|
| --syFlatShoulder | 平肩 |
| --ksSpecialBodyRemark | 特体备注 |

## 注意事项

1. **必填字段**：客户姓名（khName）、客户照片（khImgurls）必须填写
2. **版型类型**：
   - SY = 上衣
   - XK = 西裤
   - DY = 大衣
   - CS = 衬衫
3. **定制选项**：如不填写，系统会自动使用版型的默认值
4. **客户尺寸**：如不填写，系统会自动使用规格单的标准尺寸
5. **落差**：如不填写，系统会自动选择规格单中的第一个落差
6. **多明细**：items 数组可以包含多个明细项（上衣、西裤等）
7. **自动默认值**：
   - 体型默认"正常体"
   - 手机号默认"1"
   - 地址默认"1"
   - 交货日期默认下单后 15 天
   - 面料供应默认"面料客供"

## 常见问题

### Q: 如何指定手巾袋为 C 款 小明袋？
A: 在明细的 ksPatternAttr 中添加 `"SY_jacketTowelBag": "C 款 小明袋"`

### Q: 如何指定西裤脚口为反撬？
A: 在西裤明细的 ksPatternAttr 中添加 `"XK_hemOpening": "反撬"`

### Q: 如何指定客户的胸围、腰围？
A: 在明细的 netSize 中添加对应的尺寸字段，如 `"netSize": {"fullBust": 115, "fullWaistWidth": 95}`

### Q: 如何同时下单上衣和西裤？
A: 在 items 数组中添加两个明细项，一个 patternTypeCode 为 SY，一个为 XK

### Q: 定制选项可以填中文名称吗？
A: 可以！系统支持中文名称自动匹配，如填"B 款"会自动转换为对应编码

### Q: 量体数据如何传递？
A: 系统会自动从规格单获取量体项目（massingCodes）和标准尺寸（massingRuleSize），客户自定义尺寸填写在 netSize 中

## 运行命令

```bash
# 使用 JSON 文件下单
python index.py --json-file customer_order.json

# 使用 JSON 字符串下单
python index.py --json '{"khName":"张三","khImgurls":"https://example.com/photo.jpg","items":[{"patternCode":"1KN002","fabric":"22038-3/3","size":"50"}]}'

# 命令行参数方式下单（单明细）
python index.py --action create ^
    --khName "张三" ^
    --khImgurls "https://example.com/photo.jpg" ^
    --patternCode "1KN002" ^
    --fabric "22038-3/3" ^
    --size "50" ^
    --netFullBust 90 ^
    --netFullHipWidth 90 ^
    --syJacketTowelBag "小明袋"

# 查询订单
python index.py --action query --order_id 123456

# 修改订单（仅本地存储）
python index.py --action update --order_id 123456 --customer_name "李四"

# 取消订单（仅本地存储）
python index.py --action cancel --order_id 123456
```

## 文件说明

- **index.py** - 主程序文件
- **SKILL.md** - 本使用指南
- **config.example.yaml** - 配置示例文件
- **manifest.yaml** - 技能清单文件

## 技术特性

- ✅ 支持 OpenClaw 技能标准（describe/handle 函数）
- ✅ 自动获取版型默认选项
- ✅ 自动填充规格单尺寸
- ✅ 支持中文名称自动转换为编码
- ✅ 自动选择第一个落差
- ✅ 区分上衣和西裤的量体字段
- ✅ 支持多明细订单
- ✅ 完善的错误处理和日志输出
- ✅ 完整支持所有量体尺寸和定制选项
