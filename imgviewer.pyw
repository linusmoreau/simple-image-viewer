from base_ui import *
import threading


class ViewImage(Widget):
    def __init__(self, entry, history, files):
        widgets.clear()
        super().__init__((0, 0), (0, 0))
        self.path = entry.path
        self.files = files
        self.history = history
        self.place = self.files.index(entry)

        self.img = Image(screen_center, screen_dimensions, entry)
        self.img.show()

        back_button(self.history, True)

        self.show()

    def handle(self, event, mouse):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and self.place + 1 < len(self.files):
                ViewImage(self.files[self.place + 1], self.history, self.files)
                return True
            elif event.key == pygame.K_LEFT and self.place > 0:
                ViewImage(self.files[self.place - 1], self.history, self.files)
                return True
        return super().handle(event, mouse)


def back_button(history, from_img=False):
    dim = screen_height / 32
    back_b = Button((0, 0), (dim, dim), align=TOPLEFT, threed=False)
    bimg = Image(back_b.rect.center, (dim * 3 / 4, dim * 3 / 4), 'arrow.png')
    bimg.surface = pygame.transform.rotate(bimg.surface, 270)
    back_b.components.append(bimg)
    back_b.show()
    if len(history) <= 1 - from_img:
        back_b.disable()
    else:
        back_b.callback(functools.partial(menu, history[-2 + from_img], history[:-2 + from_img]))


def compare(file):
    s = os.path.splitext(file.path)[0].split('\\')[-1].lower()
    ns = ''
    i = 0
    while i < len(s):
        c = s[i]
        if c in '0123456789':
            j = 1
            while True:
                if i + j >= len(s) or s[i + j] not in '0123456789':
                    break
                else:
                    j += 1
            ns += s[i:i + j].rjust(64, '0')
            i += j
        else:
            ns += c
            i += 1
    return ns


def menu(loc, history):
    widgets.clear()
    history.append(loc)
    dirs = []
    files = []
    with os.scandir(loc) as entries:
        entry: os.DirEntry
        for entry in entries:
            if not entry.name.startswith('.'):
                if entry.is_dir():
                    dirs.append(entry)
                elif entry.is_file() and os.path.splitext(entry.path)[1].strip('.') in \
                        ['jpg', 'jpeg', 'png', 'gif', 'jfif']:
                    files.append(entry)
    files.sort(key=compare)
    all_entries = dirs + files
    num = len(all_entries)
    button_size = 32
    display = ScrollButtonDisplay(screen_center, (screen_width / 2, screen_height),
                                  total_size=num * button_size, align=CENTER, button_size=button_size)
    for i, entry in enumerate(all_entries):
        b = Button((display.contain_rect.left, display.contain_rect.top + i * button_size),
                   (display.contain_rect.w, button_size), parent=display)
        txt = Text(entry.name, (b.rect.left + b.rect.w / 16, b.rect.centery), align=LEFT,
                   background_colour=b.press_colour)
        b.components.append(txt)
        if entry.is_dir():
            b.callback(functools.partial(menu, entry.path, history))
        else:
            b.callback(functools.partial(ViewImage, entry, history, files))
        display.components.append(b)
    display.show()

    back_button(history)


if __name__ == '__main__':
    history = []
    lock = threading.Lock()
    pygame.display.set_caption('Image Viewer')
    icon = pygame.transform.scale((pygame.image.load("map.png")), (32, 32))
    icon_surf = pygame.Surface((32, 32))
    icon_surf.fill(white)
    icon_surf.blit(icon, (0, 0), None)
    pygame.display.set_icon(icon_surf)
    with open('start.txt', 'r') as f:
        start = f.read().strip()
    menu(start, history)
    run_loop(lock, show_fps=False)
