from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
import threading, time, queue

KV = '''
<MainWidget>:
    orientation: 'vertical'
    padding: 10
    spacing: 8

    BoxLayout:
        size_hint_y: None
        height: '40dp'
        spacing: 8
        Label:
            text: "Username:"
            size_hint_x: None
            width: '90dp'
        TextInput:
            id: username
            text: root.username_text
            multiline: False
            on_text: root.username_text = self.text
        Button:
            text: "Clear"
            size_hint_x: None
            width: '80dp'
            on_release: root.clear_username()

    BoxLayout:
        size_hint_y: None
        height: '40dp'
        spacing: 8
        Label:
            text: "Action:"
            size_hint_x: None
            width: '90dp'
        Spinner:
            id: action_spinner
            text: root.action_text
            values: ["DemoAction","CheckOnly","VerboseDemo"]
            size_hint_x: 0.7
            on_text: root.action_text = self.text

    BoxLayout:
        size_hint_y: None
        height: '44dp'
        spacing: 8
        Button:
            id: run_btn
            text: "Run"
            on_release: root.start_worker()
        Button:
            id: stop_btn
            text: "Stop"
            disabled: not root.is_running
            on_release: root.stop_worker()
        Button:
            text: "About"
            on_release: app.show_about()

    ProgressBar:
        id: progress_bar
        max: 100
        value: root.progress_value
        size_hint_y: None
        height: '20dp'

    Label:
        text: "Log:"
        size_hint_y: None
        height: '22dp'

    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        GridLayout:
            id: log_container
            cols: 1
            size_hint_y: None
            height: self.minimum_height
'''

class MainWidget(BoxLayout):
    username_text = StringProperty("")
    action_text = StringProperty("DemoAction")
    progress_value = NumericProperty(0)
    is_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._queue = queue.Queue()
        self._worker_thread = None
        self._stop_event = threading.Event()
        Clock.schedule_interval(self._poll_queue, 0.2)

    def clear_username(self):
        self.username_text = ""

    def append_log(self, text):
        from kivy.uix.label import Label
        lbl = Label(text=text, size_hint_y=None, height=24, halign='left', valign='middle')
        lbl.text_size = (self.width - 40, None)
        self.ids.log_container.add_widget(lbl)
        if len(self.ids.log_container.children) > 200:
            self.ids.log_container.remove_widget(self.ids.log_container.children[-1])

    def start_worker(self):
        username = self.username_text.strip()
        if not username:
            self.append_log("[!] Please enter a username.")
            return
        if self._worker_thread and self._worker_thread.is_alive():
            self.append_log("[!] Worker already running.")
            return

        self.append_log(f"Starting '{self.action_text}' for {username}")
        self.progress_value = 0
        self.is_running = True
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker, args=(username, self.action_text, self._stop_event, self._queue), daemon=True)
        self._worker_thread.start()

    def stop_worker(self):
        if self._worker_thread and self._worker_thread.is_alive():
            self._stop_event.set()
            self.append_log("Stop requested...")

    def _worker(self, username, action, stop_event, queue_):
        total_steps = 20
        for i in range(1, total_steps + 1):
            if stop_event.is_set():
                queue_.put(("log", f"Worker stopped at step {i}/{total_steps}"))
                queue_.put(("done", False))
                return
            time.sleep(0.25)
            queue_.put(("log", f"[{username}] {action} - step {i}/{total_steps}"))
            queue_.put(("progress", int(i / total_steps * 100)))
        queue_.put(("log", "Worker completed all steps."))
        queue_.put(("done", True))

    def _poll_queue(self, dt):
        try:
            while True:
                typ, payload = self._queue.get_nowait()
                if typ == "log":
                    self.append_log(payload)
                elif typ == "progress":
                    self.progress_value = payload
                elif typ == "done":
                    success = payload
                    if success:
                        self.append_log("Action finished successfully.")
                    else:
                        self.append_log("Action interrupted.")
                    self.is_running = False
                    self.progress_value = 0
        except queue.Empty:
            pass

class UsernameApp(App):
    def build(self):
        self.title = "Username Runner (Kivy)"
        Builder.load_string(KV)
        return MainWidget()

    def show_about(self):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        Popup(title="About", content=Label(text="Username Runner Demo\nSafe demo GUI."), size_hint=(0.6,0.4)).open()

if __name__ == '__main__':
    UsernameApp().run()
