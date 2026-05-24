"""
fix_encoding.py
---------------
Конвертує всі .htm/.html файли з Windows-1251 в UTF-8
і додає/оновлює <meta charset="utf-8"> в кожному файлі.

Як запустити:
  1. Скопіюй цей файл у корінь папки сайту (поряд з index.htm)
  2. Відкрий командний рядок у тій самій папці
  3. Запусти:  python fix_encoding.py
"""

import os
import re

ROOT = "."          # Запускається з кореня сайту
EXTS = (".htm", ".html")
SOURCE_ENC = "windows-1251"
TARGET_ENC = "utf-8"

converted = []
skipped   = []
errors    = []

for dirpath, _, filenames in os.walk(ROOT):
    for fname in filenames:
        if not fname.lower().endswith(EXTS):
            continue

        fpath = os.path.join(dirpath, fname)

        # --- Читаємо як windows-1251 ---
        try:
            with open(fpath, "r", encoding=SOURCE_ENC, errors="strict") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Вже не windows-1251 — пропускаємо
            skipped.append(fpath)
            continue
        except Exception as e:
            errors.append((fpath, str(e)))
            continue

        # --- Оновлюємо або додаємо <meta charset> ---
        # Видаляємо старі charset оголошення (windows-1251, cp1251, тощо)
        content = re.sub(
            r'<meta\s+[^>]*charset=["\']?[^"\'>\s]+["\']?[^>]*>',
            '',
            content,
            flags=re.IGNORECASE
        )
        # Також прибираємо http-equiv content-type
        content = re.sub(
            r'<meta\s+http-equiv=["\']content-type["\'][^>]*>',
            '',
            content,
            flags=re.IGNORECASE
        )

        # Вставляємо новий charset одразу після <head> (або на початку якщо немає)
        charset_tag = '<meta charset="utf-8">'
        if re.search(r'<head[^>]*>', content, re.IGNORECASE):
            content = re.sub(
                r'(<head[^>]*>)',
                r'\1\n' + charset_tag,
                content,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            content = charset_tag + "\n" + content

        # --- Записуємо як UTF-8 ---
        try:
            with open(fpath, "w", encoding=TARGET_ENC) as f:
                f.write(content)
            converted.append(fpath)
        except Exception as e:
            errors.append((fpath, str(e)))

# --- Звіт ---
print(f"\n{'='*50}")
print(f"  Конвертовано:  {len(converted)} файлів")
print(f"  Пропущено:     {len(skipped)} файлів (вже не windows-1251)")
print(f"  Помилки:       {len(errors)}")
print(f"{'='*50}\n")

if converted:
    print("Конвертовані файли:")
    for p in converted:
        print(f"  ✓  {p}")

if skipped:
    print("\nПропущені (можливо вже UTF-8):")
    for p in skipped:
        print(f"  ~  {p}")

if errors:
    print("\nПомилки:")
    for p, e in errors:
        print(f"  ✗  {p}: {e}")

print("\nГотово! Тепер перезалий змінені файли на GitHub.")
