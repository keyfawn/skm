import json

from betterconf import Config as Con, field
from betterconf.config import AbstractProvider
from bot.utils.log import get_logger
import logging


def _raise(ex: str):
    get_logger('bot')
    logging.critical(ex)
    exit(1)


def _get_config(json_file):
    class JSONProvider(AbstractProvider):
        def __init__(self):
            with open(json_file, "r") as f:
                self._settings = json.load(f)

        def get(self, name):
            return self._settings.get(name)

    return JSONProvider()


class EnAdminConfig(Con):
    _provider = _get_config("bot/locales/en/admin.json")

    ru_locale = field("ru_locale",
                      default=lambda: _raise('not found text "ru_locale" in admin.json'),
                      provider=_provider).value
    en_locale = field("en_locale",
                      default=lambda: _raise('not found text "en_locale" in admin.json'),
                      provider=_provider).value

    admin_panel = field("admin_panel",
                        default=lambda: _raise('not found text "admin_panel" in admin.json'),
                        provider=_provider).value

    btn_show_stat = field("btn_show_stat",
                          default=lambda: _raise('not found text "btn_show_stat" in admin.json'),
                          provider=_provider).value
    btn_users = field("btn_users",
                      default=lambda: _raise('not found text "btn_users" in admin.json'),
                      provider=_provider).value
    btn_mailing = field("btn_mailing",
                        default=lambda: _raise('not found text "btn_mailing" in admin.json'),
                        provider=_provider).value
    btn_auto_mailing = field("btn_auto_mailing",
                             default=lambda: _raise('not found text "btn_auto_mailing" in admin.json'),
                             provider=_provider).value
    btn_products = field("btn_products",
                         default=lambda: _raise('not found text "btn_products" in admin.json'),
                         provider=_provider).value

    inline_auto_mail = field("inline_auto_mail",
                             default=lambda: _raise('not found text "inline_auto_mail" in admin.json'),
                             provider=_provider).value
    inline_auto_mail_add = field("inline_auto_mail_add",
                                 default=lambda: _raise('not found text "inline_auto_mail_add" in admin.json'),
                                 provider=_provider).value
    inline_auto_mail_delete = field("inline_auto_mail_delete",
                                    default=lambda: _raise('not found text "inline_auto_mail_delete" in admin.json'),
                                    provider=_provider).value
    inline_auto_mail_cancel = field("inline_auto_mail_cancel",
                                    default=lambda: _raise('not found text "inline_auto_mail_cancel" in admin.json'),
                                    provider=_provider).value
    inline_mail_with_btn = field("inline_mail_with_btn",
                                 default=lambda: _raise('not found text "inline_mail_with_btn" in admin.json'),
                                 provider=_provider).value
    inline_mail_without_btn = field("inline_mail_without_btn",
                                    default=lambda: _raise('not found text "inline_mail_without_btn" in admin.json'),
                                    provider=_provider).value
    inline_yes = field("inline_yes",
                       default=lambda: _raise('not found text "inline_yes" in admin.json'),
                       provider=_provider).value
    inline_product_new = field("inline_product_new",
                               default=lambda: _raise('not found text "inline_product_new" in admin.json'),
                               provider=_provider).value
    inline_ok_delete = field("inline_ok_delete",
                             default=lambda: _raise('not found text "inline_ok_delete" in admin.json'),
                             provider=_provider).value
    inline_add = field("inline_add",
                       default=lambda: _raise('not found text "inline_add" in admin.json'),
                       provider=_provider).value
    inline_view_user = field("inline_view_user",
                             default=lambda: _raise('not found text "inline_view_user" in admin.json'),
                             provider=_provider).value
    inline_balance_user = field("inline_balance_user",
                                default=lambda: _raise('not found text "inline_balance_user" in admin.json'),
                                provider=_provider).value

    start = field("start", default=lambda: _raise('not found text "start" in admin.json'),
                  provider=_provider).value
    pre_spam = field("pre_spam", default=lambda: _raise('not found text "pre_spam" in admin.json'),
                     provider=_provider).value
    spam = field("spam", default=lambda: _raise('not found text "spam" in admin.json'),
                 provider=_provider).value

    all_products = field("all_products", default=lambda: _raise('not found text "all_products" in admin.json'),
                         provider=_provider).value

    new_user = field("new_user", default=lambda: _raise('not found text "new_user" in admin.json'),
                     provider=_provider).value
    new_upper = field("new_upper", default=lambda: _raise('not found text "new_upper" in admin.json'),
                      provider=_provider).value

    new_product_photo = field("new_product_photo",
                              default=lambda: _raise('not found text "new_product_photo" in admin.json'),
                              provider=_provider).value
    new_product_title = field("new_product_title",
                              default=lambda: _raise('not found text "new_product_title" in admin.json'),
                              provider=_provider).value
    new_product_desc = field("new_product_desc",
                             default=lambda: _raise('not found text "new_product_desc" in admin.json'),
                             provider=_provider).value
    new_product_price = field("new_product_price",
                              default=lambda: _raise('not found text "new_product_price" in admin.json'),
                              provider=_provider).value
    new_product_count = field("new_product_count",
                              default=lambda: _raise('not found text "new_product_count" in admin.json'),
                              provider=_provider).value
    new_product_check = field("new_product_check",
                              default=lambda: _raise('not found text "new_product_check" in admin.json'),
                              provider=_provider).value
    new_product_example = field("new_product_example",
                                default=lambda: _raise('not found text "new_product_example" in admin.json'),
                                provider=_provider).value
    new_product_add = field("new_product_add",
                            default=lambda: _raise('not found text "new_product_add" in admin.json'),
                            provider=_provider).value
    pre_delete_product = field("pre_delete_product",
                               default=lambda: _raise('not found text "pre_delete_product" in admin.json'),
                               provider=_provider).value
    delete_product = field("delete_product",
                           default=lambda: _raise('not found text "delete_product" in admin.json'),
                           provider=_provider).value

    mailing_with_btn = field("mailing_with_btn",
                             default=lambda: _raise('not found text "mailing_with_btn" in admin.json'),
                             provider=_provider).value
    mailing_markup = field("mailing_markup",
                           default=lambda: _raise('not found text "mailing_markup" in admin.json'),
                           provider=_provider).value
    mailing_text = field("mailing_text",
                         default=lambda: _raise('not found text "mailing_text" in admin.json'),
                         provider=_provider).value
    mailing_check = field("mailing_check",
                          default=lambda: _raise('not found text "mailing_check" in admin.json'),
                          provider=_provider).value
    mailing_finish = field("mailing_finish",
                           default=lambda: _raise('not found text "mailing_finish" in admin.json'),
                           provider=_provider).value
    mailing_stat = field("mailing_stat",
                         default=lambda: _raise('not found text "mailing_stat" in admin.json'),
                         provider=_provider).value

    auto_mailing = field("auto_mailing",
                         default=lambda: _raise('not found text "auto_mailing" in admin.json'),
                         provider=_provider).value
    auto_mail = field("auto_mail",
                      default=lambda: _raise('not found text "auto_mail" in admin.json'),
                      provider=_provider).value
    auto_mail_add_time = field("auto_mail_add_time",
                               default=lambda: _raise('not found text "auto_mail_add_time" in admin.json'),
                               provider=_provider).value
    auto_mailing_finish = field("auto_mailing_finish",
                                default=lambda: _raise('not found text "auto_mailing_finish" in admin.json'),
                                provider=_provider).value
    auto_mail_delete = field("auto_mail_delete",
                             default=lambda: _raise('not found text "auto_mail_delete" in admin.json'),
                             provider=_provider).value

    all_users = field("all_users",
                      default=lambda: _raise('not found text "all_users" in admin.json'),
                      provider=_provider).value
    user = field("user",
                 default=lambda: _raise('not found text "user" in admin.json'),
                 provider=_provider).value
    balance_user = field("balance_user",
                         default=lambda: _raise('not found text "balance_user" in admin.json'),
                         provider=_provider).value
    balance_user_ok = field("balance_user_ok",
                            default=lambda: _raise('not found text "balance_user_ok" in admin.json'),
                            provider=_provider).value

    stat = field("stat",
                 default=lambda: _raise('not found text "stat" in admin.json'),
                 provider=_provider).value


