'''
Descripttion: 拯救“小又”
version: 
Author: Michael-Tian-Whu
Date: 2021-08-26 22:30:07
LastEditors: Michael-Tian-Whu
LastEditTime: 2021-08-28 22:38:24
'''
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from cvzone.HandTrackingModule import HandDetector

class Drop:
    def __init__(self, path, iniLoc=(50, 50)) -> None:
        self.cloc = iniLoc  # 起始位置
        self.src = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # 保留透明度
        self.img = self._cut()
        self.size = self.img.shape[:2]
        self.move = True  # 是否可以移动

    def _cut(self) -> np.ndarray:
        # 转灰度
        gray = cv2.cvtColor(self.src[:, :, 0:3], code=cv2.COLOR_BGR2GRAY)
        # 二值化
        _,  bin = cv2.threshold(
            gray, thresh=127, maxval=255, type=cv2.THRESH_OTSU)
        # 连通域检测
        _, _, stats, _ = cv2.connectedComponentsWithStats(
            bin, connectivity=8)
        x, y, w, h, s = stats[1]
        cutImg = self.src[y:y+h, x:x+w]
        return cutImg

    def update(self, cursor):
        self.cloc = cursor  # 光标
        
cap = cv2.VideoCapture(0)  # 0 内置摄像头
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
detector = HandDetector(detectionCon=0.9)  # 人手检测置信度
drops = []
for i in range(0, 3):
    loc = (100+100*i, 100)
    drop = Drop(f"src/drop{i}.png", loc)
    drops.append(drop)
font = ImageFont.truetype("font/黄令东齐伋复刻体.ttf", 50, encoding="utf-8")
font1 = ImageFont.truetype("font/黄令东齐伋复刻体.ttf", 100, encoding="utf-8")
wwhu = cv2.imread("src/whu.png", cv2.IMREAD_UNCHANGED)
gwhu = cv2.imread("src/gwhu.png", cv2.IMREAD_UNCHANGED)
wh, ww = wwhu.shape[:2]
pos = [0, 1, 2]
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 左右镜像
    img = detector.findHands(img, draw=True)
    lmList, bbox = detector.findPosition(img, draw=True)
    # 绘制背景
    cv2img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pilimg = Image.fromarray(cv2img)
    draw = ImageDraw.Draw(pilimg)
    draw.text((60, 10), "东湖", (255, 255, 255), font=font)
    draw.text((160, 10), "鉴湖", (255, 255, 255), font=font)
    draw.text((260, 10), "星湖", (255, 255, 255), font=font)
    draw.text((900, 30), "拯救小汉", (0, 0, 0), font=font1)
    img = cv2.cvtColor(np.asarray(pilimg), cv2.COLOR_RGB2BGR)
    whu = wwhu if pos else gwhu
    for i in range(0, wh):
        for j in range(0, ww):
            if whu[i][j][3]:
                img[400+i][120+j] = whu[i][j][0:3]
    # 检测手指接触，更新坐标
    for drop in drops:
        dx, dy = drop.cloc
        dh, dw = drop.size
        if drop.move:
            if lmList:
                length, _, _ = detector.findDistance(4, 8, img, draw=True)
                if length < 50:  # “捏”
                    cursor = lmList[8]
                    if dx-dw//2 < cursor[0] < dx+dw//2 and dy-dh//2 < cursor[1] < dy+dh//2:  # 在矩形内
                        for p in pos:
                            if 420-dw < cursor[0] < 420+dw and 420+90*p-dh < cursor[1] < 420+90*p+dh:
                                cursor = (420, 420+90*p)
                                drop.move = False
                                pos.remove(p)
                                break
                        drop.update(cursor)
                        cv2.rectangle(img, (cursor[0]-dw//2, cursor[1]-dh//2), (cursor[0]+dw//2, cursor[1]+dh//2),
                                      (0, 255, 255), 3)
        else:
            cv2.rectangle(img, (dx-dw//2, dy-dh//2), (dx+dw//2,
                          dy+dh//2), (177, 177, 177), 2, lineType=cv2.LINE_AA)
        for i in range(0, dh):
            for j in range(0, dw):
                if drop.img[i][j][3]:
                    img[drop.cloc[1]-dh//2+i][drop.cloc[0] -
                                              dw//2+j] = drop.img[i][j][0:3]
    cv2.imshow("waterbreak", img)
    cv2.waitKey(1)  # 1ms
