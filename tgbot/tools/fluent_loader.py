from pathlib import Path
from fluent.runtime import FluentLocalization, FluentResourceLoader


def get_fluent_localization(language_code: str) -> FluentLocalization:
    """
    Загружает файл локализации из папки 'l10n' на основе кода языка.
    """
    locale_dir = Path(__file__).parent.joinpath("l10n")
    if not locale_dir.exists():
        raise FileNotFoundError(f"Директория локализаций '{locale_dir}' не найдена.")

    # Путь к файлу локализации
    locale_file = locale_dir / f"{language_code}.ftl"
    if not locale_file.exists():
        raise FileNotFoundError(f"Файл локализации '{locale_file}' не найден.")

    # Загружаем файл локализации
    l10n_loader = FluentResourceLoader(str(locale_dir / "{locale}.ftl"))
    return FluentLocalization(
        locales=[language_code],
        resource_ids=[str(locale_file.absolute())],
        resource_loader=l10n_loader,
    )


# from pathlib import Path
# from fluent.runtime import FluentLocalization, FluentResourceLoader
# from typing import Callable, Any
#
#
# def get_fluent_localization(language_code: str) -> FluentLocalization:
#     """
#     Загружает файл локализации из папки 'l10n' на основе кода языка.
#     """
#     locale_dir = Path(__file__).parent.joinpath("l10n")
#     if not locale_dir.exists():
#         raise FileNotFoundError(f"Директория локализаций '{locale_dir}' не найдена.")
#
#     locale_file = locale_dir / f"{language_code}.ftl"
#     if not locale_file.exists():
#         raise FileNotFoundError(f"Файл локализации '{locale_file}' не найден.")
#
#     l10n_loader = FluentResourceLoader(str(locale_dir / "{locale}.ftl"))
#     return FluentLocalization(
#         locales=[language_code],
#         resource_ids=[str(locale_file.absolute())],
#         resource_loader=l10n_loader,
#     )
#
#
# # def get_fluent_translation(language_code: str) -> Callable[[str, dict], str]:
# def get_fluent_translation(language_code: str) -> Callable[[str, dict[str, Any]], str]:
#     # def get_fluent_translation(language_code: str) -> str:
#     """
#     Возвращает функцию перевода, аналогичную i18n.t, для Fluent.
#     """
#     l10n = get_fluent_localization(language_code)
#
#     def translate(key: str, **kwargs) -> str:
#         return l10n.format_value(key, kwargs)
#
#     return translate
