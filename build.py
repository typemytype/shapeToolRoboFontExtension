import os, shutil
from mojo.extensions import ExtensionBundle

basePath = os.path.dirname(__file__)
sourcePath = os.path.join(basePath, 'source')
libPath = os.path.join(sourcePath, 'code')
htmlPath = os.path.join(sourcePath, 'docs')
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
B.version = '1.9'
B.launchAtStartUp = True
B.mainScript = 'drawShapesTool.py'
B.html = True
B.requiresVersionMajor = '4'
B.requiresVersionMinor = '0'
B.addToMenu = []

with open(licensePath) as license:
    B.license = license.read()

# copy README + images to extension docs
if not os.path.exists(htmlPath):
    os.makedirs(htmlPath)
shutil.copyfile(os.path.join(basePath, 'README.md'), os.path.join(htmlPath, 'index.md'))
for img in ['ShapeTool_dialog.png', 'ShapeTool_toolbar.png', 'ShapeToolMechanicIcon.png']:
    shutil.copyfile(os.path.join(basePath, img), os.path.join(htmlPath, img))

print('building extension...', end=' ')
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=pycOnly)
print('done!')

print()
print(B.validationErrors())
