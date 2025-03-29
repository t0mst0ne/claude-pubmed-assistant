# Claude PubMed Assistant

一個將PubMed學術文獻搜索與Claude AI助手整合的簡單API服務。

## 🌟 功能特點

- 🔍 快速搜索PubMed醫學文獻資料庫
- 📊 獲取結構化JSON格式的研究文章資料
- 📝 生成專為Claude優化的格式化輸出
- 🌐 提供簡單的Web界面進行搜索
- 🤖 為AI提示提供範本
- 🔄 支持高級搜索參數（日期範圍、排序等）

## 🚀 快速開始

### 安裝

1. 克隆此倉庫：
```bash
git clone https://github.com/yourusername/claude-pubmed-assistant.git
cd claude-pubmed-assistant
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 啟動服務器：
```bash
python run.py
```

服務器將在 http://localhost:8000 啟動，並自動打開瀏覽器

### 使用方法

#### 使用Web界面

1. 打開瀏覽器，訪問 http://localhost:8000
2. 輸入搜索詞，設置參數
3. 點擊「搜索」按鈕
4. 複製結果到Claude對話框

#### 使用API

```python
import requests
import json

# 基本搜索
response = requests.post('http://localhost:8000/api/search', 
                        json={'query': 'covid vaccine'})
results = response.json()

# 高級搜索
response = requests.post('http://localhost:8000/api/search', 
                        json={
                            'query': 'stroke treatment',
                            'max_results': 15,
                            'sort': 'date',
                            'since_year': 2022
                        })
results = response.json()

# 獲取Claude優化格式
response = requests.post('http://localhost:8000/api/claude_format', 
                        json={
                            'query': 'diabetes management',
                            'max_results': 5
                        })
claude_text = response.json()['formatted_text']
print(claude_text)  # 複製到Claude對話框
```

## 📖 工作原理

1. 服務器接收搜索請求
2. 使用PubMed E-utilities API查詢醫學文獻
3. 解析結果為結構化資料
4. 返回JSON或格式化的Markdown內容
5. 用戶將結果提供給Claude進行分析和總結

## 🧩 與Claude協作

最佳實踐：

1. 先搜索相關文獻
2. 使用「Claude優化格式」功能
3. 複製格式化結果到Claude對話框
4. 為Claude提供明確指示，例如：
   - "請分析這些關於心臟病治療的最新研究"
   - "總結這些論文的主要發現和方法論"
   - "比較這些不同研究的結果並解釋差異"

查看 `examples/claude_prompt.md` 了解更多提示模板。

## 🛠️ 進階配置

可在 `.env` 文件中設置以下選項：
```
PUBMED_API_KEY=your_api_key_here  # 可選但建議
HOST=0.0.0.0                      # 服務器主機
PORT=8000                         # 服務器端口
DEBUG=False                       # 生產環境應設為False
```

## 📋 API參考

### `POST /api/search`

參數：
- `query` (必須): 搜索詞
- `max_results` (可選, 默認=10): 最大結果數
- `sort` (可選, 默認="relevance"): 排序方式 ("relevance" 或 "date")
- `since_year` (可選): 僅顯示特定年份之後的結果

返回：JSON格式的文章列表

### `POST /api/claude_format`

參數同上，返回：
- `formatted_text`: 為Claude優化的Markdown格式文本

### `GET /api/article/<pmid>`

參數：
- `pmid`: PubMed ID

返回：特定文章的詳細信息

## 📚 依賴項

本專案僅依賴三個主要套件：
- Flask (Web框架)
- httpx (非同步HTTP客戶端)
- python-dotenv (環境變數管理)

## 🔄 疑難排解

如果遇到問題：

1. **依賴錯誤**: 確保使用 `pip install -r requirements.txt` 安裝所有依賴項
2. **連接錯誤**: 檢查網絡連接和PubMed API狀態
3. **啟動失敗**: 檢查端口是否被占用，嘗試修改 `.env` 文件中的 PORT 設置
4. **搜索結果為空**: 調整搜索詞，使用PubMed高級搜索語法 

## 📜 許可證

MIT

## 🤝 貢獻

歡迎提交Issue和Pull Request！

1. Fork此倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開Pull Request

## 📮 聯繫方式

[你的郵箱或聯繫方式]
