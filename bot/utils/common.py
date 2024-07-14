from enum import Enum

from aiogram.filters.callback_data import CallbackData


class ProductCallbackFactory(CallbackData, prefix="product"):
    id: int
    marked: bool = False


class ButtonCallbackFactory(CallbackData, prefix="button"):
    status: int


class AutoButtonCallbackFactory(CallbackData, prefix="auto_button"):
    status: int


class DeleteAutoMailingCallbackFactory(CallbackData, prefix="auto_mail_delete"):
    id: int


class AutoMailingCallbackFactory(CallbackData, prefix="auto_mail"):
    id: int


class AutoMailingStatus(str, Enum):
    add = 'add'
    cancel = 'cancel'


class AutoMailingStatusFactory(CallbackData, prefix="auto_mailing"):
    status: AutoMailingStatus


class ProductStatus(str, Enum):
    add = 'add'
    all_products = 'all_products'
    marked = 'marked'
    delete = 'delete'


class ProductDelete(CallbackData, prefix="product_delete"):
    id: int


class NewProductAdd(CallbackData, prefix="new_product_add"):
    title: str


class ProductStatusCallbackFactory(CallbackData, prefix="product_stat"):
    status: ProductStatus
    marked: bool = False


class UserCallbackFactory(CallbackData, prefix="user"):
    id: int


class BalanceUserCallbackFactory(CallbackData, prefix="balance_user"):
    id: int


class MethodStatus(str, Enum):
    crypto = 'crypto'
    epay = 'epay'


class MethodBalanceCallbackFactory(CallbackData, prefix="method_balance"):
    method: MethodStatus


class UserStatus(str, Enum):
    cancel = 'cancel'


class UserStatusCallbackFactory(CallbackData, prefix="user_status"):
    status: UserStatus


class SideProductStatus(str, Enum):
    left = 'left'
    right = 'right'
    buy = 'buy'


class SideProductCallbackFactory(CallbackData, prefix="side_product"):
    status: SideProductStatus
    product_id: int
