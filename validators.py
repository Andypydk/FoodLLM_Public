def validate_recipe(recipe, max_minutes: int) -> list[str]:
    warnings = []

    if recipe.total_minutes > max_minutes:
        warnings.append(
            f"總時間 {recipe.total_minutes} 分鐘超過使用者限制 {max_minutes} 分鐘。"
        )

    ingredient_names = {
        item.name.strip().lower()
        for item in recipe.ingredients
        if item.name.strip()
    }

    if not recipe.steps:
        warnings.append("沒有料理步驟。")

    if not recipe.ingredients:
        warnings.append("沒有食材資料。")

    if not recipe.allergens:
        warnings.append("模型未列出過敏原；請人工再次確認食品標示。")

    step_total = sum(step.minutes for step in recipe.steps)
    if step_total > recipe.total_minutes + 10:
        warnings.append(
            f"各步驟時間合計 {step_total} 分鐘，與總時間 {recipe.total_minutes} 分鐘差異較大。"
        )

    if len(ingredient_names) != len(recipe.ingredients):
        warnings.append("食材表可能有重複項目。")

    return warnings
