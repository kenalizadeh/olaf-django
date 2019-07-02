from modeltranslation.translator import translator, TranslationOptions
from merchant.models import (
        Restaurant,
        MenuItemCategory,
        MenuItem,
        MenuItemOption,
        MenuItemType
    )


class MenuItemCategoryTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )

translator.register(MenuItemCategory, MenuItemCategoryTranslationOptions)


class MenuItemTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'description',
    )

translator.register(MenuItem, MenuItemTranslationOptions)


class MenuItemOptionTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )

translator.register(MenuItemOption, MenuItemOptionTranslationOptions)


class MenuItemTypeTranslationOptions(TranslationOptions):
    fields = (
        'name',
    )

translator.register(MenuItemType, MenuItemTypeTranslationOptions)
