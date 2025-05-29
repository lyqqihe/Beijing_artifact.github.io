import pyodbc
import json
import geopandas as gpd
from pyproj import Proj, transform, CRS, Transformer
import math


def connect_to_sql_server():
    '''连接数据库'''
    server = 'localhost,1433'
    user = 'sa'
    password = 'lyq031222'
    database = '文物'

    try:
        connection = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={server};UID={user};PWD={password};DATABASE={database}"
        )
        print("Connection successful")
        return connection
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        return None

def search_dynasty(kind):
    '''根据朝代查询文物信息'''
    connection = connect_to_sql_server()
    if connection:
        cursor = connection.cursor()
        cursor.execute("select * from sheet$ where 时代=?", (kind,))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        connection.close()
        return results
    return None

def search_location(location):
    '''根据行政区位置查询文物信息'''
    connection = connect_to_sql_server()
    if connection:
        cursor = connection.cursor()
        cursor.execute("select * from sheet$ where 所在区=?", (location))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        connection.close()
        return results
    return None

def search_kind(kind):
    '''根据文物种类查询文物信息'''
    connection = connect_to_sql_server()
    if connection:
        cursor = connection.cursor()
        cursor.execute("select * from sheet$ where 类型=?", (kind,))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        connection.close()
        return results
    return None

def search_grade(grade):
    '''根据文物保护级别查询文物信息'''
    connection = connect_to_sql_server()
    if connection:
        cursor = connection.cursor()
        cursor.execute("select * from sheet$ where 级别=?", (grade,))
        results = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        connection.close()
        return results
    return None


def suggest(query):
    """搜索建议函数"""
    con = connect_to_sql_server()
    cursor = con.cursor()
    cursor.execute(
        "SELECT * FROM sheet$ WHERE 名称 LIKE ?",(f"%{query}%",)
    )
    suggestions = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return suggestions

def get_points():
    """获取点所有信息"""
    try:
        con = connect_to_sql_server()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM sheet$")
        points = cursor.fetchall()
        # 获取列名
        columns = [column[0] for column in cursor.description]
        cursor.close()
        con.close()

        # 返回 JSON 格式数据，坐标转换为火星坐标系
        result = []
        for row in points:
            try:
                # 提取经纬度并转换为浮点数
                longitude = row[columns.index("经度")]
                latitude = row[columns.index("纬度")]

                if longitude is None or latitude is None:
                    continue

                longitude = float(longitude)
                latitude = float(latitude)

                # 转换为火星坐标系
                converted_longitude, converted_latitude = wgs84_to_gcj02(longitude, latitude)
                if converted_longitude is None or converted_latitude is None:
                    raise ValueError("Coordinate conversion failed")

                # 构造结果
                result.append({
                    "longitude": converted_longitude,
                    "latitude": converted_latitude,
                    **dict(zip(columns, row))  # 其他字段
                })
            except Exception as e:
                print(f"Error processing row: {row}, Error: {e}")

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        print(f"Error in get_points: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def out_of_china(lng, lat):
    """判断经纬度是否在中国范围内"""
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)

# 转换所需的辅助函数
def transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret

def transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
    return ret

# WGS84 转 GCJ-02
def wgs84_to_gcj02(lng, lat):
    """将 WGS84 坐标转换为 GCJ-02 坐标"""
    if out_of_china(lng, lat):  # 如果不在中国范围内，返回原始坐标
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - 0.00669342162296594323 * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((6335552.717000426 / (magic * sqrtmagic)) * math.pi)
    dlng = (dlng * 180.0) / ((6378245.0 / sqrtmagic) * math.pi)
    mg_lat = lat + dlat
    mg_lng = lng + dlng
    return mg_lng, mg_lat

def normalize_dynasty(dynasty_str):
    """标准化朝代名称"""
    if not dynasty_str or dynasty_str == '':
        return ['未知']
    
    # 处理常见的分隔符
    for sep in ['、', ',', '，', ';', '；', '|']:
        if sep in str(dynasty_str):
            return [d.strip() for d in str(dynasty_str).split(sep) if d.strip()]
    
    return [dynasty_str]

