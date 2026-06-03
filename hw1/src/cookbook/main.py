from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from cookbook import models, schemas
from cookbook.database import (
    DEFAULT_DATABASE_URL,
    Base,
    create_engine,
    create_session_factory,
    get_session,
)


RecipeId = Annotated[
    int,
    Path(
        ...,
        ge=1,
        title="Recipe ID",
        description="Positive recipe identifier.",
    ),
]


def recipe_detail(recipe: models.Recipe) -> schemas.RecipeDetail:
    return schemas.RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        ingredients=recipe.ingredients,
        description=recipe.description,
        views=recipe.views,
    )


def recipe_list_item(recipe: models.Recipe) -> schemas.RecipeListItem:
    return schemas.RecipeListItem(
        id=recipe.id,
        title=recipe.title,
        views=recipe.views,
        cooking_time=recipe.cooking_time,
    )


def create_app(database_url: str = DEFAULT_DATABASE_URL) -> FastAPI:
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title="Cookbook API",
        description="Async API for storing recipes and tracking recipe popularity.",
        version="1.0.0",
        lifespan=lifespan,
    )

    async def db_session() -> AsyncIterator[AsyncSession]:
        async for session in get_session(session_factory):
            yield session

    SessionDep = Annotated[AsyncSession, Depends(db_session)]

    @app.post(
        "/recipes",
        response_model=schemas.RecipeDetail,
        status_code=status.HTTP_201_CREATED,
        summary="Create a recipe",
        response_description="Created recipe with a generated identifier.",
    )
    async def create_recipe(
        recipe: schemas.RecipeCreate,
        session: SessionDep,
    ) -> schemas.RecipeDetail:
        new_recipe = models.Recipe(
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            ingredients=recipe.ingredients,
            description=recipe.description,
        )
        session.add(new_recipe)
        await session.commit()
        await session.refresh(new_recipe)
        return recipe_detail(new_recipe)

    @app.get(
        "/recipes",
        response_model=list[schemas.RecipeListItem],
        summary="Get recipe list",
        response_description="Recipes sorted by popularity and cooking time.",
    )
    async def get_recipes(session: SessionDep) -> list[schemas.RecipeListItem]:
        query = select(models.Recipe).order_by(
            desc(models.Recipe.views),
            models.Recipe.cooking_time,
        )
        result = await session.execute(query)
        return [recipe_list_item(recipe) for recipe in result.scalars().all()]

    @app.get(
        "/recipes/{recipe_id}",
        response_model=schemas.RecipeDetail,
        summary="Get recipe details",
        response_description=(
            "Detailed recipe information. Recipe views are incremented."
        ),
    )
    async def get_recipe(
        recipe_id: RecipeId,
        session: SessionDep,
    ) -> schemas.RecipeDetail:
        result = await session.execute(
            select(models.Recipe).where(models.Recipe.id == recipe_id)
        )
        recipe = result.scalar_one_or_none()
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found",
            )

        recipe.views += 1
        await session.commit()
        await session.refresh(recipe)
        return recipe_detail(recipe)

    return app


app = create_app()
