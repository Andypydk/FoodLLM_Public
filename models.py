from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    name: str = Field(description="食材名稱")
    amount: str = Field(description="精確份量，例如 2 顆、150 克")
    note: str = Field(default="", description="備註，可留空")


class CookingStep(BaseModel):
    step: int
    instruction: str
    minutes: int = Field(ge=0)


class Recipe(BaseModel):
    recipe_name: str
    recommendation_reason: str
    cuisine: str
    servings: int
    ingredients: list[Ingredient]
    equipment: list[str]
    steps: list[CookingStep]
    total_minutes: int
    shopping_items: list[str]
    allergens: list[str]
    needs_confirmation: list[str]
    safety_notes: list[str]


class RecipeResult(BaseModel):
    recipes: list[Recipe]
    overall_note: str
