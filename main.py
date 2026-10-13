import os
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from plyer import tts
from jnius import autoclass
from android import activity
from android.permissions import request_permissions, Permission


REQUEST_CODE = 1234


class ChiniApp(App):

    def build(self):
        Window.clearcolor = (0.08, 0.09, 0.15, 1)

        self.speech_ready = False
        self.last_answer = ""

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        title = Label(
            text="चीनी",
            font_size=dp(34),
            bold=True,
            size_hint_y=None,
            height=dp(65),
            color=(0.65, 0.85, 1, 1)
        )
        root.add_widget(title)

        subtitle = Label(
            text="तुम्हारी अपनी AI असिस्टेंट",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(subtitle)

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )

        self.message = Label(
            text="नमस्ते! मैं चीनी हूँ।\n\nमुझसे बात करने के लिए नीचे बटन दबाओ।",
            font_size=dp(21),
            halign="center",
            valign="top",
            size_hint_y=None,
            color=(1, 1, 1, 1),
            padding=(dp(12), dp(15))
        )

        self.message.bind(
            width=self.update_text_size,
            texture_size=self.update_message_height
        )

        self.scroll.add_widget(self.message)
        root.add_widget(self.scroll)

        self.status = Label(
            text="तैयार हूँ",
            font_size=dp(15),
            size_hint_y=None,
            height=dp(35),
            color=(0.65, 1, 0.7, 1)
        )
        root.add_widget(self.status)

        self.listen_button = Button(
            text="🎤  चीनी से बात करें",
            font_size=dp(21),
            size_hint_y=None,
            height=dp(65),
            background_normal="",
            background_color=(0.18, 0.42, 0.85, 1)
        )
        self.listen_button.bind(on_press=self.listen)
        root.add_widget(self.listen_button)

        self.repeat_button = Button(
            text="जवाब दोबारा सुनें",
            font_size=dp(17),
            size_hint_y=None,
            height=dp(50)
        )
        self.repeat_button.bind(on_press=self.repeat_answer)
        root.add_widget(self.repeat_button)

        return root

    def update_text_size(self, instance, width):
        instance.text_size = (max(0, width - dp(25)), None)

    def update_message_height(self, instance, texture_size):
        instance.height = max(
            texture_size[1] + dp(30),
            dp(100)
        )

    def on_start(self):
        activity.bind(on_activity_result=self.on_activity_result)

        request_permissions(
            [
                Permission.RECORD_AUDIO,
                Permission.INTERNET
            ],
            self.permission_result
        )

    def permission_result(self, permissions, grants):
        if all(grants):
            self.status.text = "माइक्रोफोन की अनुमति मिल गई"
        else:
            self.status.text = "सेटिंग में माइक्रोफोन की अनुमति दें"

    def show_message(self, text):
        self.message.text = text
        Clock.schedule_once(self.scroll_to_bottom, 0.15)

    def scroll_to_bottom(self, dt):
        self.scroll.scroll_y = 0

    def speak(self, text):
        self.last_answer = text

        try:
            tts.speak(text)
        except Exception as error:
            self.status.text = "आवाज़ में समस्या हुई"
            print("TTS error:", error)

    def listen(self, instance):
        try:
            self.listen_button.disabled = True
            self.status.text = "तुम्हारी बात सुन रही हूँ..."
            self.show_message("बोलिए, मैं सुन रही हूँ।")

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
                "चीनी से हिंदी में बात करें"
            )

            PythonActivity.mActivity.startActivityForResult(
                intent,
                REQUEST_CODE
            )

        except Exception as error:
            self.listen_button.disabled = False
            self.status.text = "आवाज़ शुरू नहीं हो सकी"
            self.show_message(
                "माफ कीजिए, माइक्रोफोन शुरू नहीं हुआ। "
                "माइक्रोफोन की अनुमति जाँचें।"
            )
            print("Listen error:", error)

    def on_activity_result(self, request_code, result_code, intent):
        if request_code != REQUEST_CODE:
            return

        self.listen_button.disabled = False

        if result_code != -1 or intent is None:
            self.status.text = "फिर से कोशिश करें"
            self.show_message(
                "मैं तुम्हारी बात नहीं सुन पाई। "
                "बटन दबाकर दोबारा बोलो।"
            )
            return

        try:
            RecognizerIntent = autoclass(
                "android.speech.RecognizerIntent"
            )

            results = intent.getStringArrayListExtra(
                RecognizerIntent.EXTRA_RESULTS
            )

            if results is None or results.size() == 0:
                self.status.text = "आवाज़ समझ नहीं आई"
                self.show_message("कृपया फिर से बोलिए।")
                return

            spoken_text = str(results.get(0))

            self.status.text = "तुमने कहा: " + spoken_text
            self.show_message("तुमने कहा:\n" + spoken_text)

            Clock.schedule_once(
                lambda dt: self.reply(spoken_text),
                0.3
            )

        except Exception as error:
            self.status.text = "बात समझने में समस्या हुई"
            self.show_message(
                "माफ कीजिए, मैं अभी तुम्हारी बात समझ नहीं पाई।"
            )
            print("Recognition error:", error)

    def reply(self, text):
        message = text.lower().strip()

        if any(word in message for word in [
            "नमस्ते", "हेलो", "हैलो", "हाय"
        ]):
            answer = (
                "नमस्ते! मैं चीनी हूँ। "
                "बताइए, मैं आपकी क्या मदद करूँ?"
            )

        elif any(word in message for word in [
            "तुम्हारा नाम", "नाम क्या", "कौन हो"
        ]):
            answer = "मेरा नाम चीनी है। मैं तुम्हारी असिस्टेंट हूँ।"

        elif any(word in message for word in [
            "कैसी हो", "कैसे हो", "क्या हाल"
        ]):
            answer = "मैं अच्छी हूँ! तुम कैसे हो?"

        elif any(word in message for word in [
            "समय", "टाइम", "कितने बजे"
        ]):
            current_time = datetime.now().strftime("%I:%M")
            answer = "अभी समय है " + current_time

        elif any(word in message for word in [
            "तारीख", "आज कौन सा दिन", "आज की डेट"
        ]):
            answer = "आज की तारीख है " + datetime.now().strftime("%d-%m-%Y")

        elif any(word in message for word in [
            "धन्यवाद", "शुक्रिया", "थैंक यू"
        ]):
            answer = "तुम्हारा स्वागत है। मैं तुम्हारी मदद के लिए हूँ।"

        elif any(word in message for word in [
            "गुड मॉर्निंग", "सुप्रभात"
        ]):
            answer = "सुप्रभात! तुम्हारा दिन अच्छा और खुशियों भरा हो।"

        elif any(word in message for word in [
            "गुड नाइट", "शुभ रात्रि"
        ]):
            answer = "शुभ रात्रि! अच्छे से सोना और मीठे सपने देखना।"

        elif any(word in message for word in [
            "बाय", "अलविदा"
        ]):
            answer = "ठीक है! जब भी जरूरत हो, मुझे बुला लेना।"

        else:
            answer = (
                "मैंने सुना कि तुमने कहा: "
                + text
                + "। अभी मैं सीमित सवालों के जवाब दे सकती हूँ। "
                "मुझे आगे और बेहतर बनाया जाएगा।"
            )

        self.show_message("चीनी:\n" + answer)
        self.status.text = "जवाब दे रही हूँ..."
        self.speak(answer)
        Clock.schedule_once(self.ready_again, 1.5)

    def ready_again(self, dt):
        self.status.text = "तैयार हूँ"

    def repeat_answer(self, instance):
        if self.last_answer:
            self.speak(self.last_answer)
        else:
            self.status.text = "पहले मुझसे बात करो"

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
