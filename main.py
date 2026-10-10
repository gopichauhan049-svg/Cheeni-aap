from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading

# एंड्रॉइड परमिशन और स्पीच रिकग्निशन के लिए सेफ इम्पोर्ट
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    ANDROID_PLATFORM = True
except Exception:
    ANDROID_PLATFORM = False

class ChiniApp(App):
    def build(self):
        # ऐप शुरू होते ही एंड्रॉयड परमिशन मांगें
        if ANDROID_PLATFORM:
            try:
                request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO])
            except Exception:
                pass

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(
            text='नमस्ते दानिश! मैं "चीनी" हूँ।',
            font_size='22sp'
        )
        
        btn = Button(
            text='बोलिए (Listen)',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)
        )
        btn.bind(on_press=self.on_button_click)
        
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    def on_button_click(self, instance):
        self.label.text = 'चीनी आपकी बात सुन रही है...'
        # इसे बैकग्राउंड थ्रेड में चलाएं ताकि ऐप हैंग न हो
        threading.Thread(target=self.process_voice).start()

    def process_voice(self):
        # यहाँ आपका जेमिनी या वॉयस रिस्पॉन्स लॉजिक प्रोसेस होगा
        # अभी के लिए यह सुनिश्चित करता है कि ऐप क्रैश न हो और सुचारू रूप से चले
        pass

if __name__ == '__main__':
    ChiniApp().run()
