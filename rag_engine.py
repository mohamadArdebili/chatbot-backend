import os
from PyPDF2 import PdfReader


class RAGEngine:
    def __init__(self, knowledge_folder: str = "knowledge"):
        self.knowledge_folder = knowledge_folder
        self.knowledge_base = ""
        self.load_knowledge()

    def load_knowledge(self):
        """بارگذاری داده‌ها از فایل‌های txt و pdf"""
        try:
            if not os.path.exists(self.knowledge_folder):
                os.makedirs(self.knowledge_folder)
                print(f"✅ پوشه {self.knowledge_folder} ایجاد شد")

            all_content = []
            files_loaded = []

            # خواندن تمام فایل‌های txt و pdf
            for filename in os.listdir(self.knowledge_folder):
                filepath = os.path.join(self.knowledge_folder, filename)

                if filename.endswith('.txt'):
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        all_content.append(f"=== {filename} ===\n{content}\n")
                        files_loaded.append(filename)

                elif filename.endswith('.pdf'):
                    pdf_text = self._extract_pdf_text(filepath)
                    all_content.append(f"=== {filename} ===\n{pdf_text}\n")
                    files_loaded.append(filename)

            self.knowledge_base = "\n".join(all_content)

            if files_loaded:
                print(
                    f"✅ {len(files_loaded)} فایل بارگذاری شد: {', '.join(files_loaded)}")
                print(f"   مجموع: {len(self.knowledge_base)} کاراکتر")
            else:
                print(f"⚠️ هیچ فایلی در {self.knowledge_folder} پیدا نشد")

        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌ها: {e}")

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """استخراج متن از PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"[صفحه {page_num}]\n{page_text}")
            return "\n\n".join(text)
        except Exception as e:
            return f"[خطا در خواندن PDF: {e}]"

    def create_rag_prompt(self, user_message: str) -> str:
        """ساخت prompt غنی‌شده با داده‌های knowledge base"""
        if not self.knowledge_base:
            return user_message

        return f"""بر اساس اطلاعات زیر به سوال کاربر پاسخ بده:

اطلاعات موجود:
{self.knowledge_base}

سوال کاربر: {user_message}

اگر جواب در اطلاعات بالا نیست، بگو که اطلاعات کافی نداری."""

    def reload(self):
        """به‌روزرسانی داده‌ها"""
        self.load_knowledge()
        return {
            "status": "ok",
            "size": len(self.knowledge_base),
            "folder": self.knowledge_folder
        }

    def get_status(self):
        """وضعیت knowledge base"""
        files = []
        if os.path.exists(self.knowledge_folder):
            files = [f for f in os.listdir(self.knowledge_folder)
                     if f.endswith(('.txt', '.pdf'))]

        return {
            "loaded": len(self.knowledge_base) > 0,
            "size": len(self.knowledge_base),
            "folder": self.knowledge_folder,
            "files": files
        }
