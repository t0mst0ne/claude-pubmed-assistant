#!/usr/bin/env python3
import os
import asyncio
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from dotenv import load_dotenv
from pubmed_client import PubMedClient

# 加載環境變量
load_dotenv()

app = Flask(__name__)

# 配置
API_KEY = os.getenv("PUBMED_API_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 主頁路由
@app.route('/')
def index():
    return render_template('index.html')

# API：搜索
@app.route('/api/search', methods=['POST'])
def search():
    data = request.json or {}
    
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "查詢參數不能為空"}), 400
        
    max_results = int(data.get('max_results', 10))
    sort = data.get('sort', 'relevance')
    since_year = data.get('since_year')
    
    # 構建完整查詢
    full_query = query
    if since_year:
        full_query = f"({query}) AND {since_year}:3000[PDAT]"
    
    # 創建一個新的事件循環來執行非同步函數
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 執行搜索
        client = PubMedClient(api_key=API_KEY)
        try:
            results = loop.run_until_complete(client.search(
                query=full_query,
                max_results=max_results,
                sort=sort
            ))
            return jsonify(results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            loop.run_until_complete(client.close())
    finally:
        loop.close()

# API：獲取單篇文章詳情
@app.route('/api/article/<pmid>', methods=['GET'])
def get_article(pmid):
    # 創建一個新的事件循環來執行非同步函數
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        client = PubMedClient(api_key=API_KEY)
        try:
            article = loop.run_until_complete(client.get_article_details(pmid))
            return jsonify(article)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            loop.run_until_complete(client.close())
    finally:
        loop.close()

# API：生成Claude友好格式
@app.route('/api/claude_format', methods=['POST'])
def claude_format():
    data = request.json or {}
    
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "查詢參數不能為空"}), 400
        
    max_results = int(data.get('max_results', 10))
    sort = data.get('sort', 'relevance')
    since_year = data.get('since_year')
    
    # 構建完整查詢
    full_query = query
    if since_year:
        full_query = f"({query}) AND {since_year}:3000[PDAT]"
    
    # 創建一個新的事件循環來執行非同步函數
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # 執行搜索
        client = PubMedClient(api_key=API_KEY)
        try:
            results = loop.run_until_complete(client.search(
                query=full_query,
                max_results=max_results,
                sort=sort
            ))
            
            # 格式化為Markdown格式
            formatted = f"# PubMed搜索結果: {query}\n\n"
            
            if not results:
                formatted += "未找到結果。\n"
            else:
                for i, article in enumerate(results, 1):
                    # 標題和基本信息
                    formatted += f"## {i}. {article['title']}\n"
                    formatted += f"**期刊**: {article['journal']}, **日期**: {article['publication_date']}\n\n"
                    
                    # 摘要
                    if article['abstract']:
                        formatted += f"**摘要**: {article['abstract']}\n\n"
                    else:
                        formatted += "**摘要**: 未提供\n\n"
                    
                    # 作者
                    if article['authors']:
                        formatted += f"**作者**: {', '.join(article['authors'])}\n\n"
                    
                    # 標識符和連結
                    formatted += f"**PMID**: {article['pmid']}"
                    if article['doi']:
                        formatted += f", **DOI**: {article['doi']}"
                    formatted += f"\n**鏈接**: {article['url']}\n\n"
                    
                    if i < len(results):
                        formatted += "---\n\n"
            
            return jsonify({"formatted_text": formatted})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            loop.run_until_complete(client.close())
    finally:
        loop.close()

# Web表單搜索
@app.route('/search', methods=['POST'])
def web_search():
    query = request.form.get('query', '')
    max_results = int(request.form.get('max_results', 10))
    sort = request.form.get('sort', 'relevance')
    since_year = request.form.get('since_year')
    format_type = request.form.get('format', 'json')
    
    if not query:
        return render_template('index.html', error="請輸入搜索詞")
    
    # 直接執行搜索，不通過API
    # 構建完整查詢
    full_query = query
    if since_year and since_year.strip():
        try:
            year = int(since_year)
            full_query = f"({query}) AND {year}:3000[PDAT]"
        except ValueError:
            pass
    
    # 創建一個新的事件循環來執行非同步函數
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        client = PubMedClient(api_key=API_KEY)
        try:
            results = loop.run_until_complete(client.search(
                query=full_query,
                max_results=max_results,
                sort=sort
            ))
            
            if format_type == 'claude':
                # 格式化為Markdown格式
                formatted = f"# PubMed搜索結果: {query}\n\n"
                
                if not results:
                    formatted += "未找到結果。\n"
                else:
                    for i, article in enumerate(results, 1):
                        # 標題和基本信息
                        formatted += f"## {i}. {article['title']}\n"
                        formatted += f"**期刊**: {article['journal']}, **日期**: {article['publication_date']}\n\n"
                        
                        # 摘要
                        if article['abstract']:
                            formatted += f"**摘要**: {article['abstract']}\n\n"
                        else:
                            formatted += "**摘要**: 未提供\n\n"
                        
                        # 作者
                        if article['authors']:
                            formatted += f"**作者**: {', '.join(article['authors'])}\n\n"
                        
                        # 標識符和連結
                        formatted += f"**PMID**: {article['pmid']}"
                        if article['doi']:
                            formatted += f", **DOI**: {article['doi']}"
                        formatted += f"\n**鏈接**: {article['url']}\n\n"
                        
                        if i < len(results):
                            formatted += "---\n\n"
                
                return render_template('results.html', 
                                query=query,
                                formatted_text=formatted,
                                format_type='claude')
            else:
                return render_template('results.html', 
                                query=query,
                                results=results,
                                format_type='json')
        except Exception as e:
            return render_template('index.html', error=f"搜索錯誤: {str(e)}")
        finally:
            loop.run_until_complete(client.close())
    finally:
        loop.close()

# 運行服務器
if __name__ == '__main__':
    try:
        print(f"啟動 Claude PubMed 助手服務器... ")
        print(f"訪問 http://{HOST}:{PORT} 開始使用")
        
        # 直接使用 Flask 运行服務器
        app.run(host=HOST, port=PORT, debug=DEBUG)
        
    except Exception as e:
        print(f"啟動服務器時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
