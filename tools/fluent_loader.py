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
