from flask import render_template, request, redirect, url_for, jsonify
from . import app
from app import sql_search
from app.sql_search import get_points, get_all_categories
import json
import requests

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    return redirect(url_for('index'))

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    # 调用 sql_search.suggest 获取提示数据
    suggestions = sql_search.suggest(query)
    return jsonify(suggestions)

@app.route('/api/points', methods=['GET'])
def api_get_points():
    """返回点数据的 API"""
    try:
        points = get_points()  # 调用 get_points 函数获取点数据
        return jsonify(json.loads(points))  # 确保返回 JSON 格式数据
    except Exception as e:
        return jsonify({"error": str(e)}), 500

AMAP_KEY = 	'b2f8b7d532598cf03d5b30f33a883146'

@app.route('/api/geocode')
def geocode():
    address = request.args.get('address')
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = {'address': address, 'key': AMAP_KEY}
    resp = requests.get(url, params=params)
    return jsonify(resp.json())

@app.route('/api/route')
def route():
    origin = request.args.get('origin')  # 'lng,lat'
    destination = request.args.get('destination')  # 'lng,lat'
    mode = request.args.get('mode', 'driving')  # driving/walking/transit
    if mode == 'driving':
        url = 'https://restapi.amap.com/v3/direction/driving'
    elif mode == 'walking':
        url = 'https://restapi.amap.com/v3/direction/walking'
    elif mode == 'transit':
        url = 'https://restapi.amap.com/v3/direction/transit/integrated'
    else:
        return jsonify({'error': 'Invalid mode'}), 400
    params = {'origin': origin, 'destination': destination, 'key': AMAP_KEY, 'city': '北京'}
    resp = requests.get(url, params=params)
    return jsonify(resp.json())

@app.route('/api/statistics')
def api_statistics():
    category = request.args.get('category')
    method = request.args.get('method')
    result = sql_search.get_statistics(category, method)
    return jsonify(result)

@app.route('/api/categories')
def api_categories():
    return jsonify(get_all_categories())
