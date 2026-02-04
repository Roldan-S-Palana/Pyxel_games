import pyxel

class App:
    def __init__(self):
        pyxel.init(128, 128)  # Screen size in pixels
        pyxel.load("testmap.pyxres")  # Load your tilemap
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        # 16 tiles * 8 pixels = 128 pixels
        # Parameters: (x, y, tilemap_index, u, v, width_in_pixels, height_in_pixels)
        pyxel.bltm(0, 0, 0, 0, 0, 128, 128)

App()
