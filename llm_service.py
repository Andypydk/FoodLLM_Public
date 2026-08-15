import os
from openai import OpenAI

from models import RecipeResult
from prompt_builder import build_recipe_prompt


SYSTEM_INSTRUCTIONS = """
你是一位專業的繁體中文料理資訊助手。

所有輸出內容都必須使用繁體中文。

你必須遵守使用者提供的：
- 現有食材
- 現有設備
- 最長料理時間
- 用餐人數
- 飲食限制
- 過敏原限制
- 料理風格

每一道料理都必須提供清楚的推薦理由，
說明為什麼這道料理符合使用者目前的食材、設備、時間與飲食條件。

資訊不足時不可自行假設。

涉及嚴重過敏、疾病飲食、嬰幼兒飲食或特殊醫療需求時，
只能作為資訊整理工具，
不能取代食品標示、醫師或營養專業人員的判斷。
""".strip()


def generate_recipes(
    ingredients: list[str],
    servings: int,
    max_minutes: int,
    equipment: list[str],
    restrictions: list[str],
    cuisine: str,
    recipe_count: int = 2,
    api_key: str | None = None,
    model: str | None = None,
) -> RecipeResult:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("找不到 OPENAI_API_KEY，請先設定 API 金鑰。")
    selected_model = model or os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna"
)

    prompt = build_recipe_prompt(
        ingredients=ingredients,
        servings=servings,
        max_minutes=max_minutes,
        equipment=equipment,
        restrictions=restrictions,
        cuisine=cuisine,
        recipe_count=recipe_count,
    )

    response = client.responses.parse(
        model=selected_model,
        input=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
        text_format=RecipeResult,
    )

    if response.output_parsed is None:
        raise RuntimeError("模型沒有回傳可解析的食譜資料。")

    return response.output_parsed
