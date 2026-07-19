import os
import sys
import json
import time
import threading
from datetime import datetime
import flet as ft

from character import Character

def main(page: ft.Page):
    page.title = "Compass Mobile"
    page.window.width = 410
    page.window.height = 730
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 10

    # ----------------------------------------------------
    # مدیریت تنظیمات با فایل JSON
    # ----------------------------------------------------
    config_file_path = "mobile_config.json"
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    def load_mobile_config():
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"character": "sara", "current_project": "General", "interval": 30}

    def save_mobile_config(config_data):
        try:
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # بارگذاری اولیه تنظیمات
    mobile_config = load_mobile_config()
    current_char_name = mobile_config.get("character", "sara")
    project_name = mobile_config.get("current_project", "General")
    interval_time = mobile_config.get("interval", 30)
    
    character = Character(current_char_name)
    
    # متغیر کنترل تایمر
    timer_running = [True]

    # ----------------------------------------------------
    # بخش ۱: صفحه ثبت لاگ
    # ----------------------------------------------------
    char_image_path = character.random_image()
    char_quote = character.random_quote()

    image_widget = ft.Image(
        src=char_image_path if char_image_path else "",
        width=150,
        height=150,
        fit="contain",
        visible=True if char_image_path else False,
    )

    quote_widget = ft.Container(
        content=ft.Text(
            char_quote if char_quote else "سلام! من همراه شما هستم.",
            color="#FFD700",
            size=13,
            weight="bold",
            text_align=ft.TextAlign.CENTER,
        ),
        bgcolor="#1A202C",
        padding=10,
        border_radius=10,
        width=350,
    )

    input_done = ft.TextField(
        label="📝 ۱. تا الان چیکار کردی؟",
        hint_text="مثلاً: طراحی بخش منو...",
        border_color="#4A5568",
        focused_border_color="#3182CE",
        text_align=ft.TextAlign.RIGHT,
        width=350,
    )

    input_next = ft.TextField(
        label="🎯 ۲. تایم بعدی می‌خوای چیکار کنی؟",
        hint_text="مثلاً: نوشتن کدهای دکمه خروج...",
        border_color="#4A5568",
        focused_border_color="#3182CE",
        text_align=ft.TextAlign.RIGHT,
        width=350,
    )

    status_text = ft.Text("", color="#48BB78", size=13)

    def save_log_clicked(e):
        done_text = input_done.value.strip() if input_done.value else ""
        next_text = input_next.value.strip() if input_next.value else ""

        if not done_text and not next_text:
            status_text.value = "⚠️ لطفاً حداقل یکی از کادرها را پر کنید!"
            status_text.color = "#F56565"
            page.update()
            return

        config_now = load_mobile_config()
        active_project = config_now.get("current_project", "General")
        log_file_path = os.path.join(logs_dir, f"{active_project}.txt")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        active_char = config_now.get("character", "sara")
        log_entry = (
            f"==================================================\n"
            f"📅 زمان: {now} (موبایل)\n"
            f"👤 کاراکتر: {active_char}\n"
            f"📌 پروژه: {active_project}\n"
            f"--------------------------------------------------\n"
            f"✅ انجام شده: {done_text if done_text else '---'}\n"
            f"🎯 هدف بعدی: {next_text if next_text else '---'}\n"
            f"==================================================\n\n"
        )

        try:
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
            status_text.value = "💾 گزارش با موفقیت ثبت شد!"
            status_text.color = "#48BB78"
            input_done.value = ""
            input_next.value = ""
        except Exception as ex:
            status_text.value = f"⚠️ خطا در ذخیره فایل: {ex}"
            status_text.color = "#F56565"
            
        page.update()

    save_button = ft.Button(
        content=ft.Text("ثبت لاگ و هدف‌گذاری", color="white", weight="bold"),
        bgcolor="#3182CE",
        on_click=save_log_clicked,
        width=200,
        height=40,
    )

    proj_title_text = ft.Text(
        f"پروژه فعال: {project_name} | کاراکتر: {current_char_name}",
        size=13,
        weight="bold",
        color="#ED8936",
    )

    view_log = ft.Column(
        controls=[
            proj_title_text,
            ft.Divider(color="#4A5568"),
            image_widget,
            quote_widget,
            ft.Container(height=5),
            input_done,
            input_next,
            ft.Container(height=5),
            save_button,
            status_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ----------------------------------------------------
    # بخش ۲: صفحه تنظیمات و مدیریت
    # ----------------------------------------------------
    settings_status = ft.Text("", size=13)

    chars_base_dir = os.path.join("assets", "characters")
    os.makedirs(chars_base_dir, exist_ok=True)
    available_chars = [
        d for d in os.listdir(chars_base_dir)
        if os.path.isdir(os.path.join(chars_base_dir, d))
    ]
    if not available_chars:
        available_chars = [current_char_name]

    dd_characters = ft.Dropdown(
        label="👤 انتخاب کاراکتر فعال",
        options=[ft.dropdown.Option(c) for c in available_chars],
        value=current_char_name if current_char_name in available_chars else None,
        width=320,
    )

    def change_character_clicked(e):
        if dd_characters.value:
            config_now = load_mobile_config()
            config_now["character"] = dd_characters.value
            save_mobile_config(config_now)

            new_char = Character(dd_characters.value)
            new_img = new_char.random_image()
            if new_img:
                image_widget.src = new_img
                image_widget.visible = True
            else:
                image_widget.visible = False

            quote_text = new_char.random_quote()
            quote_widget.content.value = quote_text if quote_text else "سلام! من همراه شما هستم."

            active_proj = config_now.get("current_project", "General")
            proj_title_text.value = f"پروژه فعال: {active_proj} | کاراکتر: {dd_characters.value}"
            settings_status.value = f"✅ کاراکتر فعال به '{dd_characters.value}' تغییر کرد."
            settings_status.color = "#48BB78"
            page.update()

    btn_change_char = ft.Button(
        content=ft.Text("تغییر کاراکتر", color="white"),
        bgcolor="#805AD5",
        on_click=change_character_clicked,
    )

    existing_logs = [
        f.replace(".txt", "") for f in os.listdir(logs_dir) if f.endswith(".txt")
    ]
    if project_name not in existing_logs:
        existing_logs.append(project_name)

    dd_projects = ft.Dropdown(
        label="📌 انتخاب پروژه فعال",
        options=[ft.dropdown.Option(p) for p in existing_logs],
        value=project_name if project_name in existing_logs else None,
        width=320,
    )

    def change_project_clicked(e):
        if dd_projects.value:
            config_now = load_mobile_config()
            config_now["current_project"] = dd_projects.value
            save_mobile_config(config_now)
            
            active_char = config_now.get("character", "sara")
            proj_title_text.value = f"پروژه فعال: {dd_projects.value} | کاراکتر: {active_char}"
            settings_status.value = f"✅ پروژه فعال به '{dd_projects.value}' تغییر کرد."
            settings_status.color = "#48BB78"
            page.update()

    btn_change_project = ft.Button(
        content=ft.Text("تغییر پروژه", color="white"),
        bgcolor="#319795",
        on_click=change_project_clicked,
    )

    # فیلد جدید: تنظیم زمان یادآوری (دقیقه)
    input_interval = ft.TextField(
        label="⏱️ زمان یادآوری مجدد (دقیقه)",
        value=str(interval_time),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color="#4A5568",
        width=320,
    )

    def save_interval_clicked(e):
        try:
            val = int(input_interval.value.strip())
            if val <= 0:
                raise ValueError
            config_now = load_mobile_config()
            config_now["interval"] = val
            save_mobile_config(config_now)
            settings_status.value = f"⏱️ زمان یادآوری به {val} دقیقه تغییر یافت."
            settings_status.color = "#48BB78"
        except ValueError:
            settings_status.value = "⚠️ لطفا یک عدد بزرگتر از صفر وارد کنید."
            settings_status.color = "#F56565"
        page.update()

    btn_save_interval = ft.Button(
        content=ft.Text("ذخیره زمان یادآوری", color="white"),
        bgcolor="#D69E2E",
        on_click=save_interval_clicked,
    )

    input_add_quote = ft.TextField(
        label="💬 افزودن جمله جدید به کاراکتر فعال",
        hint_text="جمله جدید...",
        border_color="#4A5568",
        width=320,
    )

    def add_quote_clicked(e):
        q_text = input_add_quote.value.strip() if input_add_quote.value else ""
        if q_text:
            config_now = load_mobile_config()
            active_char = config_now.get("character", "sara")
            c_dir = os.path.join("assets", "characters", active_char)
            os.makedirs(c_dir, exist_ok=True)
            q_file = os.path.join(c_dir, "quotes.txt")

            try:
                with open(q_file, "a", encoding="utf-8") as f:
                    f.write(f"\n{q_text}")
                input_add_quote.value = ""
                settings_status.value = f"💬 جمله جدید به کاراکتر '{active_char}' اضافه شد!"
                settings_status.color = "#48BB78"
            except Exception as ex:
                settings_status.value = f"⚠️ خطا در نوشتن جمله: {ex}"
                settings_status.color = "#F56565"
            page.update()

    btn_add_quote = ft.Button(
        content=ft.Text("ثبت جمله جدید", color="white"),
        bgcolor="#2B6CB0",
        on_click=add_quote_clicked,
    )

    view_settings = ft.Column(
        controls=[
            ft.Text("⚙️ مدیریت کاراکتر و پروژه", size=15, weight="bold", color="#63B3ED"),
            ft.Divider(color="#4A5568"),
            dd_characters,
            btn_change_char,
            ft.Container(height=5),
            dd_projects,
            btn_change_project,
            ft.Divider(color="#4A5568"),
            input_interval,
            btn_save_interval,
            ft.Divider(color="#4A5568"),
            input_add_quote,
            btn_add_quote,
            settings_status,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ----------------------------------------------------
    # بخش ۳: ساخت دکمه‌های سوئیچ بالای صفحه
    # ----------------------------------------------------
    content_area = ft.Container(content=view_log, padding=5)

    def switch_to_log(e):
        content_area.content = view_log
        btn_tab_log.bgcolor = "#3182CE"
        btn_tab_settings.bgcolor = "#2D3748"
        page.update()

    def switch_to_settings(e):
        content_area.content = view_settings
        btn_tab_log.bgcolor = "#2D3748"
        btn_tab_settings.bgcolor = "#3182CE"
        page.update()

    btn_tab_log = ft.Button(
        content=ft.Text("📝 ثبت لاگ", color="white", size=13),
        bgcolor="#3182CE",
        on_click=switch_to_log,
        width=170,
        height=38,
    )

    btn_tab_settings = ft.Button(
        content=ft.Text("⚙️ تنظیمات", color="white", size=13),
        bgcolor="#2D3748",
        on_click=switch_to_settings,
        width=170,
        height=38,
    )

    top_bar = ft.Row(
        controls=[btn_tab_log, btn_tab_settings],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        top_bar,
        ft.Divider(color="#4A5568"),
        content_area,
    )

    # ----------------------------------------------------
    # مکانیزم تایمر بک‌گراند و سیستم نوتیفیکیشن موبایل
    # ----------------------------------------------------
    def alert_timer_worker():
        while timer_running[0]:
            config_check = load_mobile_config()
            # تبدیل دقیقه به ثانیه برای تست سریع‌تر می‌توانید این خط را تغییر دهید
            sleep_seconds = config_check.get("interval", 30) * 60
            
            # خوابیدن در بازه‌های کوچک برای بستن سریع برنامه در صورت لزوم
            for _ in range(int(sleep_seconds)):
                if not timer_running[0]:
                    return
                time.sleep(1)
                
            # ارسال نوتیفیکیشن سیستمی موبایل (حالت بنر بالای صفحه در فلت)
            active_char_name = config_check.get("character", "sara")
            current_character = Character(active_char_name)
            alert_quote = current_character.random_quote()
            
            # به روزرسانی پیام در صفحه اصلی در صورت باز بودن
            quote_widget.content.value = alert_quote
            new_img = current_character.random_image()
            if new_img:
                image_widget.src = new_img
                image_widget.visible = True
            
            # باز کردن پاپ‌آپ نوتیفیکیشن موبایلی
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"👤 {active_char_name}: {alert_quote}", size=14, weight="bold"),
                    bgcolor="#2B6CB0",
                    duration=6000
                )
            )
            page.update()

    # اجرای ترد پس‌زمینه بدون بلاک کردن UI موبایل
    threading.Thread(target=alert_timer_worker, daemon=True).start()

    # مدیریت زمان خروج یا بستن برای متوقف کردن ترد
    def on_disconnect(e):
        timer_running[0] = False
    page.on_disconnect = on_disconnect

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")