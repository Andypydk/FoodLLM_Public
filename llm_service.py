import os

from google import genai
from google.genai import types

from models import RecipeResult
from prompt_builder import build_recipe_prompt


# ============================================================
# 系統角色設定
# ============================================================

SYSTEM_INSTRUCTIONS = """
你是一位專業的智慧料理助手。

你的任務是根據使用者提供的：

- 現有食材
- 料理設備
- 可用料理時間
- 用餐人數
- 飲食限制
- 過敏資訊
- 偏好的料理風格

設計安全、合理、實際可以完成的料理。

所有輸出內容必須使用繁體中文。


【重要規則】

1. 不得加入使用者明確禁止的食材。

2. 必須檢查使用者的飲食限制與食材是否衝突。

3. 必須標示料理可能包含的過敏原。

4. 如果涉及嚴重過敏、疾病飲食、
   嬰幼兒飲食或特殊醫療需求，
   必須提供安全提醒。

5. 不確定的資訊不能自行假設，
   應放入 needs_confirmation。

6. 料理總時間應盡可能符合
   使用者設定的 max_minutes。

7. 使用者提供的設備有限時，
   不得要求使用不存在的設備。

8. ingredients 必須提供合理的料理份量。

9. steps 必須依照實際料理順序排列。

10. 每個料理步驟需要提供合理的分鐘數。

11. total_minutes 必須與料理流程合理一致。

12. shopping_items 只列出使用者目前缺少、
    但完成料理所需要的項目。

13. recommendation_reason 必須清楚說明：
    為什麼這道料理適合使用者目前的
    食材、設備、時間與飲食限制。

14. cuisine 必須符合使用者選擇的料理風格。

15. 不得捏造不存在或明顯不合理的料理方式。

16. 如果食材資訊不足，
    可以提出合理料理，
    但必須清楚標示需要補充或確認的項目。
"""


# ============================================================
# 產生料理
# ============================================================

def generate_recipes(
    ingredients,
    servings,
    max_minutes,
    equipment,
    restrictions,
    cuisine,
    recipe_count,
    api_key=None,
    model=None
):
    """
    使用 Gemini 產生結構化料理資料。

    Parameters
    ----------
    ingredients:
        使用者目前擁有的食材。

    servings:
        用餐人數。

    max_minutes:
        最長料理時間。

    equipment:
        可以使用的料理設備。

    restrictions:
        飲食限制與過敏條件。

    cuisine:
        中式、西式或中西融合等料理風格。

    recipe_count:
        希望產生的料理數量。

    api_key:
        Gemini API Key。

    model:
        Gemini 模型名稱。

    Returns
    -------
    RecipeResult
        經過 Pydantic 驗證的料理結果。
    """

    # ========================================================
    # 取得 API Key
    # ========================================================

    key = (
        api_key
        or os.getenv("GEMINI_API_KEY")
    )

    if not key:
        raise ValueError(
            "找不到 GEMINI_API_KEY，"
            "請確認 Gemini API Key 是否已正確設定。"
        )


    # ========================================================
    # 選擇模型
    # ========================================================

    selected_model = (
        model
        or "gemini-3.5-flash-lite"
    )


    # ========================================================
    # 建立 Gemini Client
    # ========================================================

    client = genai.Client(
        api_key=key
    )


    # ========================================================
    # 建立原本 FoodLLM 的料理 Prompt
    # ========================================================

    prompt = build_recipe_prompt(
        ingredients=ingredients,
        servings=servings,
        max_minutes=max_minutes,
        equipment=equipment,
        restrictions=restrictions,
        cuisine=cuisine,
        recipe_count=recipe_count
    )


    # ========================================================
    # 最終 Prompt
    # ========================================================

    full_prompt = f"""
{SYSTEM_INSTRUCTIONS}

============================================================
使用者料理需求
============================================================

{prompt}

============================================================
輸出要求
============================================================

請嚴格依照提供的 JSON Schema 產生資料。

請注意：

- 所有文字必須使用繁體中文。
- recipes 數量必須符合要求。
- 不要加入 Markdown。
- 不要使用 ```json。
- 不要加入 JSON 以外的額外說明文字。
- 每一道料理都必須有 recommendation_reason。
- 必須包含 ingredients、equipment、steps。
- 必須包含 total_minutes。
- 必須包含 shopping_items。
- 必須包含 allergens。
- 必須包含 needs_confirmation。
- 必須包含 safety_notes。
"""


    # ========================================================
    # 呼叫 Gemini
    # ========================================================

    try:

        response = client.models.generate_content(
            model=selected_model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecipeResult,
                temperature=0.4
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Gemini API 呼叫失敗："
            f"{error}"
        ) from error


    # ========================================================
    # 檢查 Gemini 是否有回應
    # ========================================================

    if response is None:

        raise ValueError(
            "Gemini 沒有回傳任何資料。"
        )


    # ========================================================
    # 優先使用 Gemini SDK 已解析完成的 Pydantic 結果
    # ========================================================

    parsed = response.parsed

    if isinstance(
        parsed,
        RecipeResult
    ):
        return parsed


    # ========================================================
    # 某些 SDK 狀況可能回傳 dict
    # ========================================================

    if isinstance(
        parsed,
        dict
    ):

        return RecipeResult.model_validate(
            parsed
        )


    # ========================================================
    # 如果 parsed 沒有成功，嘗試使用 response.text
    # ========================================================

    if response.text:

        try:

            return RecipeResult.model_validate_json(
                response.text
            )

        except Exception as error:

            raise ValueError(
                "Gemini 已回傳資料，"
                "但內容不符合 RecipeResult 格式。"
                f"\n詳細錯誤：{error}"
            ) from error


    # ========================================================
    # 完全沒有可使用的料理結果
    # ========================================================

    raise ValueError(
        "Gemini 沒有回傳有效的料理資料。"
    )