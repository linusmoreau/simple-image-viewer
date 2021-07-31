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
        self.dragged = False
        self.img = pygame.image.load(self.path)
        if self.img.get_width() > screen_dimensions[0] or self.img.get_height() > screen_dimensions[1]:
            area = screen_dimensions
        else:
            area = (self.img.get_width(), self.img.get_height())
        self.disp = Display(screen_center, area, self.img)
        self.cont = DragContainer()
        self.cont.add_part(self.disp)
        self.cont.show()
        self.zoom = self.disp.rect.w / self.img.get_width()
        self.max_zoom = 2

        back_button(self.history, True)
        close_button()
        self.reset_button()

        self.show()

    def handle(self, event, mouse):
        if event.type == pygame.KEYDOWN:
            pressed = pygame.key.get_pressed()
            if event.key in [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_PAGEDOWN] \
                    and self.place + 1 < len(self.files):
                if pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]:
                    ViewImage(self.files[-1], self.history, self.files)
                else:
                    ViewImage(self.files[self.place + 1], self.history, self.files)
                return True
            elif event.key in [pygame.K_LEFT, pygame.K_UP, pygame.K_PAGEUP] \
                    and self.place > 0:
                if pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]:
                    ViewImage(self.files[0], self.history, self.files)
                else:
                    ViewImage(self.files[self.place - 1], self.history, self.files)
                return True
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key in [pygame.K_EQUALS, pygame.K_MINUS]:
                self.key_zoom(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 or event.button == 5:
                self.cursor_zoom(event.button, mouse)
        return super().handle(event, mouse)

    def key_zoom(self, mark):
        if mark == pygame.K_EQUALS:
            self.zoom *= 6 / 5
            if self.zoom >= 2:
                self.zoom *= 5 / 6
                return
            x = round((self.disp.rect.centerx - screen_center[0]) * 6 / 5 + screen_center[0])
            y = round((self.disp.rect.centery - screen_center[1]) * 6 / 5 + screen_center[1])
        else:
            self.zoom *= 5 / 6
            x = round((self.disp.rect.centerx - screen_center[0]) * 5 / 6 + screen_center[0])
            y = round((self.disp.rect.centery - screen_center[1]) * 5 / 6 + screen_center[1])
        self.do_zoom((x, y))

    def cursor_zoom(self, mark, mouse):
        if mark == 4:
            self.zoom *= 6 / 5
            if self.zoom >= 2:
                self.zoom *= 5 / 6
                return
            x = round((self.disp.rect.centerx - mouse[0]) * 6 / 5 + mouse[0])
            y = round((self.disp.rect.centery - mouse[1]) * 6 / 5 + mouse[1])
        else:
            self.zoom *= 5 / 6
            x = round((self.disp.rect.centerx - mouse[0]) * 5 / 6 + mouse[0])
            y = round((self.disp.rect.centery - mouse[1]) * 5 / 6 + mouse[1])
        self.do_zoom((x, y))

    def do_zoom(self, pos):
        self.cont.remove_part(self.disp)
        dims = [p * self.zoom for p in [self.img.get_width(), self.img.get_height()]]
        try:
            self.disp = Display(pos, dims, self.img, align=CENTER)
            self.cont.add_part(self.disp)
        except pygame.error:
            pass

    def reset(self):
        self.cont.remove_part(self.disp)
        self.disp = Display(screen_center, screen_dimensions, self.img)
        self.cont.add_part(self.disp)
        self.zoom = self.disp.rect.w / self.img.get_width()

    def reset_button(self):
        b = Button((dim, 0), (dim, dim), align=TOPLEFT, threed=False)
        bimg = Image(b.rect.center, (dim * 3 / 4, dim * 3 / 4), 'reset.png')
        bimg.surface = pygame.transform.flip(bimg.surface, True, False)
        b.components.append(bimg)
        b.show()
        b.callback(self.reset)


dim = screen_height / 40


def back_button(history, from_img=False):
    b = Button((0, 0), (dim, dim), align=TOPLEFT, threed=False)
    img = Image(b.rect.center, (dim * 3 / 4, dim * 3 / 4), 'arrow.png')
    img.surface = pygame.transform.rotate(img.surface, 270)
    b.components.append(img)
    b.show()
    if len(history) <= 1 - from_img:
        b.disable()
    else:
        b.callback(functools.partial(menu, history[-2 + from_img], history[:-2 + from_img]))


def close_button():
    m = dim * 3 / 4
    c = (200, 20, 20)
    b = Button((screen_width, 0), (dim, dim), align=TOPRIGHT, threed=False, colour=c)
    surf = pygame.Surface((m, m))
    surf.fill(white)
    surf.set_colorkey(white)
    pygame.draw.line(surf, gold, (0, 0), (m, m), width=3)
    pygame.draw.line(surf, gold, (0, m), (m, 0), width=3)
    cross = Widget(b.rect.center, (m, m), align=CENTER, surface=surf, catchable=False)
    b.components.append(cross)
    b.callback(quit)
    b.show()


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
    close_button()


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