class EnUserConfig(Con):
    _provider = _get_config("bot/locales/en/user.json")

    ru_locale = field("ru_locale",
                      default=lambda: _raise('not found text "ru_locale" in user.json'),
                      provider=_provider).value
    en_locale = field("en_locale",
                      default=lambda: _raise('not found text "en_locale" in user.json'),
                      provider=_provider).value

    btn_products = field("btn_products",
                         default=lambda: _raise('not found text "btn_products" in user.json'),
                         provider=_provider).value
    btn_shopping = field("btn_shopping",
                         default=lambda: _raise('not found text "btn_shopping" in user.json'),
                         provider=_provider).value
    btn_profile = field("btn_profile",
                        default=lambda: _raise('not found text "btn_profile" in user.json'),
                        provider=_provider).value
    btn_about = field("btn_about",
                      default=lambda: _raise('not found text "btn_about" in user.json'),
                      provider=_provider).value
    inline_product_buy = field("inline_product_buy",
                               default=lambda: _raise('not found text "inline_product_buy" in user.json'),
                               provider=_provider).value
    inline_balance = field("inline_balance",
                           default=lambda: _raise('not found text "inline_balance" in user.json'),
                           provider=_provider).value
    inline_pay_balance = field("inline_pay_balance",
                               default=lambda: _raise('not found text "inline_pay_balance" in user.json'),
                               provider=_provider).value

    start = field("start", default=lambda: _raise('not found text "start" in user.json'),
                  provider=_provider).value
    pre_spam = field("pre_spam", default=lambda: _raise('not found text "pre_spam" in user.json'),
                     provider=_provider).value
    spam = field("spam", default=lambda: _raise('not found text "spam" in user.json'),
                 provider=_provider).value

    about = field("about", default=lambda: _raise('not found text "about" in user.json'),
                  provider=_provider).value

    small_balance = field("small_balance", default=lambda: _raise('not found text "small_balance" in user.json'),
                          provider=_provider).value
    product = field("product", default=lambda: _raise('not found text "product" in user.json'),
                    provider=_provider).value
    non_product = field("non_product", default=lambda: _raise('not found text "non_product" in user.json'),
                        provider=_provider).value
    product_end = field("product_end", default=lambda: _raise('not found text "product_end" in user.json'),
                        provider=_provider).value

    profile = field("profile", default=lambda: _raise('not found text "profile" in user.json'),
                    provider=_provider).value
    method_balance = field("method_balance", default=lambda: _raise('not found text "method_balance" in user.json'),
                           provider=_provider).value
    crypto_method = field("crypto_method", default=lambda: _raise('not found text "crypto_method" in user.json'),
                          provider=_provider).value
    epay_method = field("epay_method", default=lambda: _raise('not found text "epay_method" in user.json'),
                        provider=_provider).value
    pay_balance = field("pay_balance", default=lambda: _raise('not found text "pay_balance" in user.json'),
                        provider=_provider).value
    upper_balance = field("upper_balance", default=lambda: _raise('not found text "upper_balance" in user.json'),
                          provider=_provider).value


user = EnUserConfig()
admin = EnAdminConfig()
