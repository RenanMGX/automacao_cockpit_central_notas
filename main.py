import os
os.environ['project_name'] = "Automatização Dashboard - Cockpit Central de Notas"
from Entities.extrair_relatorio import ExtrairRelatorio
from Entities.dados import Dados, pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from patrimar_dependencies.functions import P
from patrimar_dependencies.sharepointfolder import SharePointFolders
import traceback
from getpass import getuser
from botcity.maestro import * #type:ignore

class ExecuteAPP:
    maestro:BotMaestroSDK|None
    try:
        maestro = BotMaestroSDK().from_sys_args()
        maestro.get_execution()
    except:
        maestro = None
    
    
    file_base_path:str = os.path.join(SharePointFolders(r"RPA - Dados\Dados - Contabilidade").value, "base.json")
    if not os.path.exists(file_base_path):
        pd.DataFrame().to_json(file_base_path, orient='records', date_format='iso')
        
    file_base_vtin_path:str = os.path.join(SharePointFolders(r"RPA - Dados\Dados - Contabilidade").value, "base_vtin.json")
    if not os.path.exists(file_base_vtin_path):
        pd.DataFrame().to_json(file_base_vtin_path, orient='records', date_format='iso')
    
    @staticmethod
    def start(
        *,
        sap_user:str,
        sap_password:str,
        sap_ambiente:str,
    ):
        
        extrair_relatorio = ExtrairRelatorio(
            user=sap_user,
            password=sap_password,
            ambiente=sap_ambiente
        )
        
        
        print(P("Iniciando Automação", color='blue'))
        ExtrairRelatorio.limpar_download_path()
        download_file = extrair_relatorio.extrair(file_name="cockpit_central_notas", date_min=(datetime.now() - relativedelta(days=7)), date_max=datetime.now(), fechar_sap_no_final=True)
        Dados(download_file).incrementar(file_base_path=ExecuteAPP.file_base_path)
        
        ExtrairRelatorio.limpar_download_path()
        download_file = extrair_relatorio.extrair_vtin(file_name="vtin", date_min=(datetime.now() - relativedelta(days=7)), date_max=datetime.now(), fechar_sap_no_final=True)
        Dados(download_file).incrementar(file_base_path=ExecuteAPP.file_base_vtin_path)
        
        print(P("Fim da automaçao", color='green'))
    
if __name__ == "__main__":
    from patrimar_dependencies.credenciais import Credential
    
    sap_crd:dict = Credential(
        path_raiz=SharePointFolders(r"RPA - Dados\CRD\.patrimar_rpa\credenciais").value,
        name_file="SAP_PRD"
    ).load()
    
    ExecuteAPP.start(
        sap_user=sap_crd['user'],
        sap_password=sap_crd['password'],
        sap_ambiente=sap_crd['ambiente']
    )
    