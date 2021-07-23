import random
import time

import pygame
class MainGame():
    window = None   # 游戏窗口
    height = 500    # 窗口高度
    width = 800     # 窗口宽度
    myTank = None   # 我的坦克
    enemyTankList = []  # 敌方坦克列表
    enemyTankCount = 5  # 总共要生成的敌方坦克数量
    enemyTankNum = 0    # 已经生成的敌方坦克数量
    myBulletList = []   # 我的坦克发射的子弹列表
    enemyBulletList = []    # 敌方坦克发射的子弹列表
    brickList = []  # 砖墙列表
    steelList = []  # 钢墙列表
    explode = None  # 子弹击中后的爆炸
    me = None   # 我方指挥所（仅鹰形建筑）
    def __init__(self):
        pass
    def start(self):
        pygame.display.init()
        MainGame.window = pygame.display.set_mode([MainGame.width,MainGame.height])
        # 创建我方指挥部
        MainGame.me = self.createMe()
        # 创建我的坦克，不和指挥部及其周围砖墙冲突
        MainGame.myTank = MyTank(random.randint(0, 750), random.randint(0, 450))
        while (MainGame.me.rect.top - 50 < MainGame.myTank.rect.top + 50 < MainGame.me.rect.top + 150) or (MainGame.me.rect.left - 100 < MainGame.myTank.rect.left < MainGame.me.rect.left + 100):
            MainGame.myTank = MyTank(random.randint(0, 750), random.randint(0, 450))
        # 创建墙
        self.createWall()
        # 创建一辆敌方坦克
        self.createEnemyTank()
        pygame.display.set_caption("坦克大战")
        # 游戏开始音效
        start = Music('./music/readygo.mp3')
        start.play()
        while True:
            MainGame.window.fill(pygame.Color(44, 57, 0))
            # 还没有生成5辆坦克的情况下1%概率生成一辆敌方坦克
            if MainGame.enemyTankNum < MainGame.enemyTankCount and random.randint(0,100) == 1:
                self.createEnemyTank()
            # 获取事件输入
            self.getEvent()
            # 如果现在没有敌方坦克并且已经生成了五辆敌方坦克，显示胜利并退出
            if len(self.enemyTankList) == 0 and MainGame.enemyTankNum == 5:
                MainGame.window.blit(self.getText("You win!"), (200, 200))
                pygame.display.update()
                start = Music('./music/victory.mp3')
                start.play()
                time.sleep(2)
                exit()  # 显示win
            # 如果我的坦克还存活，显示
            if self.myTank and self.myTank.live:
                MainGame.myTank.displayTank()
            # 否则，我的坦克被击毁，显示失败并退出
            else:
                MainGame.window.blit(self.getText("You lose!"),(200,200))
                pygame.display.update()
                start = Music('./music/lose.mp3')
                start.play()
                time.sleep(2)
                exit()  # 显示lose
            # 如果我方指挥部还存活，显示
            if self.me.live:
                self.me.displayMe()
            # 否则，我方指挥部被击毁，显示失败并退出
            else:
                MainGame.window.blit(self.getText("You lose!"),(200,200))
                pygame.display.update()
                start = Music('./music/lose.mp3')
                start.play()
                time.sleep(2)
                exit()  # 显示lose
            self.blitEnemyTank()    # 显示敌方坦克
            self.blitWall()     # 显示墙壁
            # 如果我的坦克的持续移动开关打开，移动
            if MainGame.myTank and not MainGame.myTank.stop:
                MainGame.myTank.move()
                # 如果我的坦克与其他碰撞，使我的坦克停滞在其他物体边缘
                if MainGame.myTank.isCollide():
                    curDirection = MainGame.myTank.direction
                    if curDirection == 'left':
                        MainGame.myTank.direction = 'right'
                        MainGame.myTank.speed = 1
                        while MainGame.myTank.isCollide():
                            MainGame.myTank.move()
                        MainGame.myTank.speed = 6
                        MainGame.myTank.direction = curDirection
                    elif curDirection == 'right':
                        MainGame.myTank.direction = 'left'
                        MainGame.myTank.speed = 1
                        while MainGame.myTank.isCollide():
                            MainGame.myTank.move()
                        MainGame.myTank.speed = 6
                        MainGame.myTank.direction = curDirection
                    elif curDirection == 'up':
                        MainGame.myTank.direction = 'down'
                        MainGame.myTank.speed = 1
                        while MainGame.myTank.isCollide():
                            MainGame.myTank.move()
                        MainGame.myTank.speed = 6
                        MainGame.myTank.direction = curDirection
                    elif curDirection == 'down':
                        MainGame.myTank.direction = 'up'
                        MainGame.myTank.speed = 1
                        while MainGame.myTank.isCollide():
                            MainGame.myTank.move()
                        MainGame.myTank.speed = 6
                        MainGame.myTank.direction = curDirection
            # 显示我的子弹
            self.blitMyBullet()
            # 显示敌方子弹
            self.blitEnemyBullet()
            # 延时更新显示
            time.sleep(0.02)
            pygame.display.update()

    # 创建一个敌方坦克。
    # 通过while True循环直到随机数left,top,speed生成的敌方坦克不和我的坦克、砖墙、钢墙、已经存在的敌方坦克冲突，将其加入敌方坦克列表。
    def createEnemyTank(self):
        # while len(MainGame.enemyTankList) < MainGame.enemyTankCount:
        while True:
            speed = random.randint(2, 4)
            left = random.randint(0, 750)
            top = random.randint(0, 450)
            enemyTank = EnemyTank(left, top, speed)
            # 不能和我的坦克
            if not pygame.sprite.collide_rect(enemyTank,MainGame.myTank):
                # 坦克不能在砖墙上
                global flag3
                flag3 = 1
                for wall in MainGame.brickList:
                    if pygame.sprite.collide_rect(wall, enemyTank):
                        flag3 = 0
                        break
                if flag3 == 0:
                    continue
                # 不能生成在钢墙上
                global flag4
                flag4 = 1
                for wall in MainGame.steelList:
                    if pygame.sprite.collide_rect(wall, enemyTank):
                        flag4 = 0
                        break
                if flag4 == 0:
                    continue
                # 不能和敌方坦克
                global flag5
                flag5 = 1
                for wall in MainGame.enemyTankList:
                    if pygame.sprite.collide_rect(wall, enemyTank):
                        flag5 = 0
                        break
                if flag5 == 0:
                    continue
                MainGame.enemyTankList.append(enemyTank)
                MainGame.enemyTankNum += 1
                appear = Music('./music/appear.mp3')
                appear.play()
                break

    # 生成我方指挥部。随机数位置生成指挥部，并生成指挥部周围砖墙，将砖墙加入砖墙列表，函数返回生成的指挥部。
    def createMe(self):
        me = Me(random.randint(50,700),random.randint(50,400))
        # 生成指挥部周边砖墙
        wallTemp = Wall(me.rect.left + 50, me.rect.top + 50, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left + 50, me.rect.top, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left + 50, me.rect.top - 50, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left, me.rect.top - 50, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left, me.rect.top + 50, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left - 50, me.rect.top + 50, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left - 50, me.rect.top, False)
        MainGame.brickList.append(wallTemp)
        wallTemp = Wall(me.rect.left - 50, me.rect.top - 50, False)
        MainGame.brickList.append(wallTemp)
        return me

    # 生成十组砖墙和五块钢墙。
    # 随机数生成每组砖墙的左上角位置和每组砖墙包含砖的块数，将这些砖拼接到砖墙组的下方或者右方，并且保证不和已经存在的砖墙和我的坦克冲突，将满足条件的砖加入砖墙列表。
    # While循环直到生成五块不与砖墙、已经存在的钢墙、我的坦克冲突的钢墙，加入钢墙列表。
    def createWall(self):
        groupNum = 10
        num = 0
        while num < groupNum:
            groupLeft = random.randint(0, 750)
            groupTop = random.randint(0, 450)
            groupCount = random.randint(2,8)
            leftCount = 0
            TopCount = 0
            for i in range(groupCount):
                leftChoice = random.choice([groupLeft,groupLeft + 50 * leftCount])
                if leftChoice == groupLeft + 50 * leftCount and leftChoice < 750:
                    leftCount += 1
                if leftChoice < 750:
                    left = leftChoice
                else:
                    continue

                topChoice = random.choice([groupTop,groupTop + 50 * TopCount])
                if topChoice == groupTop + 50 * TopCount and topChoice < 450:
                    TopCount += 1
                if topChoice < 450:
                    top = topChoice
                else:
                    continue

                wallTemp = Wall(left, top,False)
                global flag
                flag = 1
                for wall in MainGame.brickList:
                    if pygame.sprite.collide_rect(wall, wallTemp):
                        flag = 0
                        break
                if flag == 1 and not pygame.sprite.collide_rect(wallTemp,MainGame.myTank):
                    MainGame.brickList.append(wallTemp)
            num += 1

        while len(MainGame.steelList) < 5:
            left = random.randint(0,750)
            top = random.randint(0,450)
            wallTemp = Wall(left,top,True)
            # 钢墙不能生成在砖墙上
            global flag3
            flag3 = 1
            for wall in MainGame.brickList:
                if pygame.sprite.collide_rect(wall, wallTemp):
                    flag3 = 0
                    break
            if flag3 == 0:
                continue
            # 钢墙不能生成在钢墙上
            global flag4
            flag4 = 1
            for wall in MainGame.steelList:
                if pygame.sprite.collide_rect(wall, wallTemp):
                    flag4 = 0
                    break
            if flag4 == 0:
                continue
            # 不能我的坦克上
            if not pygame.sprite.collide_rect(wallTemp, MainGame.myTank):
                MainGame.steelList.append(wallTemp)

    # 显示敌方坦克列表中的坦克。
    # 如果敌方坦克还存活，就显示敌方坦克并调用敌方坦克移动、射击方法；如果敌方坦克已经被击毙，将其移出敌方坦克列表。
    def blitEnemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            if enemyTank.live:
                enemyTank.displayTank()
                enemyTank.move()
                enemyBullet = enemyTank.shot()
                if enemyBullet:
                    self.enemyBulletList.append(enemyBullet)
            else:
                MainGame.enemyTankList.remove(enemyTank)

    # 显示砖墙和钢墙列表中的砖墙和钢墙。
    # 对砖墙需要判断存活与否，若存活才显示；若已被击毁，移出列表。
    def blitWall(self):
        for wall in MainGame.brickList:
            if wall.live:
                wall.displayWall()
            else:
                MainGame.brickList.remove(wall)
        for wall in MainGame.steelList:
            wall.displayWall()

    # 若我的子弹列表中的子弹还存在，就调用子弹的显示、移动、击中敌方坦克、击中砖墙、击中钢墙、击中我方指挥部的方法；
    # 若子弹已不存在，移出列表。
    def blitMyBullet(self):
        for bullet in self.myBulletList:
            if bullet.live is True:
                bullet.displayBullet()
                bullet.move()
                bullet.hitEnemyTank()
                bullet.hitBrick()
                bullet.hitSteel()
                bullet.hitMe()
            else:
                self.myBulletList.remove(bullet)

    # 若敌方子弹列表中的子弹还存在，就调用子弹的显示、移动、击中我方坦克、击中砖墙、击中钢墙、击中我方指挥部的方法；
    # 若子弹已不存在，移出列表。
    def blitEnemyBullet(self):
        for bullet in self.enemyBulletList:
            if bullet.live is True:
                bullet.displayBullet()
                bullet.move()
                bullet.hitMyTank()
                bullet.hitBrick()
                bullet.hitSteel()
                bullet.hitMe()
            else:
                self.enemyBulletList.remove(bullet)

    # 获取事件处理。
    # 如果有键按下，按键为方向键，则更改我的坦克方向并把我的坦克持续移动开关打开；
    # 按键为空格键，将我的坦克发射的子弹加入我的子弹列表。
    # 如果方向键松开，我的坦克持续移动开关关闭，我的坦克停下。
    def getEvent(self):
        eventList = pygame.event.get()
        for event in eventList:
            if event.type == pygame.QUIT:
                self.end()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    MainGame.myTank.direction = 'left'
                    MainGame.myTank.stop = False
                elif event.key == pygame.K_RIGHT:
                    MainGame.myTank.direction = 'right'
                    MainGame.myTank.stop = False
                elif event.key == pygame.K_UP:
                    MainGame.myTank.direction = 'up'
                    MainGame.myTank.stop = False
                elif event.key == pygame.K_DOWN:
                    MainGame.myTank.direction = 'down'
                    MainGame.myTank.stop = False
                elif event.key == pygame.K_SPACE:
                    if len(MainGame.myBulletList) < 2:
                        start = Music('./music/biu.mp3')
                        start.play()
                        myBullet = Bullet(MainGame.myTank)
                        MainGame.myBulletList.append(myBullet)
                elif event.key == pygame.K_ESCAPE:
                    exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    MainGame.myTank.stop = True

    # 参数text为要显示在屏幕上的字符串。函数返回一个红色text内容的Surface。
    def getText(self,text):
        pygame.font.init()
        font = pygame.font.SysFont('laoui',120)
        textSurface = font.render(text,True,pygame.Color(255,0,0))
        return textSurface

    # 退出游戏
    def end(self):
        exit()

