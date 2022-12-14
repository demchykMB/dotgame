import random, sys, pygame, time, copy
from pygame.locals import *
import pygame_menu

pygame.init()
"""surface - размер картинки главное меню, должно совпадать с 
размером окна WINDOWWIDTH , WINDOWHEIGHT"""
surface = pygame.display.set_mode((640, 480))
bg_image = pygame.image.load('dotgamebg.jpg')#Фон главное меню

FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
SPACESIZE = 50
BOARDWIDTH = 8
BOARDHEIGHT = 8
WHITE_TILE = 'WHITE_TILE' #произвольно-уникальное значение
BLACK_TILE = 'BLACK_TILE' #произвольно-уникальное значение
EMPTY_SPACE = 'EMPTY_SPACE' #произвольно-уникальное значение
HINT_TILE = 'HINT_TILE' #произвольно-уникальное значение
ANIMATIONSPEED = 25

#количество места игрового поля слева и справа(XFIELD) или сверху и снизу(YFIELD)
XFIELD = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YFIELD = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN


def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('DOTGAME')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    boardImage = pygame.image.load('dotgametable.jpg')
    #smoothscale(), чтобы растянуть изображение доски на весь экран
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (XFIELD, YFIELD)
    BGIMAGE = pygame.image.load('dotgamebg.jpg')
    #smoothscale(), чтобы растянуть фоновое изображение на весь экран
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(boardImage, boardImageRect)

    #запуск основного цикла игры
    while True:
        if runGame() == False:
            break


def runGame():
    #сброс доски и игры
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = random.choice(['computer', 'player'])

    #рисовка стартовой доски и выбор цвета игрока
    drawBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()

    #создаёт объекты Surface и Rect для кнопок «Новая игра» и «Подсказки»
    newGameSurf = FONT.render('NEW GAME', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    hintsSurf = FONT.render('HINTS', True, TEXTCOLOR, TEXTBGCOLOR2)
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 8, 40)
    aboutSurf = FONT.render('About', True, TEXTCOLOR, TEXTBGCOLOR2)
    aboutRest = aboutSurf.get_rect()
    aboutRest.topright = (WINDOWWIDTH - 8, 80)

    while True:

        if turn == 'player':

            if getValidMoves(mainBoard, playerTile) == []:
                break
            movexy = None
            while movexy == None:

                if showHints:
                    boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                else:
                    boardToDraw = mainBoard

                checkForQuit()
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONUP:
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            return True
                        elif hintsRect.collidepoint( (mousex, mousey) ):
                            showHints = not showHints
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None

                drawBoard(boardToDraw)
                drawInfo(boardToDraw, playerTile, computerTile, turn)

                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)
                DISPLAYSURF.blit(aboutSurf, aboutRest)

                MAINCLOCK.tick(FPS)
                pygame.display.update()

            makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
            if getValidMoves(mainBoard, computerTile) != []:
                turn = 'computer'

        else:
            if getValidMoves(mainBoard, computerTile) == []:
                break

            drawBoard(mainBoard)
            drawInfo(mainBoard, playerTile, computerTile, turn)

            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)
            DISPLAYSURF.blit(aboutSurf, aboutRest)

            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            x, y = getComputerMove(mainBoard, computerTile)
            makeMove(mainBoard, computerTile, x, y, True)
            if getValidMoves(mainBoard, playerTile) != []:
                turn = 'player'

    drawBoard(mainBoard)
    scores = getScoreOfBoard(mainBoard)

    if scores[playerTile] > scores[computerTile]:
        text = 'YOU WIN! You beat the computer by %s points!' % \
               (scores[playerTile] - scores[computerTile])
    elif scores[playerTile] < scores[computerTile]:
        text = 'YOU LOSE! The computer beat you by %s points.' % \
               (scores[computerTile] - scores[playerTile])
    else:
        text = 'DRAWGAME!'

    textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(textSurf, textRect)

    text2Surf = BIGFONT.render('PLAY AGAIN?', True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

    yesSurf = BIGFONT.render('YES', True, TEXTCOLOR, TEXTBGCOLOR1)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

    noSurf = BIGFONT.render('NOW', True, TEXTCOLOR, TEXTBGCOLOR1)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yesRect.collidepoint( (mousex, mousey) ):
                    return True
                elif noRect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yesSurf, yesRect)
        DISPLAYSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def translateBoardToPixelCoord(x, y):
    return XFIELD + x * SPACESIZE + int(SPACESIZE / 2), YFIELD + y * SPACESIZE + int(SPACESIZE / 2)


