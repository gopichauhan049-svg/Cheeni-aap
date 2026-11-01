import os
import glob
import threading
from datetime import datetime

import requests

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.text import LabelBase

from plyer import tts


# Find the Hindi font included in the project.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FILES = glob.glob(
    os.path.join(BASE_DIR, "NotoSansDevanagari*.ttf")
)

HINDI_FONT = "Roboto"

if FONT_FILES:
    try:
        LabelBase.register(
            name="CheeniHindi",
            fn_regular=FONT_FILES[0]
        )
        HINDI_FONT = "CheeniHindi"
    except Exception as e:
        print("Hindi font error:", e)


KV = """
BoxLayout:
    orientation: "vertical"
    padding: "16dp"
    spacing: "10dp"

    Label:
        text: "[b]चीनी ❤️[/b]"
        markup: True
        font_name: app.hindi_font
        font_size: "28sp"
        size_hint_y: 0.13

    Label:
        id: status
        text: "नमस्ते! मैं चीनी हूँ। मुझसे बात करो।"
        font_name: app.hindi_font
        font_size: "17sp"
        halign: "center"
        valign: "middle"
        text_size: self.width, self.height
        size_hint_y: 0.12

    ScrollView:
        do_scroll_x: False

        Label:
            id: conversation
            text: "चीनी: नमस्ते! मैं तुम्हारी मदद के लिए तैयार हूँ।"
            font_name: app.hindi_font
            font_size: "17sp"
            size_hint_y: None
            height: max(self.texture_size[1] + dp(24), dp(100))
            text_size: self.width, None
            halign: "left"
            valign: "top"

    Button:
        text: "🎤 चीनी से बात करो"
        font_name: app.hindi_font
        font_size: "18sp"
        size_hint_y: 0.14
        on_release: app.listen()

    Button:
        text: "🔊 जवाब दोबारा सुनो"
        font_name: app.hindi_font
        font_size: "17sp"
        size_hint_y: 0.12
        on_release: app.repeat_answer()
"""


