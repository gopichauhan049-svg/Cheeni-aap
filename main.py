from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from plyer import tts
import requests

# हिंदी फॉन्ट रजिस्टर करें (सुनिश्चित करें कि 'font.ttf' आपके फोल्डर में हो)
try:
    LabelBase.register(name='HindiFont', fn_regular='font.ttf')
except:
    pass

class ChiniApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(
            text="नमस्ते दानिश, मैं चीनी हूँ। बोलिए, मैं आपकी क्या मदद करूँ?",
            font_name='HindiFont',
            font_size=24,
            halign='center',
            valign='middle'
        )
        root.add_widget(self.label)
        
        self.listen_btn = Button(
            text="सुन रही हूँ (Listen)",
            font_name='HindiFont',
            font_size=20,
            size_hint=(1, 0.3),
            background_color=(0.1, 0.3, 0.7, 1)
        )
        self.listen_btn.bind(on_press=self.on_listen_click)
        root.add_widget(self.listen_btn)
        
        return root

    def on_listen_click(self, instance):
        self.label.text = "आपकी बात सुनी जा रही है..."
        # यहाँ वॉइस रिकग्निशन या जेमिनी एपीआई का लॉजिक कॉल करें
        try:
            # उदाहरण के लिए टीटीएस (TTS) से बोलना
            tts.speak("हाँ दानिश, मैं सुन रही हूँ।")
        except Exception as e:
            self.label.text = f"त्रुटि: {str(e)}"

if __name__ == '__main__':
    ChiniApp().run()
  
