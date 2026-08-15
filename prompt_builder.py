def build_recipe_prompt(
    ingredients: list[str],
    servings: int,
    max_minutes: int,
    equipment: list[str],
    restrictions: list[str],
    cuisine: str,
    recipe_count: int = 2,
) -> str:
    ingredient_text = "、".join(ingredients) if ingredients else "未提供"
    equipment_text = "、".join(equipment) if equipment else "未提供"
    restriction_text = "、".join(restrictions) if restrictions else "無"

    return f"""
你是一位熟悉中式、西式與融合家庭料理的料理教師。

# 任務
請依照使用者條件設計 {recipe_count} 道候選料理。

# 使用者條件
現有食材：{ingredient_text}
用餐人數：{servings} 人
最長時間：{max_minutes} 分鐘
現有設備：{equipment_text}
飲食限制：{restriction_text}
料理風格：{cuisine}

# 必須遵守
1. 不得違反使用者的過敏、飲食或禁用食材限制。
2. 不得假裝使用者擁有未列出的主要設備。
3. 主要食材若使用者沒有，必須列入 shopping_items，不可假裝已存在。
4. 鹽、胡椒、食用油、醬油等常見基礎調味料可以合理使用；其他材料若未提供，請列入 shopping_items。
5. total_minutes 必須盡量不超過 {max_minutes} 分鐘。
6. 食材表中的每一項食材都必須實際出現在步驟中。
7. 步驟中的主要食材不得漏列於食材表。
8. 必須列出可能的過敏原。
9. 資訊不足時加入 needs_confirmation，不可自行把不確定資訊當成事實。
10. 不提供疾病診斷或治療建議。
11. 食品安全資訊不確定時，應在 safety_notes 說明需要依食品標示或專業建議確認。
12. 內容要能讓一般家庭料理使用者實際操作。
13. 所有文字內容必須使用繁體中文。
14. recommendation_reason 必須清楚說明為何推薦這一道料理，
    並根據現有食材、設備、料理時間與飲食限制說明。
""".strip()
