import os

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# ============================================================
# 冰箱辨識結果資料模型
# ============================================================

class FridgeRecognitionResult(BaseModel):

    confirmed_items: list[str] = Field(
        description="照片中可以明確確認的食材"
    )

    possible_items: list[str] = Field(
        description="照片中可能存在，但無法完全確認的食材"
    )

    needs_confirmation: list[str] = Field(
        description="無法清楚辨識，需要使用者再次確認的物品"
    )

    overall_note: str = Field(
        description="對本次冰箱照片辨識結果的簡短繁體中文說明"
    )


# ============================================================
# 冰箱照片辨識
# ============================================================

def recognize_fridge_items(
    image_bytes: bytes,
    api_key: str = None,
    model: str = "gemini-3.5-flash-lite",
    mime_type: str = "image/jpeg"
) -> dict:
    """
    使用 Gemini 分析冰箱照片並回傳結構化食材辨識結果。

    Parameters
    ----------
    image_bytes:
        使用者上傳圖片的 bytes。

    api_key:
        Gemini API Key。

    model:
        Gemini 模型名稱。

    mime_type:
        圖片 MIME Type，
        例如 image/jpeg、image/png。

    Returns
    -------
    dict
        {
            "confirmed_items": [],
            "possible_items": [],
            "needs_confirmation": [],
            "overall_note": ""
        }
    """

    # ========================================================
    # API Key
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
    # MIME Type 防呆
    # ========================================================

    if not mime_type:
        mime_type = "image/jpeg"

    allowed_mime_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if mime_type not in allowed_mime_types:
        raise ValueError(
            f"目前不支援的圖片格式：{mime_type}"
        )


    # ========================================================
    # 建立 Gemini Client
    # ========================================================

    client = genai.Client(
        api_key=key
    )


    # ========================================================
    # 冰箱照片辨識 Prompt
    # ========================================================

    prompt = """
你是一位專業的冰箱食材影像辨識助手。

請仔細分析使用者提供的照片，
辨識照片中實際可以看到的食材。

所有內容必須使用繁體中文。

請依照以下原則分類：

【confirmed_items】
只放你可以明確確認的食材。

例如：
雞蛋
番茄
高麗菜
牛奶
馬鈴薯


【possible_items】
看起來可能是某項食材，
但是因為遮擋、角度、包裝或影像品質，
無法百分之百確認的項目。


【needs_confirmation】
無法正確確認內容的物品。

例如：
包裝標籤看不清楚的盒裝食品
被塑膠袋完全遮住的食材
無法確認種類的肉品


【overall_note】
使用繁體中文簡短說明本次辨識狀況。


請嚴格遵守：

1. 不清楚的食材不要自行猜測。

2. 不要因為包裝顏色就判斷內容物。

3. 不要推測照片以外看不到的食材。

4. 食材名稱使用台灣常用繁體中文。

5. 肉品如果無法明確辨識種類，
   不要自行判斷成豬肉、牛肉或雞肉。

6. 魚類如果無法確認品種，
   可以使用「魚」或「魚類」。

7. 不要把下列物品當成食材：
   冰箱層架
   塑膠袋
   保鮮盒
   盤子
   碗
   紙巾
   包裝容器

8. 如果圖片不是冰箱照片，
   但確實包含食材，
   仍然可以辨識可見食材。

9. 如果完全沒有可辨識食材，
   confirmed_items 可以是空陣列。

10. 不要輸出 Markdown。
"""


    # ========================================================
    # 將圖片 bytes 轉成 Gemini Part
    # ========================================================

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )


    # ========================================================
    # 呼叫 Gemini
    # ========================================================

    try:

        response = client.models.generate_content(
            model=model,
            contents=[
                image_part,
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FridgeRecognitionResult,
                temperature=0.2
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Gemini 冰箱照片辨識失敗："
            f"{error}"
        ) from error


    # ========================================================
    # 檢查回傳結果
    # ========================================================

    if response is None:

        raise ValueError(
            "Gemini 沒有回傳冰箱辨識資料。"
        )


    # ========================================================
    # 優先使用 SDK 已解析的結果
    # ========================================================

    parsed = response.parsed

    if isinstance(
        parsed,
        FridgeRecognitionResult
    ):

        return parsed.model_dump()


    # ========================================================
    # 如果 SDK 回傳 dict
    # ========================================================

    if isinstance(
        parsed,
        dict
    ):

        result = (
            FridgeRecognitionResult
            .model_validate(
                parsed
            )
        )

        return result.model_dump()


    # ========================================================
    # parsed 不可用時，嘗試解析 response.text
    # ========================================================

    if response.text:

        try:

            result = (
                FridgeRecognitionResult
                .model_validate_json(
                    response.text
                )
            )

            return result.model_dump()

        except Exception as error:

            raise ValueError(
                "Gemini 有回傳內容，"
                "但冰箱辨識結果格式不正確。"
                f"\n詳細錯誤：{error}"
            ) from error


    # ========================================================
    # 完全沒有有效結果
    # ========================================================

    raise ValueError(
        "Gemini 沒有回傳有效的冰箱辨識結果。"
    )