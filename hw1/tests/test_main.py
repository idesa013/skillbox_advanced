from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from cookbook.main import create_app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    app = create_app("sqlite+aiosqlite:///:memory:")

    with TestClient(app) as test_client:
        yield test_client


def create_recipe(
    client: TestClient,
    title: str,
    cooking_time: int,
) -> dict[str, Any]:
    response = client.post(
        "/recipes",
        json={
            "title": title,
            "cooking_time": cooking_time,
            "ingredients": ["ingredient"],
            "description": f"{title} description",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    return cast(dict[str, Any], response.json())


def test_create_recipe_returns_created_recipe(client: TestClient) -> None:
    recipe = create_recipe(client, "Pancakes", 20)

    assert recipe["id"] == 1
    assert recipe["title"] == "Pancakes"
    assert recipe["cooking_time"] == 20
    assert recipe["ingredients"] == ["ingredient"]
    assert recipe["description"] == "Pancakes description"
    assert recipe["views"] == 0


def test_get_recipe_increments_views(client: TestClient) -> None:
    recipe = create_recipe(client, "Soup", 45)

    first_response = client.get(f"/recipes/{recipe['id']}")
    second_response = client.get(f"/recipes/{recipe['id']}")

    assert first_response.status_code == status.HTTP_200_OK
    assert first_response.json()["views"] == 1
    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()["views"] == 2


def test_get_recipes_sorts_by_views_desc_and_cooking_time_asc(
    client: TestClient,
) -> None:
    slow_recipe = create_recipe(client, "Slow stew", 120)
    popular_recipe = create_recipe(client, "Popular salad", 15)
    fast_recipe = create_recipe(client, "Fast toast", 5)

    client.get(f"/recipes/{popular_recipe['id']}")
    client.get(f"/recipes/{popular_recipe['id']}")
    client.get(f"/recipes/{slow_recipe['id']}")

    response = client.get("/recipes")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": popular_recipe["id"],
            "title": "Popular salad",
            "views": 2,
            "cooking_time": 15,
        },
        {
            "id": slow_recipe["id"],
            "title": "Slow stew",
            "views": 1,
            "cooking_time": 120,
        },
        {
            "id": fast_recipe["id"],
            "title": "Fast toast",
            "views": 0,
            "cooking_time": 5,
        },
    ]


def test_get_recipes_sorts_equal_views_by_cooking_time(client: TestClient) -> None:
    create_recipe(client, "Long pasta", 40)
    create_recipe(client, "Quick eggs", 8)

    response = client.get("/recipes")

    assert response.status_code == status.HTTP_200_OK
    assert [recipe["title"] for recipe in response.json()] == [
        "Quick eggs",
        "Long pasta",
    ]


def test_unknown_recipe_returns_404(client: TestClient) -> None:
    response = client.get("/recipes/404")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Recipe not found"}
