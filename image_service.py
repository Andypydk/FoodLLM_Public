import base64

from openai import OpenAI


def generate_recipe_image(
    recipe_name: str,
    ingredients: list[str],
    cuisine: str,
    api_key: str
) -> bytes:

    client = OpenAI(api_key=api_key)

    ingredient_text = "、".join(ingredients)

    prompt = f"""
請產生一張真實自然、具有食慾的家庭料理攝影照片。

料理名稱：{recipe_name}
料理風格：{cuisine}
主要食材：{ingredient_text}

圖片要求：
- 真實食物攝影風格
- 料理外觀必須符合料理名稱
- 食材必須合理呈現在料理中
- 家庭料理擺盤
- 自然光
- 約 45 度角或俯視攝影
- 背景乾淨簡潔
- 不要人物
- 不要文字
- 不要浮水印
- 不要菜單
"""

    result = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json

    image_bytes = base64.b64decode(image_base64)

    return image_bytes