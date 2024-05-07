import pyxel


class App:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.moving = 0
        self.upping = 0
        self.obstacles = []
        self.lost = False
        self.monsters = []
        self.playerPixels = []
        self.rockPixels = []
        self.doubleRockPixels = []
        self.monsterPixels = []
        self.totalLife = 3
        self.game_over_compte = 0
        self.tir = []
        self.cloud_generation = [128, 128 + 3 * 16]

        pyxel.init(128, 128)
        pyxel.load("main.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):

        if pyxel.btn(pyxel.KEY_LEFT) and not self.lost:
            self.moving += 1
            self.x -= 5
        elif pyxel.btn(pyxel.KEY_RIGHT) and not self.lost:
            self.moving += 1
            self.x += 5
            if pyxel.rndi(1, 10) == 1:
                x = self.x + pyxel.width - 20
                already = False
                for obstacle in self.obstacles:
                    if x >= obstacle[0] and x < obstacle[0] + 16 * 5:
                        already = True
                if not already:
                    self.obstacles.append((x, pyxel.rndi(1, 5) == 1))
            if pyxel.rndi(1, 20) == 1:
                x = self.x + pyxel.width - 20
                already = False
                for monster in self.monsters:
                    if x >= monster and x < monster + 16 * 5:
                        already = True
                if not already:
                    self.monsters.append(x)
                    if pyxel.rndi(1, 5) == 1:
                        self.monsters.append(x + 16)

        if pyxel.btn(pyxel.KEY_SPACE) and not self.lost:
            self.tir.append([33, self.y - 5])
        for t in self.tir:
            t[0] += 5
            if t[0] > 128:
                self.tir.remove(t)

        if self.moving == 10:
            self.moving = 0

        if pyxel.btn(pyxel.KEY_UP) and self.upping == 0 and not self.lost:
            self.upping = 1
        if self.upping == 1 and not self.lost:
            self.y += (45 - self.y) * 0.1
            if self.y >= 30:
                self.upping = 2
        if self.upping == 2 and not self.lost:
            self.y -= (55 - self.y) * 0.1
            if self.y <= 0:
                self.y = 0
                self.upping = 0

        for obstacle in self.obstacles:
            if not obstacle[1] and len(self.rockPixels) > 0:
                if self.pixelOverlap(self.playerPixels, self.x, pyxel.height - 16 - self.y, self.rockPixels,
                                     obstacle[0] - 20, pyxel.height - 16):
                    self.lost = True
            elif len(self.doubleRockPixels) > 0:
                if self.pixelOverlap(self.playerPixels, self.x, pyxel.height - 16 - self.y, self.doubleRockPixels,
                                     obstacle[0] - 20, pyxel.height - 16):
                    self.lost = True

        for monster in self.monsters:
            if len(self.monsterPixels) > 0:
                if self.pixelOverlap(self.playerPixels, self.x, pyxel.height - 16 - self.y, self.monsterPixels,
                                     monster - 20, pyxel.height - 16):
                    self.lost = True
                    self.monsters.remove(monster)

        if self.totalLife > 0 and self.lost:
            self.lost = False
            self.totalLife -= 1
            if self.totalLife == 0:
                self.lost = True
                pyxel.stop()
            else:
                self.obstacles.clear()

    def draw(self):
        pyxel.cls(0)

        pyxel.rect(0, 0, pyxel.width, pyxel.height, 5)
        pyxel.text(pyxel.width - 15, 5, str(round(self.x / 10)), 0)

        if self.moving < 5:
            pyxel.blt(20, pyxel.height - 16 - self.y, 0, 0, 8, 16, 16)
        else:
            pyxel.blt(20, pyxel.height - 16 - self.y, 0, 16, 8, 16, 16)

        if len(self.playerPixels) == 0:
            self.playerPixels = self.findBlackPixels(20, pyxel.height - 16, 16, 16)
            pyxel.playm(0, loop=True)

        for obstacle in self.obstacles:
            x = obstacle[0] - self.x
            if x < -32: continue
            if not obstacle[1]:
                pyxel.blt(x, pyxel.height - 16, 0, 176, 128, 16, 16)
                if len(self.rockPixels) == 0:
                    self.rockPixels = self.findBlackPixels(x, pyxel.height - 16, 16, 16)
            else:
                pyxel.blt(x, pyxel.height - 16, 0, 224, 128, 32, 16)
                if len(self.doubleRockPixels) == 0 and x < pyxel.width - 32:
                    self.doubleRockPixels = self.findBlackPixels(x, pyxel.height - 16, 32, 16)

        for monster in self.monsters:
            x = monster - self.x
            if x < -32: continue
            pyxel.blt(x, pyxel.height - 16, 0, 128, 8, 16, 16)
            if len(self.monsterPixels) == 0 and x < pyxel.width - 32:
                self.monsterPixels = self.findBlackPixels(x, pyxel.height - 16, 16, 16)

        for t in self.tir:
            pyxel.blt(t[0], pyxel.height - 16 - t[1], 0, 35, 11, 2, 2)

        self.lifebar()
        self.game_over_animation()
        self.cloud()

    def findBlackPixels(self, x, y, w, h):
        blackpixels = []
        for i in range(w):
            for j in range(h):
                if pyxel.pget(x + i, y + j) == 0:
                    blackpixels.append((i, j))
        return blackpixels

    def pixelOverlap(self, pixels1, p1x, p1y, pixels2, p2x, p2y):
        for p1 in pixels1:
            for p2 in pixels2:
                if p1[0] + p1x == p2[0] + p2x and p1[1] + p1y == p2[1] + p2y:
                    return True
        return False

    def lifebar(self):
        for i in range(self.totalLife):
            pyxel.blt(5 + (10 * i), 5, 0, 51, 203, 10, 10)
        for i in range(3 - self.totalLife):
            pyxel.blt((25 - (10 * i)), 5, 0, 51, 187, 10, 10)
            pass

    def game_over_animation(self):
        if self.lost:
            if self.game_over_compte <= 15:
                pyxel.blt(20, pyxel.height - 16 - self.y, 0, 96, 88, 16, 16)
            elif self.game_over_compte > 15:
                pyxel.blt(20, pyxel.height - 16 - self.y, 0, 112, 88, 16, 16)
            self.game_over_compte += 1

    def cloud(self):
        pyxel.blt(self.cloud_generation[0], 20, 0, 160, 32, 16, 16)
        pyxel.blt(self.cloud_generation[1], 40, 0, 160, 32, 16, 16)
        for i in range(len(self.cloud_generation)):
            self.cloud_generation[i] -= 1
            if self.cloud_generation[i] <= -16:
                self.cloud_generation[i] = 128


App()
