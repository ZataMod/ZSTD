from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDRoundFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.animation import Animation
from kivy.metrics import dp
import os
import pyzstd

KV = """
Screen:
    md_bg_color: app.theme_cls.bg_darkest
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(40)
        spacing: dp(25)
        
        # Header
        MDLabel:
            text: "ZSTD TOOL"
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            font_style: 'H4'
            font_name: 'AldotheApache.ttf'
            font_size: '50sp'
            size_hint_y: None
            height: dp(80)
            
        # Status Card
        MDCard:
            size_hint: 0.95, None
            height: dp(60)
            pos_hint: {'center_x': 0.5}
            md_bg_color: app.theme_cls.bg_dark
            elevation: 3
            padding: dp(10)
            
            MDLabel:
                id: status_label
                text: "Chưa chọn thư mục"
                halign: 'center'
                theme_text_color: 'Secondary'
                font_name: 'Roboto'
                font_size: '16sp'
                
        # Buttons Container
        MDBoxLayout:
            orientation: 'vertical'
            size_hint: 0.85, None
            height: dp(280)
            pos_hint: {'center_x': 0.5}
            spacing: dp(25)
            
            MDRoundFlatButton:
                id: select_btn
                text: "Chọn Thư Mục"
                on_release: app.file_manager_open()
                pos_hint: {'center_x': 0.5}
                size_hint: 0.8, None
                height: dp(56)
                md_bg_color: app.theme_cls.primary_color
                text_color: 1, 1, 1, 1
                line_color: 0, 0, 0, 0
                font_name: 'Roboto'
                font_size: '16sp'
                
            MDBoxLayout:
                spacing: dp(20)
                size_hint_y: None
                height: dp(56)
                pos_hint: {'center_x': 0.5}
                
                MDRaisedButton:
                    id: encrypt_btn
                    text: "Mã Hóa"
                    on_release: app.process_files("encrypt")
                    size_hint: 0.48, None
                    height: dp(56)
                    md_bg_color: app.theme_cls.accent_color
                    font_name: 'Roboto'
                    font_size: '16sp'
                    
                MDRaisedButton:
                    id: decrypt_btn
                    text: "Giải Mã"
                    on_release: app.process_files("decrypt")
                    size_hint: 0.48, None
                    height: dp(56)
                    md_bg_color: app.theme_cls.accent_color
                    font_name: 'Roboto'
                    font_size: '16sp'
                    
            MDRoundFlatButton:
                id: check_btn
                text: "Kiểm Tra File"
                on_release: app.check_files()
                pos_hint: {'center_x': 0.5}
                size_hint: 0.8, None
                height: dp(56)
                md_bg_color: app.theme_cls.primary_color
                text_color: 1, 1, 1, 1
                line_color: 0, 0, 0, 0
                font_name: 'Roboto'
                font_size: '16sp'
                
        # Footer
        MDLabel:
            text: "© Copyright Zata Mod"
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: 1, 1, 1, 0.5
            font_name: 'Roboto'
            font_size: '14sp'
            size_hint_y: None
            height: dp(40)
"""

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Teal"
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        self.selected_folder = ""
        return Builder.load_string(KV)
    
    def animate_button(self, button):
        anim = Animation(size=(button.width * 0.95, button.height * 0.95), duration=0.1) + \
               Animation(size=(button.width, button.height), duration=0.1)
        anim.start(button)
    
    def on_start(self):
        buttons = [self.root.ids.select_btn, self.root.ids.encrypt_btn,
                  self.root.ids.decrypt_btn, self.root.ids.check_btn]
        for btn in buttons:
            btn.opacity = 0
            anim = Animation(opacity=1, duration=0.5)
            anim.start(btn)
    
    def file_manager_open(self):
        self.animate_button(self.root.ids.select_btn)
        self.file_manager.show(os.path.expanduser("/sdcard"))
    
    def select_path(self, path):
        self.selected_folder = path
        self.root.ids.status_label.text = f"Đã chọn: {path}"
        dialog = MDDialog(
            title="Thành công",
            text=f"Đã chọn thư mục: {path}",
            radius=[20, 20, 20, 20]
        )
        dialog.open()
        self.exit_manager()
    
    def exit_manager(self, *args):
        self.file_manager.close()
    
    def process_files(self, mode):
        button = self.root.ids.encrypt_btn if mode == "encrypt" else self.root.ids.decrypt_btn
        self.animate_button(button)
        
        dict_path = "dict.vinh"
        if not os.path.exists(dict_path):
            MDDialog(
                title="Lỗi",
                text="Không tìm thấy file dict",
                radius=[20, 20, 20, 20]
            ).open()
            return
        if not self.selected_folder:
            MDDialog(
                title="Lỗi",
                text="Vui lòng chọn thư mục trước",
                radius=[20, 20, 20, 20]
            ).open()
            return
            
        with open(dict_path, "rb") as f:
            ZSTD_DICT = f.read()
            
        processed_count = 0
        for file in os.listdir(self.selected_folder):
            if file.endswith((".xml", ".bytes")):
                file_path = os.path.join(self.selected_folder, file)
                try:
                    if mode == "decrypt":
                        self.giai(file_path, ZSTD_DICT)
                    elif mode == "encrypt":
                        self.mahoa(file_path, ZSTD_DICT)
                    processed_count += 1
                except Exception as e:
                    MDDialog(
                        title="Lỗi",
                        text=f"Lỗi xử lý {file}: {str(e)}",
                        radius=[20, 20, 20, 20]
                    ).open()
                    return
                    
        MDDialog(
            title="Hoàn tất",
            text=f"Đã xử lý {processed_count} file",
            radius=[20, 20, 20, 20]
        ).open()
    
    def check_files(self):
        self.animate_button(self.root.ids.check_btn)
        if not self.selected_folder:
            MDDialog(
                title="Lỗi",
                text="Vui lòng chọn thư mục trước",
                radius=[20, 20, 20, 20]
            ).open()
            return
        
        encrypted_count = 0
        decrypted_count = 0
        total_files = 0
        
        for file in os.listdir(self.selected_folder):
            if file.endswith((".xml", ".bytes")):
                total_files += 1
                file_path = os.path.join(self.selected_folder, file)
                with open(file_path, 'rb') as f:
                    content = f.read()
                    if b"\x28\xb5\x2f\xfd" in content:
                        encrypted_count += 1
                    elif b"\x22\x4a\x67\x00" in content:
                        encrypted_count += 1
                    else:
                        decrypted_count += 1
        
        result_text = f"Tổng: {total_files} file\n" \
                     f"Đã mã hóa: {encrypted_count}\n" \
                     f"Đã giải: {decrypted_count}"
        
        MDDialog(
            title="Kết quả kiểm tra",
            text=result_text,
            radius=[20, 20, 20, 20]
        ).open()
    
    def giai(self, file, ZSTD_DICT):
        with open(file, 'rb') as f:
            dl = f.read()
        if b"\x28\xb5\x2f\xfd" in dl:
            dl = dl[dl.find(b"\x28\xb5\x2f\xfd"):]
            try:
                dl = pyzstd.decompress(dl, pyzstd.ZstdDict(ZSTD_DICT, True))
                with open(file, "wb") as output_file:
                    output_file.write(dl)
            except Exception as e:
                raise Exception(f"Giải mã thất bại: {str(e)}")
    
    def mahoa(self, file, ZSTD_DICT):
        with open(file, 'rb') as f:
            dl = f.read()
        if b"\x22\x4a\x67\x00" not in dl:
            try:
                compressed = bytearray(pyzstd.compress(dl, 17, pyzstd.ZstdDict(ZSTD_DICT, True)))
                compressed[0:0] = len(dl).to_bytes(4, "little", signed=False)
                compressed[0:0] = b"\x22\x4a\x00\xef"
                with open(file, "wb") as output_file:
                    output_file.write(compressed)
            except Exception as e:
                raise Exception(f"Mã hóa thất bại: {str(e)}")

if __name__ == "__main__":
    MainApp().run()