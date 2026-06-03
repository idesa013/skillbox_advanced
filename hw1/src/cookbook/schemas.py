from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
        title="Recipe title",
        description="Short human-readable recipe name.",
        examples=["Pancakes"],
    )
    cooking_time: int = Field(
        ...,
        gt=0,
        title="Cooking time",
        description="Cooking time in minutes.",
        examples=[25],
    )
    ingredients: list[str] = Field(
        ...,
        title="Ingredients",
        description="List of ingredients required for the recipe.",
        examples=[["flour", "milk", "eggs"]],
    )
    description: str = Field(
        ...,
        min_length=1,
        title="Description",
        description="Step-by-step text description of the recipe.",
        examples=["Mix all ingredients and fry on a hot pan until golden."],
    )


class RecipeCreate(RecipeBase):
    """Request body for creating a recipe."""


class RecipeListItem(BaseModel):
    id: int = Field(..., description="Unique recipe identifier.", examples=[1])
    title: str = Field(..., description="Recipe title.", examples=["Pancakes"])
    views: int = Field(..., description="Number of detail-page opens.", examples=[4])
    cooking_time: int = Field(
        ...,
        description="Cooking time in minutes.",
        examples=[25],
    )


class RecipeDetail(RecipeBase):
    id: int = Field(..., description="Unique recipe identifier.", examples=[1])
    views: int = Field(..., description="Number of detail-page opens.", examples=[5])