# 基本物件类
class BaseItem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

# 坦克类
class Tank(BaseItem):
    # 参数left,top为坦克左上角横坐标和纵坐标。
    # 初始化坦克图片、方向、矩形、速度、持续移动开关和生命。
    def __init__(self,left,top):
        self.images = {
            'up':pygame.image.load('./images/myTankUp.png'),
            'down':pygame.image.load('./images/myTankDown.png'),
            'left':pygame.image.load('./images/myTankLeft.png'),
            'right':pygame.image.load('./images/myTankRight.png'),
        }
        self.direction = 'up'
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = 6
        self.stop = True #持续移动开关
        self.live = True

    # 根据坦克方向选择坦克图片，并显示到窗口。
    def displayTank(self):
        self.image = self.images[self.direction]
        MainGame.window.blit(self.image,self.rect)

    # 如果没有到达窗口边界，朝坦克方向前进坦克速度数值的距离。
    def move(self):
        if self.direction == 'left':
            if self.rect.left > 0:
                self.rect.left -= self.speed
        elif self.direction == 'right':
            if self.rect.left+self.rect.height < MainGame.width:
                self.rect.left += self.speed
        elif self.direction == 'up':
            if self.rect.top > 0:
                self.rect.top -= self.speed
        elif self.direction == 'down':
            if self.rect.top + self.rect.height < MainGame.height:
                self.rect.top += self.speed

    # 用自身生成一个子弹（即自己发射子弹）并返回子弹。
    def shot(self):
        return Bullet(self)

