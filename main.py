import threading
import re

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform

from plyer import tts


KV = """
BoxLayout:
    orientation: "vertical"
    padding: "20dp"
    spacing: "15dp"

    Label:
        text: "[b]चीनी ❤️[/b]"
        markup: True
        font_size: "32sp"
        size_hint_y: 0.2

    Label:
        id: status
        text: "नमस्ते! मैं चीनी हूँ। मुझसे बात करो।"
        font_size: "19sp"
        halign: "center"
        valign: "middle"
        text_size: self.width, None

    ScrollView:
        Label:
            id: conversation
            text: "चीनी: नमस्ते! मैं तुम्हारी मदद के लिए तैयार हूँ।"
            font_size: "18sp"
            size_hint_y: None
            height: self.texture_size[1] + dp(20)
            text_size: self.width, None

    Button:
        text: "🎤 चीनी से बात करो"
        font_size: "20sp"
        size_hint_y: 0.18
        on_release: app.listen()

    Button:
        text: "🔊 जवाब दोबारा सुनो"
        size_hint_y: 0.13
        on_release: app.repeat_answer()
"""


class CheeniApp(App):

    def build(self):
        self.last_answer = "नमस्ते! मैं चीनी हूँ। बताओ, क्या मदद चाहिए?"
        self.listening = False
        self.request_code = 7412

        root = Builder.load_string(KV)

        if platform == "android":
            try:
                from android import activity
                activity.bind(
                    on_activity_result=self.on_activity_result
                )
                from android.permissions import (
                    request_permissions,
                    Permission
                )
                request_permissions([
                    Permission.RECORD_AUDIO
                ])
            except Exception as e:
                print("Android setup:", e)

        return root

    def listen(self):
        if self.listening:
            self.root.ids.status.text = "मैं सुन रही हूँ..."
            return

        if platform != "android":
            self.root.ids.status.text = (
                "कृपया Android मोबाइल पर इस्तेमाल करें।"
            )
            return

        try:
            from jnius import autoclass

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
                RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE,
                "hi-IN"
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_MAX_RESULTS, 1
            )
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "चीनी से बात करें"
            )

            self.listening = True
            self.root.ids.status.text = (
                "चीनी सुन रही है... आराम से पूरी बात बोलो।"
            )

            PythonActivity.mActivity.startActivityForResult(
                intent, self.request_code
            )

        except Exception as e:
            self.listening = False
            self.root.ids.status.text = (
                "माइक्रोफ़ोन शुरू नहीं हुआ। दोबारा कोशिश करो।"
            )
            print("Listen error:", e)

    def on_activity_result(
        self, request_code, result_code, intent
    ):
        if request_code != self.request_code:
            return

        self.listening = False

        if result_code != -1 or intent is None:
            self.root.ids.status.text = (
                "मैं तुम्हारी बात नहीं सुन पाई। फिर कोशिश करो।"
            )
            return

        try:
            from jnius import autoclass

            RecognizerIntent = autoclass(
                "android.speech.RecognizerIntent"
            )

            results = intent.getStringArrayListExtra(
                RecognizerIntent.EXTRA_RESULTS
            )

            if results is None or results.size() == 0:
                self.root.ids.status.text = (
                    "आवाज़ समझ नहीं आई। फिर बोलो।"
                )
                return

            text = str(results.get(0)).strip()

            if not text:
                self.root.ids.status.text = (
                    "कुछ सुनाई नहीं दिया। फिर कोशिश करो।"
                )
                return

            self.root.ids.conversation.text += (
                "\\n\\nतुम: " + text
            )

            answer = self.get_answer(text)
            self.speak(answer)

        except Exception as e:
            self.root.ids.status.text = (
                "जवाब तैयार करने में परेशानी हुई।"
            )
            print("Result error:", e)

    def get_answer(self, text):
        message = text.lower().strip()

        if any(word in message for word in [
            "नमस्ते", "हेलो", "हाय", "hello", "hi"
        ]):
            return "हेलो बाबू! ❤️ मैं चीनी हूँ। बताओ, कैसे हो?"

        if any(word in message for word in [
            "तुम्हारा नाम", "तुम कौन", "नाम क्या"
        ]):
            return "मेरा नाम चीनी है। मैं तुम्हारी पर्सनल असिस्टेंट हूँ।"

        if any(word in message for word in [
            "कैसी हो", "कैसे हो"
        ]):
            return "मैं अच्छी हूँ! तुमसे बात करके अच्छा लगा।"

        if any(word in message for word in [
            "समय", "टाइम", "कितने बजे"
        ]):
            from datetime import datetime
            return "अभी समय है " + datetime.now().strftime("%I:%M %p")

        if any(word in message for word in [
            "बाय", "अलविदा", "good night"
        ]):
            return "ठीक है बाबू, अपना ध्यान रखना। ❤️"

        return (
            "बाबू, मैंने तुम्हारी बात सुनी: "
            + text
            + "। अभी मुझे इस सवाल का जवाब देना नहीं सिखाया गया है।"
        )

    def speak(self, answer):
        self.last_answer = answer

        self.root.ids.conversation.text += (
            "\\n\\nचीनी: " + answer
        )
        self.root.ids.status.text = "चीनी जवाब दे रही है..."

        def say():
            try:
                tts.speak(answer)
                Clock.schedule_once(
                    lambda dt: self.set_ready(), 1
                )
            except Exception as e:
                print("TTS error:", e)
                Clock.schedule_once(
                    lambda dt: self.set_ready(), 0
                )

        threading.Thread(
            target=say, daemon=True
        ).start()

    def set_ready(self):
        self.root.ids.status.text = (
            "अब तुम दोबारा मुझसे बात कर सकते हो।"
        )

    def repeat_answer(self):
        self.speak(self.last_answer)


if __name__ == "__main__":
    CheeniApp().run()
