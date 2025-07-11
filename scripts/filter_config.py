# -*- coding: utf-8 -*-
"""
新闻过滤关键词配置 - 宽松版
只要是有意义的新闻就保留
"""

FILTER_CONFIG = {
    "version": "3.0",
    "categories": {
        "国际": {
            "keywords": [
                "中国", "中美", "美中", "Beijing", "Xi Jinping", "习近平", "Biden", "白宫",
                "国务院", "G7", "G20", "UN", "联合国", "欧盟", "NATO", "北约",
                "外交", "制裁", "会晤", "峰会", "双边会谈", "台湾", "South China Sea",
                "南海", "台海", "港澳", "新疆", "西藏", "人权", "间谍", "特使",
                "地缘政治", "脱钩", "decoupling",
                # 多语种政治关键词
                "Trump", "Biden", "Putin", "Xi", "Macron", "Scholz", "Sunak",
                "Politics", "Government", "Election", "President", "Prime Minister",
                "外交", "政治", "选举", "总统", "总理", "政府", "国会", "议会",
                # 国际新闻通用词
                "国际", "世界", "全球", "International", "World", "Global", "Foreign", "外交"
            ]
        },
        "军事": {
            "keywords": [
                "PLA", "解放军", "军演", "导弹", "航母", "战略轰炸机", "侦察机", "军事部署",
                "五角大楼", "Pentagon", "军售", "台军", "军备竞赛", "核潜艇", "Indo-Pacific",
                "俄乌战争", "乌克兰", "NATO军演", "军事对抗", "东海", "台海危机", "军事基地",
                "AUKUS", "QUAD", "亚太部署", "高超音速武器", "Missile", "Strike", "War",
                # 多语种军事关键词
                "Military", "Defense", "Arms", "Weapon", "War", "Conflict", "Navy", "Army", "Air Force",
                "军事", "国防", "武器", "战争", "冲突", "海军", "陆军", "空军", "导弹", "坦克"
            ]
        },
        "科技": {
            "keywords": [
                "AI", "Artificial Intelligence", "人工智能", "大模型", "算力", "Supercomputer",
                "半导体", "芯片", "chip", "GPU", "CPU", "Intel", "AMD", "ARM", "华为", "NVIDIA",
                "台积电", "中美科技战", "出口管制", "technology ban", "封锁", "ASML", "光刻机",
                "5G", "6G", "通信技术", "Starlink", "SpaceX", "太空互联网", "量子计算",
                "数字人民币", "数字货币", "CBDC", "区块链", "网络安全", "网络攻击", "blackout",
                # 多语种科技关键词
                "Technology", "Innovation", "Digital", "Software", "Hardware", "Internet", "Mobile",
                "科技", "创新", "数字", "软件", "硬件", "互联网", "移动", "智能", "自动化"
            ]
        },
        "财经": {
            "keywords": [
                "人民币", "RMB", "Dollar", "美元", "货币政策", "Inflation", "通胀", "降息", "升息",
                "美联储", "Fed", "IMF", "世行", "WTO", "贸易战", "出口管制", "投资限制",
                "中概股", "外资撤离", "Capital control", "跨国公司", "经济制裁",
                "一带一路", "Belt and Road", "制造业转移", "全球供应链", "Foreign direct investment",
                # 多语种财经关键词
                "Economy", "Finance", "Market", "Trade", "Investment", "Banking", "Stock", "Currency",
                "经济", "金融", "市场", "贸易", "投资", "银行", "股票", "货币", "汇率", "股市"
            ]
        },
        "社会": {
            "keywords": [
                "社会", "民生", "教育", "医疗", "住房", "就业", "社会保障", "社会福利",
                "Society", "Education", "Healthcare", "Housing", "Employment", "Social Security",
                "社会", "教育", "医疗", "住房", "就业", "社保", "福利", "民生"
            ]
        },
        "文化": {
            "keywords": [
                "文化", "艺术", "文学", "电影", "音乐", "博物馆", "文化遗产", "传统",
                "Culture", "Art", "Literature", "Film", "Music", "Museum", "Heritage",
                "文化", "艺术", "文学", "电影", "音乐", "博物馆", "遗产", "传统"
            ]
        },
        "体育": {
            "keywords": [
                "体育", "足球", "篮球", "奥运会", "世界杯", "联赛", "运动员", "教练",
                "Sports", "Football", "Basketball", "Olympics", "World Cup", "League", "Athlete",
                "体育", "足球", "篮球", "奥运", "世界杯", "联赛", "运动员", "教练"
            ]
        },
        "环境": {
            "keywords": [
                "环境", "气候", "污染", "环保", "可持续发展", "绿色", "能源", "碳排放",
                "Environment", "Climate", "Pollution", "Green", "Energy", "Carbon", "Sustainability",
                "环境", "气候", "污染", "环保", "可持续", "绿色", "能源", "碳"
            ]
        },
        "健康": {
            "keywords": [
                "健康", "医疗", "疾病", "疫苗", "药物", "医院", "医生", "患者",
                "Health", "Medical", "Disease", "Vaccine", "Medicine", "Hospital", "Doctor",
                "健康", "医疗", "疾病", "疫苗", "药物", "医院", "医生", "患者"
            ]
        }
    },
    "weak_keywords": [
        # 减少弱相关词，只保留明显无关的内容
        "UFO", "外星人", "灵异", "算命", "占卜"
    ],
    "blocked_keywords": [
        # 只屏蔽明显无意义的内容
        "小学生作文", "段子", "恶搞", "无意义", "测试", "广告"
    ]
} 