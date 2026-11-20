from app.i18n import translate_html


def test_arabic_is_default_and_document_direction_is_rtl():
    rendered = translate_html('<html lang="ar" dir="rtl"><body><h1>لوحة التحكم</h1></body></html>', "ar")
    assert '<html lang="ar" dir="rtl">' in rendered
    assert "لوحة التحكم" in rendered


def test_english_translation_sets_ltr_and_translates_static_content():
    rendered = translate_html(
        '<html lang="ar" dir="rtl"><body><h1>لوحة التحكم</h1><input placeholder="أدخل اسم المستخدم" value="اسم الموظف"></body></html>',
        "en",
    )
    assert '<html lang="en" dir="ltr">' in rendered
    assert "<h1>Dashboard</h1>" in rendered
    assert 'placeholder="Enter your username"' in rendered
    # Values and employee-entered content must not be translated.
    assert 'value="اسم الموظف"' in rendered


def test_simplified_chinese_translation_sets_ltr_and_zh_cn_locale():
    rendered = translate_html(
        '<html lang="ar" dir="rtl"><body><h1>لوحة التحكم</h1><p>الموظفون النشطون</p></body></html>',
        "zh",
    )
    assert '<html lang="zh-CN" dir="ltr">' in rendered
    assert "<h1>控制面板</h1>" in rendered
    assert "<p>在职员工</p>" in rendered


def test_scripts_and_user_content_are_not_modified():
    source = (
        '<html lang="ar" dir="rtl"><body><script>const label = "لوحة التحكم";</script>'
        '<textarea>اسم الموظف</textarea><p>لوحة التحكم</p></body></html>'
    )
    rendered = translate_html(source, "en")
    assert 'const label = "لوحة التحكم";' in rendered
    assert "<textarea>اسم الموظف</textarea>" in rendered
    assert "<p>Dashboard</p>" in rendered


def test_base_layout_uses_no_remote_font_or_script_assets():
    from pathlib import Path

    base = Path("app/templates/base.html").read_text(encoding="utf-8")
    css = Path("app/static/app.css").read_text(encoding="utf-8")

    assert "fonts.googleapis.com" not in base
    assert "fonts.gstatic.com" not in base
    assert "https://" not in base
    assert "@import url(" not in css
