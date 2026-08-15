# 冰箱食材 AI 料理助手

此專案依照《LLM 食物料理應用學習》期末專題核心需求製作。

## 功能

- 輸入現有食材
- 選擇中式／西式／融合
- 設定用餐人數
- 設定最長料理時間
- 選擇現有設備
- 設定多種飲食限制
- 使用 OpenAI Responses API
- 以 Pydantic Structured Outputs 固定食譜格式
- 顯示食材與份量
- 顯示料理步驟與每步時間
- 顯示總時間
- 顯示缺少的採買項目
- 顯示過敏原
- 顯示需要確認的資訊
- 顯示食品安全提醒
- 內建 20 組測試案例
- 可輸出 test_results.csv

## 1. 建立虛擬環境

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

如果 PowerShell 不允許啟動，可改用 Windows CMD：

```cmd
.venv\Scripts\activate.bat
```

## 2. 安裝套件

```powershell
python -m pip install -r requirements.txt
```

## 3. 設定 OpenAI API Key

Windows CMD：

```cmd
setx OPENAI_API_KEY "你的_API_Key"
```

設定後請關閉並重新開啟 VS Code / Terminal。

確認環境變數存在：

```cmd
echo %OPENAI_API_KEY%
```

模型預設使用：

```text
gpt-5-mini
```

若帳戶可用模型不同，可另外設定：

```cmd
setx OPENAI_MODEL "你的模型名稱"
```

## 4. 先跑命令列版

```powershell
python main.py
```

## 5. 跑 Streamlit 網頁版

```powershell
python -m streamlit run app.py
```

瀏覽器會自動開啟本機網頁。

## 6. 執行測試案例

先測前三組，避免一次產生太多 API 用量：

```powershell
python run_tests.py 3
```

要跑全部 20 組：

```powershell
python run_tests.py 20
```

完成後會產生：

```text
test_results.csv
```

## 專案檔案

```text
FoodLLM_Final/
├─ app.py
├─ main.py
├─ llm_service.py
├─ models.py
├─ prompt_builder.py
├─ validators.py
├─ test_cases.py
├─ run_tests.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

## 安全提醒

不要把 API Key 直接寫在 Python 程式碼裡，也不要提交到 GitHub。

若部署 Streamlit Community Cloud，可在 App 的 Secrets 設定：

```toml
OPENAI_API_KEY = "你的_API_Key"
OPENAI_MODEL = "gpt-5-mini"
```

不要把 `.streamlit/secrets.toml` 提交到 GitHub。
