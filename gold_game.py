import os
import pygame
import random
import sys
import pygame.mixer

random.seed(1234)


class Bomb_rect(pygame.sprite.Sprite):  # 绘出炸弹
    def __init__(self, Bomb_position, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image\\bomb.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = Bomb_position
        self.speed = speed

    def move(self):
        self.rect = self.rect.move(self.speed)


class Gold_rect(pygame.sprite.Sprite):  # 绘出金币
    def __init__(self, gold_position, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image\\gold.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = gold_position
        self.speed = speed

    def move(self):
        self.rect = self.rect.move(self.speed)


class Gold_Game:
    def __init__(self, level_num=2):
        pygame.init()
        self.bakscreen = pygame.display.set_mode([800, 600])
        self.bakscreen.fill([0, 160, 233])
        pygame.display.set_caption('Dig!Dig!')
        self.drawback()

        pygame.mixer.init()
        pygame.mixer.music.load('music/background_music.mp3')
        pygame.mixer.music.play(-1)

        self.levelnum = level_num if level_num in [1, 2, 3, 4, 5] else 1
        self.scorenum = 0
        self.highscore = self.get_high_score()
        self.ileft = 1
        self.iright = 10
        self.x = 100
        self.y = 480
        self.filename = 'image\\1.png'
        self.backimg_ren = self.rect(self.filename, [self.x, self.y])
        self.bakscreen.blit(self.backimg_ren.image, self.backimg_ren.rect)
        self.load_text()
        self.speed = [0, self.levelnum]

        ######
        self.all_items = []
        self.mygold = Gold_rect([random.randint(50, 580), 100], self.speed)
        self.all_items.append(self.mygold)
        self.mybomb = Bomb_rect([random.randint(50, 580), 100], self.speed)
        self.all_items.append(self.mybomb)
        ######
        self.game_over = False

        pygame.display.update()

    def get_high_score(self):
        if os.path.isfile('highscore'):
            highfile = open('highscore', 'r')
            highscore = int(highfile.readline())
            highfile.close()
        else:
            highscore = 0
        return highscore

    def drawback(self):
        my_back = pygame.image.load('image\\background.png')
        self.bakscreen.blit(my_back, [0, 0])

    def load_text(self):
        my_font = pygame.font.SysFont(None, 24)
        levelstr = 'Level:' + str(self.levelnum)
        text_screen = my_font.render(levelstr, True, (255, 0, 0))
        self.bakscreen.blit(text_screen, (650, 50))
        highscorestr = 'Higescore:' + str(self.highscore)
        text_screen = my_font.render(highscorestr, True, (255, 0, 0))
        self.bakscreen.blit(text_screen, (650, 80))
        scorestr = 'Score:' + str(self.scorenum)
        text_screen = my_font.render(scorestr, True, (255, 0, 0))
        self.bakscreen.blit(text_screen, (650, 110))

    class rect():
        def __init__(self, filename, initial_position):
            self.image = pygame.image.load(filename)
            self.rect = self.image.get_rect()
            self.rect.topleft = initial_position

    def load_game_over(self):
        my_font = pygame.font.SysFont(None, 50)
        levelstr = 'GAME OVER'
        over_screen = my_font.render(levelstr, True, (255, 0, 0))
        self.bakscreen.blit(over_screen, (300, 240))
        highscorestr = 'YOUR SCORE IS ' + str(self.scorenum)
        over_screen = my_font.render(highscorestr, True, (255, 0, 0))
        self.bakscreen.blit(over_screen, (280, 290))
        if self.scorenum > int(self.highscore):
            highscorestr = 'YOUR HAVE GOT THE HIGHEST SCORE!'
            text_screen = my_font.render(highscorestr, True, (255, 0, 0))
            self.bakscreen.blit(text_screen, (100, 340))
            highfile = open('highscore', 'w')
            highfile.writelines(str(self.scorenum))
            highfile.close()
        self.all_items.clear()
        pygame.display.update()

    def update_game(self):
        self.drawback()
        self.load_text()

        for item in self.all_items:
            item.move()
            if item.rect.top > 600:
                self.all_items.remove(item)
                if (random.randint(0, 1) == 0):
                    self.all_items.append(Gold_rect([random.randint(50, 580), 100], self.speed))
                else:
                    self.all_items.append(Bomb_rect([random.randint(50, 580), 100], self.speed))
            self.bakscreen.blit(item.image, item.rect)

        self.backimg_ren = self.rect(self.filename, [self.x, self.y])
        self.bakscreen.blit(self.backimg_ren.image, self.backimg_ren.rect)

        for item in self.all_items:
            if item.rect.colliderect(self.backimg_ren.rect):
                self.all_items.remove(item)
                if (isinstance(item, Gold_rect)):
                    self.scorenum += 5
                    if self.scorenum > 0 and self.scorenum % 25 == 0:
                        self.levelnum = self.levelnum + 1
                        self.speed = [0, self.levelnum]
                    self.load_text()
                    if (random.randint(0, 1) == 0):
                        self.all_items.append(Gold_rect([random.randint(50, 580), 100], self.speed))
                    else:
                        self.all_items.append(Bomb_rect([random.randint(50, 580), 100], self.speed))
                if (isinstance(item, Bomb_rect)):
                    self.load_game_over()

        if len(self.all_items) != 0:
            pygame.display.update()

    def handle_input(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            self.move_left()
        elif pressed_keys[pygame.K_RIGHT]:
            self.move_right()

    def move_left(self):
        self.drawback()
        self.load_text()

        if self.iright > 14:
            self.iright = 10
        self.iright += 1
        self.filename = f'image\\{self.iright}.png'
        if self.x < 50:
            self.x = 50
        else:
            self.x -= 10

        self.backimg_ren = self.rect(self.filename, [self.x, self.y])
        self.bakscreen.blit(self.backimg_ren.image, self.backimg_ren.rect)

    def move_right(self):
        self.drawback()
        self.load_text()

        if self.ileft > 4:
            self.ileft = 0
        self.ileft += 1
        self.filename = f'image\\{self.ileft}.png'
        if self.x > 730:
            self.x = 730
        else:
            self.x += 10

        self.backimg_ren = self.rect(self.filename, [self.x, self.y])
        self.bakscreen.blit(self.backimg_ren.image, self.backimg_ren.rect)

    def start(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    break
            self.handle_input()
            self.update_game()

        # 游戏结束后,关闭 Pygame 窗口
        pygame.quit()
        return self.scorenum
