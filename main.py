from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class ChiniApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(
            text="नमस्ते दानिश! मैं 'चीनी' हूँ।",
            font_size='22sp'
        )
        
        btn = Button(
            text="बोलिए (Listen)",
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)
        )
        btn.bind(on_press=self.on_button_click)
        
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    def on_button_click(self, instance):
        self.label.text = "चीनी आपकी बात सुन रही है..."

if __name__ == "__main__":
    ChiniApp().run()
                           