class CheeniApp(App):

    def build(self):
        self.hindi_font = HINDI_FONT
        self.last_answer = (
            "नमस्ते बाबू! मैं चीनी हूँ। बताओ, क्या मदद चाहिए?"
        )
        self.listening = False
        self.busy = False
        self.request_code = 7412

        self.conversation_history = []

        root = Builder.load_string(KV)

        if platform == "android":
            try:
                from android import activity
                from android.permissions import (
                    request_permissions,
                    Permission
                )

                activity.bind(
                    on_activity_result=self.on_activity_result
                )

                request_permissions([
                    Permission.RECORD_AUDIO
                ])

            except Exception as e:
                print("Android setup error:", e)

        return root

    def add_message(self, message):
        label = self.root.ids.conversation

        if label.text:
            label.text += "\n\n"

        label.text += message

        Clock.schedule_once(
            lambda dt: setattr(
                self.root.ids.status, "text_size",
                (
                    self.root.ids.status.width,
                    self.root.ids.status.height
                )
            ),
            0
        )

    def listen(self):
        if self.listening or self.busy:
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
                RecognizerIntent.EXTRA_MAX_RESULTS,
                1
            )

            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "चीनी से बात करें"
            )

            self.listening = True

            self.root.ids.status.text = (
                "चीनी सुन रही है... अपनी बात बोलो।"
            )

            PythonActivity.mActivity.startActivityForResult(
                intent,
                self.request_code
            )

        except Exception as e:
            self.listening = False

            self.root.ids.status.text = (
                "माइक्रोफ़ोन शुरू नहीं हुआ।"
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

            user_text = str(results.get(0)).strip()

            if not user_text:
                return

            self.add_message("तुम: " + user_text)

            self.root.ids.status.text = (
                "चीनी तुम्हारे सवाल का जवाब सोच रही है..."
            )

            self.get_ai_answer(user_text)

        except Exception as e:
            self.root.ids.status.text = (
                "तुम्हारी बात समझने में परेशानी हुई।"
            )
            print("Speech result error:", e)

    def get_ai_answer(self, user_text):
        if self.busy:
            return

        self.busy = True

        threading.Thread(
            target=self._ask_gemini,
            args=(user_text,),
            daemon=True
        ).start()

    def _ask_gemini(self, user_text):
        try:
            try:
                from cheeni_config import GEMINI_API_KEY
            except ImportError:
                GEMINI_API_KEY = "AQ.Ab8RN6I1R86forw5xLQTOgrGZNu_ohCinfk2d3N9S-tcE1VNFQ"

            if not GEMINI_API_KEY:
                raise RuntimeError(
                    "Gemini API Key सेट नहीं है।"
                )

            url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/gemini-3.8-flash:generateContent"
            )

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY
            }

            history_text = ""

            for item in self.conversation_history[-8:]:
                history_text += (
                    item["role"] + ": "
                    + item["text"] + "\n"
                )

            prompt = (
                "तुम चीनी नाम की एक मददगार, प्यारी और "
                "विनम्र हिंदी बोलने वाली निजी AI असिस्टेंट हो। "
                "यूज़र को जरूरत के अनुसार हिंदी या Hinglish में "
                "स्पष्ट, उपयोगी और स्वाभाविक जवाब दो। "
                "यूज़र को Danish या बाबू कह सकती हो। "
                "झूठा दावा मत करना कि तुमने कोई काम किया है।\n\n"
                "बातचीत का इतिहास:\n"
                + history_text
                + "\nयूज़र का नया सवाल:\n"
                + user_text
            )

            response = requests.post(
                url,
                headers=headers,
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 800
                    }
                },
                timeout=45
            )

            if not response.ok:
                raise RuntimeError(
                    "Gemini API error "
                    + str(response.status_code)
                    + ": "
                    + response.text[:300]
                )

            data = response.json()

            answer = (
                data["candidates"][0]
                ["content"]["parts"][0]["text"]
                .strip()
            )

            if not answer:
                raise RuntimeError(
                    "Gemini ने खाली जवाब दिया।"
                )

            self.conversation_history.append({
                "role": "यूज़र",
                "text": user_text
            })

            self.conversation_history.append({
                "role": "चीनी",
                "text": answer
            })

            Clock.schedule_once(
                lambda dt: self.speak(answer),
                0
            )

        except Exception as e:
            error_message = str(e)

            print("Gemini error:", error_message)

            if "API Key" in error_message:
                answer = (
                    "बाबू, मेरी Gemini API Key सेट नहीं है। "
                    "इसे सही करना होगा।"
                )
            elif "401" in error_message or "403" in error_message:
                answer = (
                    "बाबू, मेरी API Key या उसकी अनुमति में "
                    "समस्या है। Google AI Studio में इसे जाँचो।"
                )
            elif "429" in error_message:
                answer = (
                    "बाबू, अभी API की उपयोग सीमा पूरी हो गई है। "
                    "थोड़ी देर बाद फिर कोशिश करो।"
                )
            else:
                answer = (
                    "बाबू, अभी AI से संपर्क नहीं हो पा रहा है। "
                    "इंटरनेट और API सेटिंग जाँचकर फिर कोशिश करो।"
                )

            Clock.schedule_once(
                lambda dt: self.speak(answer),
                0
            )

    def speak(self, answer):
        self.last_answer = answer

        self.add_message("चीनी: " + answer)

        self.root.ids.status.text = (
            "चीनी जवाब दे रही है..."
        )

        threading.Thread(
            target=self._speak_worker,
            args=(answer,),
            daemon=True
        ).start()

    def _speak_worker(self, answer):
        try:
            tts.speak(answer)

        except Exception as e:
            print("TTS error:", e)

        finally:
            Clock.schedule_once(
                lambda dt: self.set_ready(),
                0
            )

    def set_ready(self):
        self.busy = False

        self.root.ids.status.text = (
            "अब तुम दोबारा मुझसे बात कर सकते हो।"
        )

    def repeat_answer(self):
        if self.busy:
            return

        self.speak(self.last_answer)


if __name__ == "__main__":
    CheeniApp().run()
