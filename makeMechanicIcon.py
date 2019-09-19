import os

size(512, 512)

B1 = BezierPath()
B1.oval(40, 170, 300, 300)
L, B, R, T = B1.bounds()
linearGradient((L, T), (R, B), [(0.3,), (0,)], [0, 1])
drawPath(B1)

B2 = BezierPath()
B2.rect(205, 45, 260, 260)
L, B, R, T = B2.bounds()
linearGradient((L, T), (R, B), [(0.3,), (0,)], [0, 1])
drawPath(B2)

folder = os.getcwd()
imgPath = os.path.join(folder, 'ShapeToolMechanicIcon.png')
saveImage(imgPath)