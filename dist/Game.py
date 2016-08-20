# coding=utf8
import threading
import pygame
import time
import ctypes
import logging
import configparser
import math
from pygame.locals import *


class Game():
    """
    游戏的主干，涵盖了除了显示模块以外的所有数据处理模块。
    """

    def __init__(self):
        """
        必须载入
        """
        # self.hideCmdWindow()
        # self.showCmdWindow()
        self.isRunning = True
        self.init()
        pass

    def init(self):
        """
        初始化。载入config.conf；
        """
        self.startInputStar()
        config = configparser.ConfigParser()
        config.read('config.conf')
        self.display = Display(config['init'])
        self.display.createWindow()
        self.display.startLoop()

    def startInputStar(self):
        def inputStar():
            while self.isRunning:
                cmd = input()
                print(cmd)
                if cmd == 'exit':
                    self.isRunning = False
        star = threading.Thread(name='inputStar', target=inputStar)
        star.start()

    def hideCmdWindow(self):
        """
        隐藏命令行窗口
        """
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd:
            ctypes.windll.user32.ShowWindow(hWnd, 0)

    def showCmdWindow(self):
        """
        显示已隐藏的命令行窗口
        """
        hWnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hWnd:
            ctypes.windll.user32.ShowWindow(hWnd, 1)


class Display():
    """
    显示模块。负责图像处理、数据到图像的转换以及用户输入的捕获及提交。
    """

    def __init__(self, config):
        """
        初始化。
        """
        self.isRunning = True
        # Initialise screen
        pygame.init()
        self.config = {}
        self.config['squareSize'] = int(config['squareSize'])
        self.config['windowWidth'] = int(config['windowWidth'])
        self.config['windowHeight'] = int(config['windowHeight'])
        self.config['windowMode'] = config['windowMode']
        self.config['windowTitle'] = config['windowTitle']
        self.map = Map(self.config)
        self.camera = Camera(self.config)
        # self.screen = pygame.display.set_mode((150, 50))
        # pygame.display.set_caption('Basic Pygame program')
        #
        # # Fill background
        # background = pygame.Surface(self.screen.get_size())
        # background = background.convert()
        # background.fill((250, 250, 250))
        #
        # # Display some text
        # font = pygame.font.Font(None, 36)
        # text = font.render("Hello There", 1, (10, 10, 10))
        # textpos = text.get_rect()
        # textpos.centerx = background.get_rect().centerx
        # background.blit(text, textpos)
        #
        # # Blit everything to the screen
        # self.screen.blit(background, (0, 0))
        # pygame.display.flip()
        #
        # # Event loop
        # while 1:
        #     for event in pygame.event.get():
        #         if event.type == QUIT:
        #             return
        #
        #     self.screen.blit(background, (0, 0))
        #     pygame.display.flip()

    def createWindow(self):
        """
        创建游戏显示主窗口。
        """
        self.screen = pygame.display.set_mode(
            (int(self.config['windowWidth']), int(self.config['windowHeight'])))
        pygame.display.set_caption(self.config['windowTitle'])
        self.screen.fill((255, 255, 255))
        newSurface = pygame.Surface((50, 50))
        newSurface.fill((255, 255, 255))
        pygame.draw.rect(newSurface, (0, 0, 0), (0, 0, 50, 50), 1)
        pygame.Surface.blit(self.screen, newSurface, (0, 0
                                                      ))
        pygame.Surface.blit(self.screen, newSurface, (50, 0))
        self.camera.setHWCamera((0, 0))
        pygame.display.flip()

    def startLoop(self):
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == QUIT:
                    print('QUIT')
                    self.isRunning = False
                elif event.type == KEYDOWN:
                    print('KEYDOWN', event.key)
                    if event.key == 119:  # w
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0], pos[1] - 1))
                    elif event.key == 115:  # s
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0], pos[1] + 1))
                    elif event.key == 97:  # a
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0] - 1, pos[1]))
                    elif event.key == 100:  # d
                        pos = self.camera.getHWCamera()
                        self.camera.setHWCamera((pos[0] + 1, pos[1]))
                elif event.type == KEYUP:
                    print('KEYUP', event.key)
                elif event.type == MOUSEMOTION:
                    print('MOUSEMOTION', event.pos)
                elif event.type == MOUSEBUTTONDOWN:
                    print('MOUSEBUTTONDOWN', event.button)
                elif event.type == MOUSEBUTTONUP:
                    print('MOUSEBUTTONUP', event.button)
                elif event.type == ACTIVEEVENT:
                    print('ACTIVEEVENT', event.gain)
            #
            pygame.Surface.blit(
                self.screen, self.map.renderMap(self.camera), (0, 0))
            self.camera.update()
            #
            pygame.display.flip()
            # pygame.time.wait(20)
            time.sleep(0.02)


