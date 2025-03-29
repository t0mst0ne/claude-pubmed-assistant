#!/usr/bin/env python3
"""
基本用法示例 - 展示如何直接通過API使用Claude PubMed助手
"""

import requests
import json
import sys

# 服務器URL（預設為本地運行）
SERVER_URL = "http://localhost:8000"

def search_pubmed(query, max_results=10, sort="relevance", since_year=None):
    """
    搜索PubMed並返回結果
    """
    url = f"{SERVER_URL}/api/search"
    
    data = {
        "query": query,
        "max_results": max_results,
        "sort": sort
    }
    
    if since_year:
        data["since_year"] = since_year
    
    response = requests.post(url, json=data)
    
    if response.status_code != 200:
        print(f"錯誤: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def get_claude_format(query, max_results=10, sort="relevance", since_year=None):
    """
    獲取Claude友好格式的PubMed搜索結果
    """
    url = f"{SERVER_URL}/api/claude_format"
    
    data = {
        "query": query,
        "max_results": max_results,
        "sort": sort
    }
    
    if since_year:
        data["since_year"] = since_year
    
    response = requests.post(url, json=data)
    
    if response.status_code != 200:
        print(f"錯誤: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()["formatted_text"]

def save_to_file(content, filename):
    """
    將內容保存到文件
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已保存到 {filename}")

def main():
    """
    主函數 - 處理命令行參數並執行搜索
    """
    if len(sys.argv) < 2:
        print("用法: python basic_usage.py <搜索詞> [最大結果數] [排序方式] [起始年份] [輸出文件]")
        return
    
    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    sort = sys.argv[3] if len(sys.argv) > 3 else "relevance"
    since_year = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
    output_file = sys.argv[5] if len(sys.argv) > 5 else None
    
    print(f"搜索 PubMed: {query}")
    print(f"最大結果數: {max_results}")
    print(f"排序方式: {sort}")
    if since_year:
        print(f"起始年份: {since_year}")
    
    # 獲取JSON結果
    results = search_pubmed(query, max_results, sort, since_year)
    
    if not results:
        print("沒有找到結果")
        return
    
    print(f"找到 {len(results)} 篇文章")
    
    # 打印第一篇文章的標題和摘要
    if results:
        print("\n第一篇文章:")
        print(f"標題: {results[0]['title']}")
        print(f"期刊: {results[0]['journal']}")
        print(f"發布日期: {results[0]['publication_date']}")
        print(f"PMID: {results[0]['pmid']}")
        if results[0]['abstract']:
            print(f"摘要: {results[0]['abstract'][:200]}...")
    
    # 獲取Claude格式
    claude_text = get_claude_format(query, max_results, sort, since_year)
    
    # 保存到文件（如果指定）
    if output_file:
        save_to_file(claude_text, output_file)
    
    print("\nClaude格式輸出的前200個字符:")
    print(claude_text[:200] + "...\n")
    print("你可以使用 get_claude_format() 函數獲取完整的格式化文本，"
          "然後將其粘貼到Claude對話框中。")

if __name__ == "__main__":
    main()
