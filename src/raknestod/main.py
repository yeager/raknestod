import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gdk, Gio
import gettext, locale, os, json, time, random
__version__ = "0.1.0"

APP_ID = "se.danielnylander.raknestod"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'share', 'locale')
if not os.path.isdir(LOCALE_DIR): LOCALE_DIR = '/usr/share/locale'
try:
    locale.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.bindtextdomain(APP_ID, LOCALE_DIR)
    gettext.textdomain(APP_ID)
except Exception: pass
_ = gettext.gettext
def N_(s): return s

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_('Math Support'))
        self.set_default_size(500, 500)
        self._num1 = random.randint(1, 5)
        self._num2 = random.randint(1, 5)
        self._op = '+'
        self._score = 0

        
        # Easter egg state
        self._egg_clicks = 0
        self._egg_timer = None

        header = Adw.HeaderBar()
        
        # Add clickable app icon for easter egg
        app_btn = Gtk.Button()
        app_btn.set_icon_name("se.danielnylander.raknestod")
        app_btn.add_css_class("flat")
        app_btn.set_tooltip_text(_("Raknestod"))
        app_btn.connect("clicked", self._on_icon_clicked)
        header.pack_start(app_btn)

        menu_btn = Gtk.MenuButton(icon_name='open-menu-symbolic')
        menu = Gio.Menu()
        menu.append(_('About'), 'app.about')
        menu_btn.set_menu_model(menu)
        header.pack_end(menu_btn)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main.append(header)

        self._score_label = Gtk.Label(label=_('Score: 0'))
        self._score_label.add_css_class('title-4')
        self._score_label.set_margin_top(8)
        main.append(self._score_label)

        self._question = Gtk.Label()
        self._question.add_css_class('title-1')
        self._question.set_margin_top(24)
        main.append(self._question)

        self._visual = Gtk.Label()
        self._visual.add_css_class('title-2')
        main.append(self._visual)

        answers = Gtk.FlowBox()
        answers.set_max_children_per_line(4)
        answers.set_selection_mode(Gtk.SelectionMode.NONE)
        answers.set_halign(Gtk.Align.CENTER)
        answers.set_margin_top(24)
        self._answer_flow = answers
        main.append(answers)

        self._feedback = Gtk.Label()
        self._feedback.add_css_class('title-2')
        self._feedback.set_margin_top(16)
        main.append(self._feedback)

        next_btn = Gtk.Button(label=_('Next →'))
        next_btn.add_css_class('suggested-action')
        next_btn.add_css_class('pill')
        next_btn.set_halign(Gtk.Align.CENTER)
        next_btn.set_margin_top(8)
        next_btn.connect('clicked', lambda b: self._new_question())
        main.append(next_btn)

        self.set_content(main)
        self._new_question()

    def _new_question(self):
        self._num1 = random.randint(1, 9)
        self._num2 = random.randint(1, self._num1)
        self._op = random.choice(['+', '-'])
        if self._op == '+':
            answer = self._num1 + self._num2
            self._question.set_text(f'{self._num1} + {self._num2} = ?')
            self._visual.set_text('🍎' * self._num1 + ' + ' + '🍎' * self._num2)
        else:
            answer = self._num1 - self._num2
            self._question.set_text(f'{self._num1} - {self._num2} = ?')
            self._visual.set_text('🍎' * self._num1 + ' - ' + '🍎' * self._num2)

        self._feedback.set_text('')
        while child := self._answer_flow.get_first_child():
            self._answer_flow.remove(child)

        options = list(set([answer, answer+1, answer-1, answer+2]))
        random.shuffle(options)
        for opt in options[:4]:
            btn = Gtk.Button(label=str(max(0, opt)))
            btn.add_css_class('pill')
            btn.add_css_class('title-3')
            btn.connect('clicked', self._check, max(0, opt), answer)
            self._answer_flow.insert(btn, -1)

    def _check(self, btn, chosen, answer):
        if chosen == answer:
            self._score += 1
            self._feedback.set_text(_('Correct! 🌟'))
        else:
            self._feedback.set_text(_('Try again! The answer is %d') % answer)
        self._score_label.set_text(_('Score: %d') % self._score)
    def _on_icon_clicked(self, *args):
        """Handle clicks on app icon for easter egg."""
        self._egg_clicks += 1
        if self._egg_timer:
            GLib.source_remove(self._egg_timer)
        self._egg_timer = GLib.timeout_add(500, self._reset_egg)
        if self._egg_clicks >= 7:
            self._trigger_easter_egg()
            self._egg_clicks = 0

    def _reset_egg(self):
        """Reset easter egg click counter."""
        self._egg_clicks = 0
        self._egg_timer = None
        return False

    def _trigger_easter_egg(self):
        """Show the secret easter egg!"""
        try:
            # Play a fun sound
            import subprocess
            subprocess.Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            # Fallback beep
            try:
                subprocess.Popen(['pactl', 'play-sample', 'bell'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass

        # Show confetti message
        toast = Adw.Toast.new(_("🎉 Du hittade hemligheten!"))
        toast.set_timeout(3)
        
        # Create toast overlay if it doesn't exist
        if not hasattr(self, '_toast_overlay'):
            content = self.get_content()
            self._toast_overlay = Adw.ToastOverlay()
            self._toast_overlay.set_child(content)
            self.set_content(self._toast_overlay)
        
        self._toast_overlay.add_toast(toast)



class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id='se.danielnylander.raknestod')
        self.connect('activate', lambda a: MainWindow(application=a).present())
        about = Gio.SimpleAction.new('about', None)
        about.connect('activate', lambda a,p: Adw.AboutDialog(application_name=_('Math Support'),
            application_icon=APP_ID, version=__version__, developer_name='Daniel Nylander',
            website='https://github.com/yeager/raknestod', license_type=Gtk.License.GPL_3_0,
            comments=_('Visual math for children')).present(self.get_active_window()))
        self.add_action(about)

def main():
    App().run()

if __name__ == '__main__':
    main()

