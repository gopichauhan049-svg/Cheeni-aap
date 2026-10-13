import os
import glob

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.clock import Clock

from plyer import tts
from jnius import autoclass
from android import activity
from android.permissions import request_permissions, Permission


REQUEST_CODE = 1234


class ChiniApp(App):

    def build(self):
        self.listening = False

        # Hindi font automatically find and load
        folder = os.path.dirname(os.path.abspath(__file__))
        fonts = glob.glob(
            os.path.join(folder, "NotoSansDevanagari*.ttf")
        )

        self.font_name = "Roboto"

        if fonts:
            LabelBase.register(
                name="HindiFont",
                fn_regular=fonts[0]
            )
            self.font_name = "HindiFont"

        root = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=20
        )

        self.label = Label(
            text="नमस्ते! मैं चीनी हूँ।",
            font_name=self.font_name,
            font_size=25,
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter("text_size"))
        root.add_widget(self.label)

        self.button = Button(
            text="चीनी से बात करें",
            font_name=self.font_name,
            font_size=22,
            size_hint=(1, 0.3)
        )
        self.button.bind(on_press=self.listen)
        root.add_widget(self.button)

        return root

    def on_start(self):
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.INTERNET
        ])

        activity.bind(
            on_activity_result=self.on_activity_result
        )

    def speak(self, message):
        try:
            tts.speak(message)
        except Exception as error:
            self.label.text = "आवाज़ की समस्या: " + str(error)

    def listen(self, instance):
        try:
            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass(
                "android.speech.RecognizerIntent"
            )
            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            intent = Intent(
                RecognizerIntent.ACTION_RECOGNIZE_SPEECH
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE,
                "hi-IN"
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "चीनी सुन रही है, बोलिए"
            )

            self.label.text = "बोलिए, मैं सुन रही हूँ..."

            PythonActivity.mActivity.startActivityForResult(
                intent,
                REQUEST_CODE
            )

        except Exception as error:
            self.label.text = "माइक्रोफोन शुरू नहीं हुआ।"
            self.speak("माफ कीजिए, अभी सुनने में समस्या है।")
            print(error)

    def on_activity_result(
        self, request_code, result_code, intent
    ):
        if request_code != REQUEST_CODE:
            return

        if result_code != -1 or intent is None:
            self.label.text = "आपकी आवाज़ नहीं मिली। फिर कोशिश करें।"
            return

        RecognizerIntent = autoclass(
            "android.speech.RecognizerIntent"
        )

        results = intent.getStringArrayListExtra(
            RecognizerIntent.EXTRA_RESULTS
        )

        if results is None or results.size() == 0:
            self.label.text = "मैं समझ नहीं पाई। फिर बोलिए।"
            return

        text = str(results.get(0))
        self.label.text = "आपने कहा: " + text

        self.reply(text)

    def reply(self, text):
        message = text.lower()

        if "नमस्ते" in message or "हेलो" in message:
            answer = "हेलो! मैं चीनी हूँ। बताइए, मैं आपकी क्या मदद करूँ?"

        elif "तुम्हारा नाम" in message or "नाम क्या" in message:
            answer = "मेरा नाम चीनी है। मैं आपकी असिस्टेंट हूँ।"

        elif "कैसी हो" in message:
            answer = "मैं अच्छी हूँ। आप बताइए, कैसे हैं?"

        elif "समय" in message or "टाइम" in message:
            from datetime import datetime
            answer = "अभी समय है " + datetime.now().strftime("%I बजकर %M मिनट")

        elif "धन्यवाद" in message or "थैंक यू" in message:
            answer = "आपका स्वागत है। मैं आपकी मदद के लिए हूँ।"

        else:
            answer = (
                "आपने कहा, " + text +
                "। मैं चीनी हूँ। अभी मुझे और चीजें सिखाई जा रही हैं।"
            )

        self.label.text = answer
        self.speak(answer)

    def on_pause(self):
        return True

    def on_stop(self):
        try:
            activity.unbind(
                on_activity_result=self.on_activity_result
            )
        except Exception:
            pass


if __name__ == "__main__":
    ChiniApp().run()
