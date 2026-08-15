from llm_service import generate_recipes


def split_items(text: str) -> list[str]:
    text = text.replace("，", ",")
    return [item.strip() for item in text.split(",") if item.strip()]


print("=== 冰箱食材 AI 料理助手 ===")

ingredients = split_items(input("請輸入現有食材（逗號分隔）："))
servings = int(input("請輸入用餐人數："))
max_minutes = int(input("請輸入最長料理時間（分鐘）："))
equipment = split_items(input("請輸入現有設備（逗號分隔）："))
restrictions = split_items(input("請輸入飲食限制（沒有可直接 Enter）："))
cuisine = input("請輸入料理風格（中式/西式/融合）：").strip() or "中式"

print("\nAI 正在產生食譜...\n")

try:
    result = generate_recipes(
        ingredients=ingredients,
        servings=servings,
        max_minutes=max_minutes,
        equipment=equipment,
        restrictions=restrictions,
        cuisine=cuisine,
        recipe_count=2,
    )

    for index, recipe in enumerate(result.recipes, start=1):
        print("=" * 50)
        print(f"候選料理 {index}：{recipe.recipe_name}")
        print(f"料理風格：{recipe.cuisine}")
        print(f"份數：{recipe.servings}")
        print(f"總時間：{recipe.total_minutes} 分鐘")

        print("\n食材：")
        for item in recipe.ingredients:
            note = f"（{item.note}）" if item.note else ""
            print(f"- {item.name}：{item.amount}{note}")

        print("\n設備：")
        for item in recipe.equipment:
            print(f"- {item}")

        print("\n步驟：")
        for step in recipe.steps:
            print(f"{step.step}. {step.instruction}（約 {step.minutes} 分鐘）")

        print("\n缺少／採買項目：")
        if recipe.shopping_items:
            for item in recipe.shopping_items:
                print(f"- {item}")
        else:
            print("- 無")

        print("\n過敏原：")
        print("、".join(recipe.allergens) if recipe.allergens else "未辨識到明確過敏原")

        print("\n需要確認：")
        if recipe.needs_confirmation:
            for item in recipe.needs_confirmation:
                print(f"- {item}")
        else:
            print("- 無")

        print("\n安全提醒：")
        if recipe.safety_notes:
            for item in recipe.safety_notes:
                print(f"- {item}")
        else:
            print("- 無")

    print("\n整體說明：")
    print(result.overall_note)

except Exception as exc:
    print("發生錯誤：", exc)
