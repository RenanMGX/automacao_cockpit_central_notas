from Entities.dependencies.logs import Logs
from getpass import getuser
import win32com.client
from datetime import datetime
import psutil
import subprocess
from time import sleep
import traceback
from functions import P
from functools import wraps

class SAPManipulation():
    @property
    def ambiente(self) -> str:
        return self.__ambiente
    
    @property
    def session(self) -> win32com.client.CDispatch:
        return self.__session
    @session.deleter
    def session(self):
        try:
            del self.__session
        except:
            pass
        
    @property
    def log(self) -> Logs:
        return Logs()
    
    @property
    def using_active_conection(self) -> bool:
        return self.__using_active_conection
    
    def __init__(self, *, user:str="", password:str="", ambiente:str="", using_active_conection:bool=False) -> None:
        self.__using_active_conection = using_active_conection
        self.__user:str = user
        self.__password:str = password
        self.__ambiente:str = ambiente
         
    #decorador
    @staticmethod
    def start_SAP(f):
        def wrap(self, *args, **kwargs):
            try:
                self.session
            except AttributeError:
                self.__conectar_sap()
            try:
                result =  f(self, *args, **kwargs)
            finally:
                sleep(5)
                if kwargs.get('fechar_sap_no_final') == True:
                    self.fechar_sap()
            return result
                #raise Exception("o sap precisa ser conectado primeiro!")
        return wrap
        
    @staticmethod
    def __verificar_conections(f):
        @wraps(f)
        def wrap(self, *args, **kwargs):
            _self:SAPManipulation = self
            
            result = f(_self, *args, **kwargs)
            try:
                if "Continuar com este logon sem encerrar os logons existentes".lower() in (choice:=_self.session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2")).text.lower():
                    choice.select()
                    _self.session.findById("wnd[0]").sendVKey(0)
            except:
                pass
            return result
        return wrap
    
    @__verificar_conections
    def __conectar_sap(self) -> None:
        print(P("Iniciando SAP"))
        self.__session: win32com.client.CDispatch
        if not self.using_active_conection:
            try:
                if not self.__verificar_sap_aberto():
                    subprocess.Popen(r"C:\Program Files (x86)\SAP\FrontEnd\SapGui\saplogon.exe")
                    sleep(5)
                
                SapGuiAuto: win32com.client.CDispatch = win32com.client.GetObject("SAPGUI")# type: ignore
                application: win32com.client.CDispatch = SapGuiAuto.GetScriptingEngine# type: ignore
                connection = application.OpenConnection(self.__ambiente, True) # type: ignore
                self.__session = connection.Children(0)# type: ignore
                
                self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = self.__user # Usuario
                self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = self.__password # Senha
                self.session.findById("wnd[0]").sendVKey(0)
                
                return 
            except Exception as error:
                if "connection = application.OpenConnection(self.__ambiente, True)" in traceback.format_exc():
                    raise Exception("SAP está fechado!")
                else:
                    self.log.register(status='Error', description=str(error), exception=traceback.format_exc())
                    raise ConnectionError(f"não foi possivel se conectar ao SAP motivo: {type(error).__class__} -> {error}")
        else:
            try:
                if not self.__verificar_sap_aberto():
                    raise Exception("SAP está fechado!")
                
                self.SapGuiAuto: win32com.client.CDispatch = win32com.client.GetObject("SAPGUI")
                self.application: win32com.client.CDispatch = self.SapGuiAuto.GetScriptingEngine
                self.connection: win32com.client.CDispatch = self.application.Children(0)
                self.__session = self.connection.Children(0)
                
            except Exception as error:
                if "self.connection: win32com.client.CDispatch = self.application.Children(0)" in traceback.format_exc():
                    raise Exception("SAP está fechado!")
                elif "SAP está fechado!" in traceback.format_exc():
                    raise Exception("SAP está fechado!")
                else:
                    self.log.register(status='Error', description=str(error), exception=traceback.format_exc())

    #@usar_sap
    def fechar_sap(self):
        print(P("fechando SAP!"))
        try:
            sleep(1)
            self.session.findById("wnd[0]").close()
            sleep(1)
            try:
                self.session.findById('wnd[1]/usr/btnSPOP-OPTION1').press()
            except:
                self.session.findById('wnd[2]/usr/btnSPOP-OPTION1').press()
                del self.__session
        except Exception as error:
            if 'O objeto chamado foi desconectado de seus clientes.' in str(error):
                print(P("SAP já está fechado", color='yellow'))
                return
            print(P(f"não foi possivel fechar o SAP {type(error)} | {error}"))

    @start_SAP
    def listar(self, campo):
        cont = 0
        for child_object in self.session.findById(campo).Children:
            print(P(f"{cont} | ID: {child_object.Id} | Type: {child_object.Type} | Text: {child_object.Text}"))
            cont += 1

    def __verificar_sap_aberto(self) -> bool:
        for process in psutil.process_iter(['name']):
            if "saplogon" in process.name().lower():
                return True
        return False    
    
    @start_SAP
    def __teste(self):
        print(P("testado"))
  
if __name__ == "__main__":
    pass
    #crd = Credential("SAP_QAS").load()
    
    #bot = SAPManipulation(user=crd['user'], password=crd['password'], ambiente="S4Q")
    #bot.conectar_sap()
    #bot._teste()
    
    #import pdb;pdb.set_trace()
    #bot.fechar_sap()
