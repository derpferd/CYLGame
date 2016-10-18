import tcod as libtcod
import tdl
import tempfile
import os.path
# import tcod_to_tdl as libtcod

TCOT_ROOT_CONSOLE = None
TDL_ROOT_CONSOLE = None

def data_file(filename):
    resource_path = os.path.join(os.path.split(__file__)[0], os.path.pardir, "data", filename)
    return resource_path


class CYLGameLanguage(object):
    LITTLEPY = 0

    @staticmethod
    def get_language_description(language):
        if language == CYLGameLanguage.LITTLEPY:
            return open(data_file("little_python_intro.md")).read()


class CYLGame(object):
    MAP_WIDTH = 80
    MAP_HEIGHT = 25
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8
    GAME_TITLE = ""
    CHAR_SET = "terminal8x8_gs_ro.png"

    def is_running(self):
        raise Exception("Not implemented!")

    def get_vars_for_bot(self):
        raise Exception("Not implemented!")

    @staticmethod
    def default_prog_for_bot(language):
        raise Exception("Not implemented!")

    def handle_key(self, key):
        raise Exception("Not implemented!")

    def draw_screen(self, libtcod, console):
        raise Exception("Not implemented!")


class CYLGameRunner(object):
    def __init__(self, game_class, bot=None):
        self.game = None
        self.game_class = game_class
        self.bot = bot
        self.console = None

        self.kill = False

        keys = [chr(x) for x in range(ord("A"), ord("Z")+1)] + \
               [chr(x) for x in range(ord("a"), ord("z")+1)] + \
               [chr(x) for x in range(ord("0"), ord("9")+1)]

        self.key_consts = {}
        for c in keys:
            self.key_consts["key_"+c] = ord(c)

        self.dir_consts = {"north": ord("w"), "south": ord("s"), "west": ord("a"), "east": ord("d")}
        # for i in range(10):
        #     self.key_consts["NUM" + str(i)] = ord(str(i))

    def run(self):
        global TDL_ROOT_CONSOLE
        self.kill = False
        if not self.bot:
            if not TDL_ROOT_CONSOLE:
                # TCOT_ROOT_CONSOLE = libtcod.console_init_root(self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, self.game.GAME_TITLE)
                tdl.setFont(data_file("fonts/" + self.game_class.CHAR_SET))
                TDL_ROOT_CONSOLE = tdl.init(self.game_class.SCREEN_WIDTH, self.game_class.SCREEN_HEIGHT, self.game_class.GAME_TITLE)
                #libtcod.console_set_custom_font(data_file("fonts/terminal16x16_gs_ro.png"), libtcod.FONT_LAYOUT_ASCII_INROW)
        else:
            self.vars = {}
            if not TDL_ROOT_CONSOLE:
                # TCOT_ROOT_CONSOLE = libtcod.console_init_root(0, 0, self.game.GAME_TITLE)
                TDL_ROOT_CONSOLE = tdl.init(0, 0)

        self.game = self.game_class()

        # self.console = libtcod.console_new(self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT)
        self.console = tdl.Console(self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT)
        self.screen_cap = []
        while self.game.is_running() and not self.kill:
            if self.bot:
                self.__run_bot()
            else:
                self.__run_user()
        if self.bot:
            return self.screen_cap

    def get_screen_array(self):
        tf = tempfile.NamedTemporaryFile(mode="rb")
        libtcod.console_save_asc(self.console.tcod_console, tf.name)
        # fp = open(tf.name, 'rb')
        lines = tf.readlines()
        y, x = map(int, lines[1].split())
        chars = lines[2][1::9]
        arr = []
        for i in range(y):
            arr += [map(ord, chars[i::x])]
        # fp.close()
        # tf.delete
        return arr
        # arr = []
        # for j in range(self.game.SCREEN_HEIGHT):
        #     arr += [[]]
        #     for i in range(self.game.SCREEN_WIDTH):
        #         # char = libtcod.console_get_char(self.console, i, j)
        #         char = self.console.get_char(i, j)[0]
        #         arr[j] += [char]
        # return arr

    def __run_user(self):
        self.game.draw_screen(libtcod, self.console.tcod_console)
        # libtcod.console_blit(self.console, 0, 0, self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, TCOT_ROOT_CONSOLE, 0, 0)
        # libtcod.console_flush()
        TDL_ROOT_CONSOLE.blit(self.console, 0, 0, self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, 0, 0)
        tdl.flush()

        # key = libtcod.console_wait_for_keypress(True)
        key = tdl.event.key_wait()
        if key.char:
            # c = chr(key.c)
            self.game.handle_key(key.char)

    def __run_bot(self):
        self.game.draw_screen(libtcod, self.console.tcod_console)
        # libtcod.console_blit(self.console, 0, 0, self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, TCOT_ROOT_CONSOLE, 0, 0)
        # libtcod.console_flush()
        self.screen_cap += [self.get_screen_array()]

        self.vars.update(self.game.get_vars_for_bot())
        self.vars.update(self.key_consts)
        self.vars.update(self.dir_consts)
        self.vars = self.bot.run(self.vars)

        if "move" in self.vars:
            self.game.handle_key(chr(self.vars["move"]))
        else:
            self.kill = True
