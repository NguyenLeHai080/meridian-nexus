from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LoginInput(StrictModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class RegisterInput(LoginInput):
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=12, max_length=200)
    password_confirmation: str = Field(min_length=12, max_length=200)

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterInput":
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match.")
        return self


class EmailActionInput(StrictModel):
    email: EmailStr


class TokenInput(StrictModel):
    token: str = Field(min_length=32, max_length=200)


class PasswordResetInput(TokenInput):
    email: EmailStr
    password: str = Field(min_length=12, max_length=200)
    password_confirmation: str = Field(min_length=12, max_length=200)

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordResetInput":
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match.")
        return self


class MfaCodeInput(StrictModel):
    code: str = Field(min_length=6, max_length=32)


class MfaSetupInput(StrictModel):
    password: str = Field(min_length=1, max_length=200)
    current_code: str | None = Field(default=None, min_length=6, max_length=32)


class MfaChallengeInput(MfaCodeInput):
    challenge_token: str = Field(min_length=32, max_length=200)


class ContactInput(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    subject: str = Field(min_length=1, max_length=180)
    message: str = Field(min_length=1, max_length=5000)


class ChatStartInput(StrictModel):
    name: str | None = Field(default=None, max_length=120)
    email: EmailStr | None = None
    message: str = Field(min_length=1, max_length=2000)


class ChatReplyInput(StrictModel):
    message: str = Field(min_length=1, max_length=2000)


class CheckoutItem(StrictModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class ShippingAddress(StrictModel):
    line: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=120)
    country: str = Field(min_length=1, max_length=120)


class CheckoutInput(StrictModel):
    items: list[CheckoutItem] = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=3, max_length=30)
    address: ShippingAddress
    promotion_code: str | None = Field(default=None, max_length=50)


class ProfileUpdateInput(StrictModel):
    name: str = Field(min_length=2, max_length=100)


class CategoryInput(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class CategoryUpdateInput(CategoryInput):
    slug: str = Field(min_length=1, max_length=140)
    is_active: bool


class ProductInput(StrictModel):
    name: str = Field(min_length=1, max_length=180)
    sku: str = Field(min_length=1, max_length=80)
    category_id: int | None = None
    price: Decimal = Field(ge=0)
    sale_price: Decimal | None = Field(default=None, ge=0)
    stock: int = Field(ge=0)
    images: list[HttpUrl] = Field(default_factory=list, max_length=20)
    excerpt: str | None = Field(default=None, max_length=300)
    description: str | None = None
    is_featured: bool = False
    status: str = Field(pattern="^(draft|published|archived)$")
    published_at: datetime | None = None


class PromotionInput(StrictModel):
    name: str = Field(min_length=1, max_length=150)
    code: str | None = Field(default=None, max_length=50)
    type: str = Field(pattern="^(percent|fixed)$")
    value: Decimal = Field(gt=0)
    minimum_order: Decimal = Field(default=0, ge=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_active: bool = True


class OrderUpdateInput(StrictModel):
    status: str = Field(pattern="^(pending|confirmed|processing|shipped|completed|cancelled)$")
    payment_status: str = Field(pattern="^(unpaid|paid|refunded)$")


class RolesUpdateInput(StrictModel):
    roles: list[str] = Field(min_length=1, max_length=10)


class PostInput(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, max_length=220)
    excerpt: str | None = Field(default=None, max_length=350)
    content: str = Field(min_length=1)
    cover_image: HttpUrl | None = None
    status: str = Field(pattern="^(draft|published|archived)$")
    published_at: datetime | None = None


class ContactStatusInput(StrictModel):
    status: str = Field(pattern="^(new|in_progress|resolved|spam)$")