def animateTileChange(tilesToFlip, tileColor, additionalTile):
    if tileColor == WHITE_TILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0

        if tileColor == WHITE_TILE:
            color = tuple([rgbValues] * 3) #значение RGB
        elif tileColor == BLACK_TILE:
            color = tuple([255 - rgbValues] * 3) #значение RGB

        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        checkForQuit()


def drawBoard(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    for x in range(BOARDWIDTH + 1):
        startx = (x * SPACESIZE) + XFIELD
        starty = YFIELD
        endx = (x * SPACESIZE) + XFIELD
        endy = YFIELD + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        startx = XFIELD
        starty = (y * SPACESIZE) + YFIELD
        endx = XFIELD + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YFIELD
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))


def getSpaceClicked(mousex, mousey):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XFIELD and \
               mousex < (x + 1) * SPACESIZE + XFIELD and \
               mousey > y * SPACESIZE + YFIELD and \
               mousey < (y + 1) * SPACESIZE + YFIELD:
                return (x, y)
    return None


def drawInfo(board, playerTile, computerTile, turn):#Счетчик игры
    scores = getScoreOfBoard(board)
    scoreSurf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def resetBoard(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE

    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE


def getNewBoard():
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)

    return board

#Допустимые ходы
def isValidMove(board, tile, xstart, ystart):
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile

    if tile == WHITE_TILE:
        otherTile = BLACK_TILE
    else:
        otherTile = WHITE_TILE

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = EMPTY_SPACE
    if len(tilesToFlip) == 0:
        return False
    return tilesToFlip


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


def getBoardWithValidMoves(board, tile):
    dupeBoard = copy.deepcopy(board)

    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    return dupeBoard


def getValidMoves(board, tile):
    validMoves = []

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves


def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE:
                xscore += 1
            if board[x][y] == BLACK_TILE:
                oscore += 1
    return {WHITE_TILE:xscore, BLACK_TILE:oscore}

"""вывести в главное меню для выбора"""
def enterPlayerTile():

    textSurf = FONT.render('CHOOSE YOUR COLOR:', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return [WHITE_TILE, BLACK_TILE]
                elif oRect.collidepoint( (mousex, mousey) ):
                    return [BLACK_TILE, WHITE_TILE]

        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def makeMove(board, tile, xstart, ystart, realMove=False):

    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tilesToFlip, tile, (xstart, ystart))

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True


def isOnCorner(x, y):
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)


def getComputerMove(board, computerTile):

    possibleMoves = getValidMoves(board, computerTile)

    random.shuffle(possibleMoves)

    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove


def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)):
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
#Главное меню

frame_color=pygame_menu.themes.THEME_DARK.copy()#Тема рамки
frame_color.set_background_color_opacity(0.4)#Прозрачность темы

menu = pygame_menu.Menu('DotGame', 400, 300,
                       theme=frame_color)# Название \ размер главное меню
# Кнопки главное меню
menu.add.text_input('Your name : ', default='')
menu.add.button('Play', main)
menu.add.button('Quit', pygame_menu.events.EXIT)
"""Добавить  
игрок выберает играть с компьютером или player2

"""
while True:

    surface.blit(bg_image, (0, 0))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    if menu.is_enabled():
        menu.update(events)
        menu.draw(surface)

    pygame.display.update()

#########################################################################

# if __name__ == '__main__':
#     main()
