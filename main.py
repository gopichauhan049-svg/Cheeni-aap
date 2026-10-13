from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from plyer import tts
import requests

class ChiniApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical", padding=20, spacing=20)

        self.label = Label(
            text="नमस्ते दानिश, मैं चीनी हूँ। बोलिए, मैं आपकी क्या मदद करूँ?",
            font_size=22,
            halign="center",
            valign="middle"
        )
        # चौड़ाई के हिसाब से टेक्स्ट सेट करने के लिए
        self.label.bind(size=self.label.setter('text_size'))
        root.add_widget(self.label)

        self.listen_btn = Button(
            text="सुन रही हूँ (Listen)",
            font_size=20,
            size_hint=(1, 0.3),
            background_color=(0.1, 0.3, 0.7, 1)
        )
        self.listen_btn.bind(on_press=self.on_listen_click)
        root.add_widget(self.listen_btn)

        return root

    def on_listen_click(self, instance):
        self.label.text = "आपकी बात सुनी जा रही है..."
        try:
            # बोलने के लिए TTS का उपयोग
            tts.speak("हाँ दानिश, मैं सुन रही हूँ")
        except Exception as e:
            self.label.text = f"त्रुटि: {str(e)}"

if __name__ == '__main__':
    ChiniApp().run()
    