# 我的坦克类
class MyTank(Tank):
    def __init__(self,left,top):
        super(MyTank, self).__init__(left,top)

    # 判断是否与敌方坦克、钢墙、砖墙碰撞，若是，返回True
    def isCollide(self):
        # 与敌方坦克碰撞
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(self, enemyTank) and enemyTank != self:
                return True
        # 与钢墙碰撞
        for brick in MainGame.steelList:
            if pygame.sprite.collide_rect(self, brick):
                return True
        # 与砖墙碰撞
        for brick in MainGame.brickList:
            if pygame.sprite.collide_rect(self, brick):
                return True

# 敌方坦克类
class EnemyTank(Tank):
    # 参数left,top为坦克左上角横坐标和纵坐标，speed为坦克速度。
    # 调用坦克类Tank的初始化方法。初始化坦克图片、方向、矩形、速度、持续移动开关、生命和计时。
    def __init__(self,left,top,speed):
        super(EnemyTank, self).__init__(left,top)
        self.images = {
            'up':pygame.image.load('./images/enemyTankUp.png'),
            'down':pygame.image.load('./images/enemyTankDown.png'),
            'left':pygame.image.load('./images/enemyTankLeft.png'),
            'right':pygame.image.load('./images/enemyTankRight.png'),
        }
        self.direction = self.randDirection()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = speed
        self.stop = True #持续移动开关
        self.timeCount = 35

    def displayEnemyTank(self):
        super().displayTank()

    # 转向与现在方向相反的方向
    def deverse(self):
        if self.direction == 'up':
            self.direction = 'down'
        elif self.direction == 'down':
            self.direction = 'up'
        elif self.direction == 'right':
            self.direction = 'left'
        elif self.direction == 'left':
            self.direction = 'right'

    # 判断是否与敌方坦克列表中的坦克、钢墙、砖墙、我的坦克碰撞，若是，返回True。
    def isCollide(self):
        # 与敌方坦克碰撞
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(self, enemyTank) and enemyTank != self:
                return True
        # 与钢墙碰撞
        for brick in MainGame.steelList:
            if pygame.sprite.collide_rect(self, brick):
                return True
        # 与砖墙碰撞
        for brick in MainGame.brickList:
            if pygame.sprite.collide_rect(self, brick):
                return True
        # 与我的坦克碰撞
        if pygame.sprite.collide_rect(self, MainGame.myTank):
            return True

    def move(self):
        # 如果发生了碰撞，调用deverse转向。
        if self.isCollide():
            self.deverse()
        # 如果没有到达窗口边界，朝坦克方向前进坦克速度数值的距离；否则随机转向。
        if self.direction == 'left':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.direction = self.randDirection()
        elif self.direction == 'right':
            if self.rect.left+self.rect.height < MainGame.width:
                self.rect.left += self.speed
            else:
                self.direction = self.randDirection()
        elif self.direction == 'up':
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                self.direction = self.randDirection()
        elif self.direction == 'down':
            if self.rect.top + self.rect.height < MainGame.height:
                self.rect.top += self.speed
            else:
                self.direction = self.randDirection()
        # 如果计时归零，随机转向，计时重置；否则计时减一。
        if self.timeCount != 0:
            self.timeCount = self.timeCount - 1
        else:
            self.direction = self.randDirection()
            self.timeCount = 35

    # 返回随机方向的字符串。
    def randDirection(self):
        num = random.randint(1,4)
        if num == 1:
            return 'up'
        elif num == 2:
            return 'down'
        elif num == 3:
            return 'left'
        elif num == 4:
            return 'right'

    # 使用随机数，有1%概率发射子弹，函数返回子弹。
    def shot(self):
        num = random.randint(1,1000)
        if num <= 10:
            return Bullet(self)

