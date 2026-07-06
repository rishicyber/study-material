from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


class User(BaseModel):
    fname: str
    lname: str
    age: int = Field(
        title="This is the age field",
        description="This is the age of user, it should be greater than 0",
        gt=0,
    )


class Image(BaseModel):
    name: str
    url: HttpUrl


class Product(BaseModel):
    name: str = Field(
        default="Nokia",
        title="product name",
        description="This is the name of the product",
        min_length=2,
    )
    price: int = Field(
        title="product name", description="This is the name of the product", ge=0
    )
    tags: set[str] = set()
    image: list[Image]

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "iPhone",
    #             "price": 10000,
    #             "tags": ["apple", "mobile"],
    #             "image": [
    #                 {"name": "phone_front_view", "url": "https://google.com/"},
    #                 {"name": "phone_side_view", "url": "https://google.com/"},
    #             ]
    #         }
    #     }

    # Modern Pydantic v2 configuration
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "iPhone",  # Optional: BaseModel has default value assigned
                    "price": 10000,
                    "tags": ["apple", "mobile"],
                    "image": [
                        {"name": "phone_front_view", "url": "https://google.com/"},
                        {"name": "phone_side_view", "url": "https://google.com/"},
                    ],
                }
            ]
        }
    }


class Offer(BaseModel):
    name: str
    description: str
    products: list[Product]


@app.post("/add_product_image")
def add_product_with_image(product: Product):
    return {"new_product_with_image": product}


@app.post("/offer")
def offer_on_products(offer: Offer):
    return {"offer": offer}


@app.post("/user/{uid}")
def add_user(uid: int, profile_id: int, user: User, product: Product):
    user.age += 5
    return {"uid": uid, "profile_id": profile_id, "user": user, "product": product}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