class Map():
    """
    地图管理类。注重数据储存与管理。
    """

    def __init__(self, config):
        pygame.init()
        self.config = config
        self.map = {}

    def setMapBlock(self, position, data):
        positionStr = '%s|%s' % (position[0], position[1]
                                 )
        self.map[positionStr] = data

    def getMapBlock(self, position):
        positionStr = '%s|%s' % (position[0], position[1]
                                 )
        # return self.map[positionStr]
        if positionStr in self.map.keys():
            return self.map[positionStr]
        else:
            newSurface = pygame.Surface((50, 50))
            if position[0] == 0 or position[1] == 0:
                newSurface.fill((255, 0, 0))
            else:
                newSurface.fill((255, 255, 255))
            pygame.draw.rect(newSurface, (0, 0, 0), (0, 0, 50, 50), 1)
            font = pygame.font.Font(None, 20)
            text = font.render('(%s,%s)' %
                               (position[0], position[1]), 1, (10, 10, 10))
            pygame.Surface.blit(newSurface, text, (0, 0))
            self.setMapBlock(position, newSurface)
            return self.map[positionStr]

    def renderMap(self, camera):
        """
        返回一个已渲染的地图Surface
        """
        renderSurfaceW = int(self.config[
                             'windowWidth'] / self.config['squareSize'] + 1) * self.config['squareSize']  # 需要渲染的总大小
        renderSurfaceH = int(self.config[
                             'windowHeight'] / self.config['squareSize'] + 1) * self.config['squareSize']
        renderSurface = pygame.Surface(
            (renderSurfaceW, renderSurfaceH))  # 未裁剪的渲染图
        blockList = self.getMapBlockPositionInSight(
            camera.SWCamera['TPosition'])  # 获取需要渲染的位置元组列表
        # 未裁剪的渲染Surface左上角方块所代表的TX
        renderSurfaceTX = math.floor((camera.SWCamera['TPosition'][0] - self.config['windowWidth'] / 2 + self.config[
            'squareSize'] / 2) / self.config['squareSize']) * self.config['squareSize']
        renderSurfaceTY = math.floor((camera.SWCamera['TPosition'][1] - self.config['windowHeight'] / 2 + self.config[
            'squareSize'] / 2) / self.config['squareSize']) * self.config['squareSize']
        # print('renderSurfaceTX', renderSurfaceTX)
        for each in blockList:
            tPositionX = each[0] * self.config['squareSize']  # 每个Block的绝对TX
            # print('tPositionX', renderSurfaceTX)
            tPositionY = each[1] * self.config['squareSize']
            # 每个Block在未裁剪的渲染Surface上的相对TX
            renderPositionTX = tPositionX - renderSurfaceTX
            # print('renderPositionTX', renderPositionTX)
            renderPositionTY = tPositionY - renderSurfaceTY
            renderPositionHX = renderPositionTX + self.config['squareSize'] / 2
            renderPositionHY = renderPositionTY + self.config['squareSize'] / 2
            blockSurface = self.getMapBlock(each)
            pygame.Surface.blit(renderSurface, blockSurface,
                                (renderPositionTX, renderPositionTY))
        dx = -(camera.SWCamera['TPosition'][0] - renderSurfaceTX -
               self.config['windowWidth'] / 2 + self.config['squareSize'] / 2)
        dy = -(camera.SWCamera['TPosition'][1] - renderSurfaceTY -
               self.config['windowHeight'] / 2 + self.config['squareSize'] / 2)
        screenSurface = pygame.Surface(
            (self.config['windowWidth'], self.config['windowHeight']))
        renderSurface.convert()
        pygame.Surface.blit(screenSurface, renderSurface, (dx, dy))
        # pygame.image.save(renderSurface, 'a.bmp')
        # pygame.image.save(screenSurface, 'b.bmp')
        # print(renderSurfaceTX)
        return screenSurface

    def getMapBlockPositionInSight(self, TPosition):
        """
        获取需要被渲染的方块的位置（positiion）列表
        """
        TPositionLeft = TPosition[0] - self.config['windowWidth'] / 2
        TPositionRight = TPosition[0] + self.config['windowWidth'] / 2
        TPositionTop = TPosition[1] - self.config['windowHeight'] / 2
        TPositionBottom = TPosition[1] + self.config['windowHeight'] / 2

        positionXLeft = math.floor(
            (TPositionLeft + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionXRight = math.floor(
            (TPositionRight + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionYTop = math.floor(
            (TPositionTop + self.config['squareSize'] / 2) / self.config['squareSize'])
        positionYBottom = math.floor(
            (TPositionBottom + self.config['squareSize'] / 2) / self.config['squareSize'])

        newList = []
        for x in range(positionXLeft, positionXRight + 1):
            for y in range(positionYTop, positionYBottom + 1):
                newList.append((x, y))
        # print(len(newList))
        return newList

    def mapGenerate(self, size):
        pass

    def getMapBlockPositionListByDistance(self, position, distance):
        """
        获取与给定位置相距给定距离的所有的块距离列表
        """
        newList = []

        def tmp(a, b):
            if (a, b) in newList:
                pass
            else:
                newList.append((a, b))
        for each in range(0, distance):
            tmp(each, distance - each)
            tmp(each, each - distance)
            tmp(- each, distance - each)
            tmp(- each, each - distance)
        return newList


class Camera():
    """
    控制摄像机。
    """

    def __init__(self, config):
        pygame.init()
        self.config = config
        self.HWCamera = {}
        self.HWCamera['position'] = (0, 0)
        self.SWCamera = {}
        self.SWCamera['TPosition'] = (0, 0)

    def setHWCamera(self, position):
        self.HWCamera['position'] = position

    def getHWCamera(self):
        return self.HWCamera['position']

    def getSWCamera(self):
        return self.SWCamera['TPosition']

    def update(self):
        x = self.HWCamera['position'][0] * self.config['squareSize']
        y = self.HWCamera['position'][1] * self.config['squareSize']
        dx = x - self.SWCamera['TPosition'][0]
        dy = y - self.SWCamera['TPosition'][1]
        ndx = dx * 0.8
        ndy = dy * 0.8
        nx = x - ndx
        ny = y - ndy
        self.SWCamera['TPosition'] = (nx, ny)

if __name__ == '__main__':
    game = Game()
