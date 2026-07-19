import os
import random

class Character:
    def __init__(self, name):
        self.name = name
        # مسیر فیزیکی برای خواندن فایل‌ها توسط پایتون
        self.physical_folder = os.path.join("assets", "characters", name)
        self.quote_file = os.path.join(self.physical_folder, "quotes.txt")
        
        self.images = self.load_images()
        self.quotes = self.load_quotes()

    def load_images(self):
        images = []
        if os.path.exists(self.physical_folder):
            for file in os.listdir(self.physical_folder):
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    # برای فلت، آدرس باید نسبت به پوشه assets باشد
                    images.append(f"/characters/{self.name}/{file}")
        return images

    def load_quotes(self):
        if os.path.exists(self.quote_file):
            try:
                with open(self.quote_file, "r", encoding="utf-8") as f:
                    return [i.strip() for i in f if i.strip()]
            except Exception:
                pass
        return ["سلام 😊"]

    def random_quote(self):
        return random.choice(self.quotes) if self.quotes else "سلام 😊"

    def random_image(self):
        if not self.images:
            return None
        return random.choice(self.images)