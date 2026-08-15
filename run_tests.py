import csv
import sys

from llm_service import generate_recipes
from test_cases import TEST_CASES
from validators import validate_recipe


def main():
    limit = len(TEST_CASES)
    if len(sys.argv) >= 2:
        limit = max(1, min(int(sys.argv[1]), len(TEST_CASES)))

    selected_cases = TEST_CASES[:limit]
    rows = []

    for index, case in enumerate(selected_cases, start=1):
        print(f"[{index}/{len(selected_cases)}] {case['name']}")

        try:
            result = generate_recipes(
                ingredients=case["ingredients"],
                servings=case["servings"],
                max_minutes=case["max_minutes"],
                equipment=case["equipment"],
                restrictions=case["restrictions"],
                cuisine=case["cuisine"],
                recipe_count=1,
            )

            recipe = result.recipes[0]
            warnings = validate_recipe(recipe, case["max_minutes"])
            status = "成功" if not warnings else "部分成功"

            rows.append({
                "case": case["name"],
                "status": status,
                "recipe": recipe.recipe_name,
                "warnings": " | ".join(warnings),
            })

        except Exception as exc:
            rows.append({
                "case": case["name"],
                "status": "失敗",
                "recipe": "",
                "warnings": str(exc),
            })

    with open("test_results.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["case", "status", "recipe", "warnings"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n完成，結果已寫入 test_results.csv")


if __name__ == "__main__":
    main()