#绘制统计图表
def get_statistics(category, method):
    """分区统计：统计北京市每个区的各类文物数量"""
    if method not in ['pie', 'bar']:
        return {"error": "仅支持饼图和柱状图"}
    
    connection = connect_to_sql_server()
    if not connection:
        return {"error": "数据库连接失败"}
    
    cursor = connection.cursor()
    # 获取所有区并标准化
    cursor.execute("SELECT DISTINCT 所在区 FROM sheet$ WHERE 所在区 IS NOT NULL AND 所在区 != ''")
    raw_districts = [str(row[0]).strip() for row in cursor.fetchall()]
    
    # 创建区划映射字典
    district_mapping = {}
    for district in raw_districts:
        if not district:
            continue
        # 处理包含分隔符的情况
        if any(sep in district for sep in ['、', ',', '，', ';', '；', '|']):
            parts = [p.strip() for p in district.replace('，', ',').replace('；', ';').replace('、', ',').split(',') if p.strip()]
            for part in parts:
                if part not in district_mapping:
                    district_mapping[part] = part
        else:
            if district not in district_mapping:
                district_mapping[district] = district
    
    # 获取标准化后的区划列表
    districts = sorted(list(district_mapping.keys()))
    
    # 根据不同类别进行统计
    if category == 'dynasty':
        field = '时代'
        # 获取所有朝代并标准化
        cursor.execute(f"SELECT DISTINCT {field} FROM sheet$ WHERE {field} IS NOT NULL")
        raw_dynasties = [str(row[0]).strip() for row in cursor.fetchall()]
        
        # 创建朝代映射字典
        dynasty_mapping = {}
        for dynasty in raw_dynasties:
            if not dynasty:
                continue
            # 处理包含分隔符的情况
            if any(sep in dynasty for sep in ['、', ',', '，', ';', '；', '|']):
                parts = [p.strip() for p in dynasty.replace('，', ',').replace('；', ';').replace('、', ',').split(',') if p.strip()]
                for part in parts:
                    if part not in dynasty_mapping:
                        dynasty_mapping[part] = part
            else:
                if dynasty not in dynasty_mapping:
                    dynasty_mapping[dynasty] = dynasty
        
        # 获取标准化后的朝代列表
        categories = sorted(list(dynasty_mapping.keys()))
        
        # 构建分区-朝代统计矩阵
        matrix = []
        for district in districts:
            row_counts = [0] * len(categories)
            # 获取该区所有文物记录
            cursor.execute(f"SELECT {field}, 所在区 FROM sheet$ WHERE 所在区 LIKE ?", (f"%{district}%",))
            for dynasty_str, district_str in cursor.fetchall():
                if not dynasty_str:
                    continue
                    
                # 处理朝代
                if any(sep in str(dynasty_str) for sep in ['、', ',', '，', ';', '；', '|']):
                    dynasty_parts = [p.strip() for p in str(dynasty_str).replace('，', ',').replace('；', ';').replace('、', ',').split(',') if p.strip()]
                else:
                    dynasty_parts = [str(dynasty_str).strip()]
                # 处理区划
                if any(sep in str(district_str) for sep in ['、', ',', '，', ';', '；', '|']):
                    district_parts = [p.strip() for p in str(district_str).replace('，', ',').replace('；', ';').replace('、', ',').split(',') if p.strip()]
                else:
                    district_parts = [str(district_str).strip()]
                
                # 如果当前区在区划列表中，则统计
                if district in district_parts:
                    for dynasty in dynasty_parts:
                        if dynasty in categories:
                            idx = categories.index(dynasty)
                            row_counts[idx] += 1
            matrix.append(row_counts)
    else:
        if category == 'open_status':
            field = '开放状态'
        elif category == 'type':
            field = '类型'
        elif category == 'level':
            field = '级别'
        else:
            connection.close()
            return {"error": "无效的统计类别"}
            
        cursor.execute(f"SELECT DISTINCT {field} FROM sheet$ WHERE {field} IS NOT NULL AND {field} != ''")
        categories = [str(row[0]) for row in cursor.fetchall()]
        # 对级别进行排序：数字开头的在前，'其他'在最后
        if category == 'level':
            num_cats = [c for c in categories if c and c[0].isdigit()]
            other_cats = [c for c in categories if c == '其他']
            rest_cats = [c for c in categories if c not in num_cats and c not in other_cats]
            categories = sorted(num_cats, key=lambda x: int(''.join(filter(str.isdigit, x)))) + rest_cats + other_cats
        
        matrix = []
        for district in districts:
            row_counts = []
            for cat in categories:
                # 修改查询以处理多区划情况
                cursor.execute(f"SELECT COUNT(*) FROM sheet$ WHERE 所在区 LIKE ? AND {field}=?", (f"%{district}%", cat))
                count = cursor.fetchone()[0]
                row_counts.append(count)
            matrix.append(row_counts)
    
    connection.close()
    return {"districts": districts, "categories": categories, "matrix": matrix}

def get_all_categories():
    """返回所有筛选标准下的类别"""
    connection = connect_to_sql_server()
    if not connection:
        return {"error": "数据库连接失败"}
    cursor = connection.cursor()
    result = {}
    # 朝代
    cursor.execute("SELECT DISTINCT 时代 FROM sheet$ WHERE 时代 IS NOT NULL AND 时代 != ''")
    dynasties = set()
    for row in cursor.fetchall():
        for d in normalize_dynasty(row[0]):
            d = d.strip()  # 去除首尾空格
            if d:  # 排除空字符串
                dynasties.add(d)
    result['dynasty'] = sorted(list(dynasties))
    # 级别
    cursor.execute("SELECT DISTINCT 级别 FROM sheet$ WHERE 级别 IS NOT NULL AND 级别 != ''")
    result['level'] = sorted([row[0] for row in cursor.fetchall()])
    # 行政区
    cursor.execute("SELECT DISTINCT 所在区 FROM sheet$ WHERE 所在区 IS NOT NULL AND 所在区 != ''")
    districts = set()
    for row in cursor.fetchall():
        for d in normalize_dynasty(row[0]):  # 复用分割
            districts.add(d)
    result['location'] = sorted(list(districts))
    # 类型
    cursor.execute("SELECT DISTINCT 类型 FROM sheet$ WHERE 类型 IS NOT NULL AND 类型 != ''")
    result['type'] = sorted([row[0] for row in cursor.fetchall()])
    connection.close()
    return result

