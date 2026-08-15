import base64
import json

from openai import OpenAI


def recognize_fridge_items(
    image_bytes: bytes,
    api_key: str,
    model: str = "gpt-5.6-luna"
) -> dict:
    """
    辨識冰箱照片中的食材。
    回傳格式：
    {
        "confirmed_items": [...],
        "possible_items": [...],
        "needs_confirmation": [...],
        "overall_note": "..."
    }
    """

    client = OpenAI(api_key=api_key)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
你是一位冰箱食材辨識助手。

請根據使用者提供的冰箱照片，辨識可見的食材。
請務必使用繁體中文回覆，並且只回傳 JSON，不要加上其他說明文字。

請將結果分成以下四個欄位：
1. confirmed_items：你很確定看到的食材
2. possible_items：你不完全確定，但有可能的食材
3. needs_confirmation：你認為需要使用者再確認的項目
4. overall_note：整體辨識說明

注意：
- 若看不清楚，不要亂猜
- 可以辨識常見食材，例如雞蛋、牛奶、番茄、青菜、豆腐、肉類、水果、醬料等
- 若是包裝食品但無法明確辨識內容，可放入 needs_confirmation
- 不要輸出 markdown
- 只輸出 JSON

JSON 格式範例：
{
  "confirmed_items": ["雞蛋", "牛奶"],
  "possible_items": ["起司"],
  "needs_confirmation": ["一盒綠色蔬菜"],
  "overall_note": "照片中可辨識到雞蛋與牛奶，另有部分食材較不清楚。"
}
"""

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            }
        ]
    )

    text = response.output_text.strip()

    # 若模型回傳 ```json ... ```，先去掉包裝
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)

    return {
        "confirmed_items": data.get("confirmed_items", []),
        "possible_items": data.get("possible_items", []),
        "needs_confirmation": data.get("needs_confirmation", []),
        "overall_note": data.get("overall_note", "")
    }