# 子弹类
class Bullet(BaseItem):
    # 参数tank为发射子弹的坦克。
    # 初始化子弹图片、方向、矩形、速度、生命。
    def __init__(self,tank):
        self.images = {
            'up': pygame.image.load('./images/bulletUp.png'),
            'down': pygame.image.load('./images/bulletDown.png'),
            'left': pygame.image.load('./images/bulletLeft.png'),
            'right': pygame.image.load('./images/bulletRight.png'),
        }
        self.direction = tank.direction
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.speed = tank.speed*1.5
        self.live = True    # bullet碰撞后清除
        # 根据子弹方向、矩形长宽和坦克，计算子弹左上角位置left，top。
        if self.direction == 'up':
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'down':
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == 'left':
            self.rect.left = tank.rect.left - self.rect.width
            self.rect.top = tank.rect.top + tank.rect.height/2 - self.rect.height/2
        elif self.direction == 'right':
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.height/2 - self.rect.height/2

    def displayBullet(self):
        MainGame.window.blit(self.image,self.rect)

    # 如果没有到达窗口边界，朝子弹方向前进速度数值的距离；否则子弹消亡，改变生命。
    def move(self):
        if self.direction == 'left':
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.live = False
        elif self.direction == 'right':
            if self.rect.left+self.rect.height < MainGame.width:
                self.rect.left += self.speed
            else:
                self.live = False
        elif self.direction == 'up':
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                self.live = False
        elif self.direction == 'down':
            if self.rect.top + self.rect.height < MainGame.height:
                self.rect.top += self.speed
            else:
                self.live = False

    # 如果和敌方坦克冲突，生成一个爆炸效果，更新屏幕，子弹和敌方坦克消亡，播放击毁音效。
    def hitEnemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(enemyTank,self):
                MainGame.explode = Explode(enemyTank)
                MainGame.explode.displayExplode()
                pygame.display.update()
                MainGame.explode = None
                self.live = False
                enemyTank.live = False
                start = Music('./music/crack.mp3')
                start.play()

    # 如果和我的坦克冲突，生成一个爆炸效果，更新屏幕，子弹和我的坦克消亡，播放击毁音效。
    def hitMyTank(self):
        if pygame.sprite.collide_rect(self,MainGame.myTank):
            MainGame.explode = Explode(MainGame.myTank)
            MainGame.explode.displayExplode()
            pygame.display.update()
            MainGame.explode = None
            self.live = False
            MainGame.myTank.live = False
            start = Music('./music/crack.mp3')
            start.play()

    # 如果和我方指挥部冲突，生成一个爆炸效果，更新屏幕，子弹和我方指挥部消亡，播放击毁音效。
    def hitMe(self):
        if pygame.sprite.collide_rect(self,MainGame.me):
            MainGame.explode = Explode(MainGame.me)
            MainGame.explode.displayExplode()
            pygame.display.update()
            MainGame.explode = None
            self.live = False
            MainGame.me.live = False
            start = Music('./music/crack.mp3')
            start.play()

    # 如果和砖墙冲突，生成一个爆炸效果，更新屏幕，子弹和砖墙消亡，播放击毁音效。
    def hitBrick(self):
        for brick in MainGame.brickList:
            if pygame.sprite.collide_rect(brick, self):
                MainGame.explode = Explode(brick)
                MainGame.explode.displayExplode()
                pygame.display.update()
                MainGame.explode = None
                self.live = False
                brick.live = False
                start = Music('./music/crack.mp3')
                start.play()

    # 如果和钢墙冲突，生成一个爆炸效果，更新屏幕，子弹消亡，播放碰撞钢墙音效。
    def hitSteel(self):
        for brick in MainGame.steelList:
            if pygame.sprite.collide_rect(brick, self):
                MainGame.explode = Explode(brick)
                MainGame.explode.displayExplode()
                pygame.display.update()
                MainGame.explode = None
                self.live = False
                start = Music('./music/steel.mp3')
                start.play()

