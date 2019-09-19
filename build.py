import os, shutil
from mojo.extensions import ExtensionBundle

basePath = os.path.dirname(__file__)
sourcePath = os.path.join(basePath, 'source')
libPath = os.path.join(sourcePath, 'code')
htmlPath = None # os.path.join(sourcePath, 'docs')
resourcesPath = os.path.join(sourcePath, 'resources')
licensePath = os.path.join(basePath, 'LICENSE')
pycOnly = False
extensionFile = 'ShapeTool.roboFontExt'
extensionPath = os.path.join(basePath, extensionFile)

B = ExtensionBundle()
B.name = "ShapeTool"
B.developer = 'TypeMyType'
B.developerURL = 'http://www.typemytype.com'
B.icon = os.path.join(basePath, 'ShapeToolMechanicIcon.png')
B.version = '1.7'
B.launchAtStartUp = True
B.mainScript = 'drawShapesTool.py'
B.html = False
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '2'
B.addToMenu = []

with open(licensePath) as license:
    B.license = license.read()

print('building extension...', end=' ')
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=pycOnly)
print('done!')

print()
print(B.validationErrors())
