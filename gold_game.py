import os
import pygame
import random
import sys
import pygame.mixer


class Gold_Game:
    def __init__(self, level_num = 1):
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
        self.goldx = random.randint(50, 580)
        self.speed = [0, self.levelnum]
        self.mygold = self.gold_rect([self.goldx, 100], self.speed)
        pygame.display.update()

    def get_high_score(self):
        if os.path.isfile('highscore'):
            highfile = open('highscore', 'r')
            highscore = highfile.readline()
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

    class rect():  # 画出小人
        def __init__(self, filename, initial_position):
            self.image = pygame.image.load(filename)
            self.rect = self.image.get_rect()
            self.rect.topleft = initial_position

    class gold_rect(pygame.sprite.Sprite):  # 绘出金币
        def __init__(self, gold_position, speed):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('image\\gold.png')
            self.rect = self.image.get_rect()
            self.rect.topleft = gold_position
            self.speed = speed

        def move(self):
            self.rect = self.rect.move(self.speed)

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


    def update_game(self):
        if self.scorenum > 0 and self.scorenum / 50.0 == int(self.scorenum / 50.0):
            self.levelnum = self.scorenum / 50 + self.levelnum
            self.speed = [0, self.levelnum]

        self.drawback()
        self.load_text()
        self.mygold.move()
        self.bakscreen.blit(self.mygold.image, self.mygold.rect)

        self.backimg_ren = self.rect(self.filename, [self.x, self.y])
        self.bakscreen.blit(self.backimg_ren.image, self.backimg_ren.rect)

        if self.mygold.rect.top > 600:
            self.load_game_over()
        if self.mygold.rect.colliderect(self.backimg_ren.rect):
            self.scorenum += 5
            self.load_text()
            self.goldx = random.randint(50, 580)
            self.mygold = self.gold_rect([self.goldx, 100], self.speed)

        pygame.display.update()

    def handle_input(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT]:
            self.move_left()
        elif pressed_keys[pygame.K_RIGHT]:
            self.move_right()

    def start(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.handle_input()
            self.update_game()