# 爆炸类
class Explode():
    # 参数tank为与子弹碰撞的物体。
    # 初始化爆炸图片、矩形。
    def __init__(self,tank):
        self.rect = tank.rect
        self.image = pygame.image.load('images/explode.png')
    def  displayExplode(self):
        MainGame.window.blit(self.image,self.rect)

# 墙壁类
class Wall(BaseItem):
    # 参数left,top为墙壁左上角横坐标和纵坐标，isSteel是标识要生成的墙壁是否是钢墙的布尔值。
    # 初始化墙壁图片、矩形、生命。
    def __init__(self,left,top,isSteel):
        if isSteel:
            self.image = pygame.image.load('images/steelWall.png')
        else:
            self.image = pygame.image.load('images/brick1.png')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.live = True
    def displayWall(self):
        MainGame.window.blit(self.image,self.rect)

# 我方指挥部类
class Me():
    # 参数left,top为指挥部左上角横坐标和纵坐标。
    def __init__(self,left,top):
        self.image = pygame.image.load('images/me.png')
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.live = True
    def displayMe(self):
        MainGame.window.blit(self.image,self.rect)

# 音乐类
class Music():
    # 参数fileName为音乐路径的字符串。
    # 初始化mixer模块，加载fileName音效。
    def __init__(self,fileName):
        pygame.mixer.init()
        pygame.mixer.music.load(fileName)

    def play(self):
        pygame.mixer.music.play()


# 游戏开始
MainGame().start()