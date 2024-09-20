import os
from dependencies.sap import SAPManipulation
from dependencies.config import Config
from dependencies.credenciais import Credential
from dependencies.logs import Logs
import traceback
from datetime import datetime
from functools import wraps
from dependencies.functions import P, Functions
import shutil

class ExtrairRelatorio(SAPManipulation):
    download_path = os.path.join(os.getcwd(), 'download_path')
    
    def __init__(self) -> None:
        crd:dict = Credential(Config()['credential']['crd']).load()
        super().__init__(user=crd['user'], password=crd['password'], ambiente=crd['ambiente'])
    
    @staticmethod
    def preparar_entradas(f):
        @wraps(f)
        def wrap(self, *args, **kwargs):
            if (kwargs.get('file_name')):
                kwargs['file_name'] = kwargs['file_name'].lower()
                if not kwargs['file_name'].endswith('xlsx'):
                    kwargs['file_name'] += '.xlsx'
                kwargs['file_name'] = datetime.now().strftime("%d%m%Y%H%M%S") + kwargs['file_name']
            
            if (download_path:=kwargs.get('download_path')):
                if not os.path.exists(download_path):
                    os.makedirs(download_path)                  
        
            return f(self, *args, **kwargs)
        return wrap
    
    @preparar_entradas
    @SAPManipulation.start_SAP 
    def extrair(self, *, file_name:str, date_min:datetime, date_max:datetime, fechar_sap_no_final:bool, download_path:str=download_path,) -> str:
        print(P("Iniciando Extração"))
        try:
            print(P("entrando na transação 'start_report'"))
            self.session.findById("wnd[0]/tbar[0]/okcd").text = "/n start_report"
            self.session.findById("wnd[0]").sendVKey(0)
            
            print(P("abrindo programa 'AQICSYSTQV000043COCKPIT_CENTRA'"))
            self.session.findById("wnd[0]/usr/txtD_SREPOVARI-REPORT").text = "AQICSYSTQV000043COCKPIT_CENTRA"
            self.session.findById("wnd[0]").sendVKey(0)
            
            self.session.findById("wnd[0]/usr/ctxtSP$00001-LOW").text = date_min.strftime('%d.%m.%Y')
            self.session.findById("wnd[0]/usr/ctxtSP$00001-HIGH").text = date_max.strftime('%d.%m.%Y')
            self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
            print(P("gerando relatorio!"))
            
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").setCurrentCell(-1,"WRBTR")
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").selectColumn("WRBTR")
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").contextMenu()
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").selectContextMenuItem("&SUMC")
            
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").contextMenu()
            self.session.findById("wnd[0]/usr/cntlCONTAINER/shellcont/shell").selectContextMenuItem("&XXL")
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = download_path
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 10
            print(P("extraindo relatorio"))
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
            final_path:str = os.path.join(download_path, file_name)
            Functions.fechar_excel(final_path)
            print(P("extração finalizada!", color='green'))
            return final_path
            
        except Exception as error:
            Logs().register(status='Error', description=str(error), exception=traceback.format_exc())
            raise error
       
    @staticmethod
    def limpar_download_path(download_path:str=download_path):
        for file in os.listdir(download_path):
            file:str = os.path.join(download_path, file)
            try:
                if os.path.isfile(file):
                    os.unlink(file)
                elif os.path.isdir(file):
                    shutil.rmtree(file)
            except Exception as error:
                Logs().register(status='Error', description=str(error), exception=traceback.format_exc())

if __name__ == "__main__":
    pass
