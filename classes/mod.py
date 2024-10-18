import requests
from zipfile import ZipFile
import rarfile
from rarfile import RarFile
rarfile.UNRAR_TOOL = r'UnRAR.exe'
import io

import os

class Mod:
    def __init__(self,name,dic,ownedPacks):
        self.name : str = name
        self.link : str = dic["Link"]
        self.fileName : str = dic["FileName"]
        self.linkEA : str = dic["LinkEA"]
        self.toOverride : bool = "toOverride" in dic
        self.filesPerEP = dic["filesPerEP"]
        self.ownedPacks : set = ownedPacks

    def __repr__(self):
        return repr(f'''Name: {self.name} | Filename: {self.fileName} | Link: {self.link} | LinkEA: {self.linkEA} | toOverride: {self.toOverride} | filesPerEP: {self.filesPerEP}''')

    def downloadMod(self):
        req = requests.get(self.link)

        if req.status_code != 200:
            return -1
        
        path = f"Download/{"Mods" if not self.toOverride else "Override"}/{self.name}/"
        os.makedirs(path, exist_ok=True)
        with open(path+self.fileName,"wb") as f:
            f.write(req.content)

    def downloadAndExtractMod(self,path=None):
        print(f"Downloding {self.fileName} from {self.link}")
        req = requests.get(self.link)
        if req.status_code != 200:
            return -1
        
        if not path:
            path = f"Download/{"Mods" if not self.toOverride else "Override"}/{self.name.replace(":","")}/"
        else:
            path = f"{path}/{"Mods" if not self.toOverride else "Override"}/{self.name.replace(":","")}/"

        os.makedirs(path, exist_ok=True)
        EPDependentFiles =  dict((v,k) for k,v in self.filesPerEP.items()) if self.filesPerEP else {}

        if self.fileName.endswith(".zip") or self.fileName.endswith(".rar"):
            archive = ZipFile(io.BytesIO(req.content)) if self.fileName.endswith(".zip") else RarFile(io.BytesIO(req.content))
            fileList = archive.filelist if self.fileName.endswith(".zip") else archive.infolist()
            for fileInfo in fileList:
                if fileInfo.filename not in EPDependentFiles or EPDependentFiles[fileInfo.filename] in self.ownedPacks:
                    print(f"Extracting {fileInfo.filename} to {path}")
                    archive.extract(fileInfo,path)
            archive.close()
        else:
            with open(path+self.fileName,"wb") as f:
                print(f"Writing {self.fileName} to {path}")
                f.write(req.content)

        return 1
        
    
    def downloadAndExtractModWithFileMap(self,fileMap):
        print(f"Downloding {self.fileName} from {self.link}")
        req = requests.get(self.link)
        if req.status_code != 200:
            return -1
               
        EPDependentFiles =  dict((v,k) for k,v in self.filesPerEP.items()) if self.filesPerEP else {}

        if self.fileName.endswith(".zip") or self.fileName.endswith(".rar"):
            archive = ZipFile(io.BytesIO(req.content)) if self.fileName.endswith(".zip") else RarFile(io.BytesIO(req.content))
            for fileName,filePath in fileMap.items():
                if fileName not in EPDependentFiles or EPDependentFiles[fileName] in self.ownedPacks:
                    os.makedirs(filePath, exist_ok=True)
                    print(f"Extracting {fileName} to {filePath}")
                    archive.extract(fileName,filePath)
            archive.close()

        return 1