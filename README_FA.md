# راهنمای فارسی اجرا

۱. پایتون ۳٫۹ یا بالاتر نصب کنید.
۲. در پوشهٔ پروژه: `pip install -r requirements.txt`
۳. اجرا: `PYTHONPATH=src python -m cbam_tvi.cli` (در ویندوز PowerShell: `$env:PYTHONPATH="src"; python -m cbam_tvi.cli`)
۴. جدول‌ها در `results/` و شکل‌ها در `figures/` ساخته می‌شوند.
۵. آزمون بازتولید اعداد مقاله: `pytest`

هیچ عددی در کد نیست؛ همهٔ ورودی‌ها در پوشهٔ `data/` هستند (شرح کامل در `data/README.md`).
برای به‌روزرسانی (مثلاً جدول داده-ستاندهٔ جدید یا سال تجاری جدید) فقط فایل‌های `data/` را تغییر دهید.
