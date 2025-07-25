import os
os.environ['project_name'] = "Automatização Dashboard - Cockpit Central de Notas"
from Entities.extrair_relatorio import ExtrairRelatorio
from Entities.dados import Dados, pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from patrimar_dependencies.arguments import Arguments
from patrimar_dependencies.functions import P
from patrimar_dependencies.logs import Logs_old
from patrimar_dependencies.sharepointfolder import SharePointFolders
import traceback
from getpass import getuser

class Execute:
    file_base_path:str = os.path.join(SharePointFolders(r"RPA - Dados\Dados - Contabilidade").value, "base.json")
    if not os.path.exists(file_base_path):
        pd.DataFrame().to_json(file_base_path, orient='records', date_format='iso')
        
    file_base_vtin_path:str = os.path.join(SharePointFolders(r"RPA - Dados\Dados - Contabilidade").value, "base_vtin.json")
    if not os.path.exists(file_base_vtin_path):
        pd.DataFrame().to_json(file_base_vtin_path, orient='records', date_format='iso')
    
    @staticmethod
    def start():
        print(P("Iniciando Automação", color='blue'))
        ExtrairRelatorio.limpar_download_path()
        download_file = ExtrairRelatorio().extrair(file_name="cockpit_central_notas", date_min=(datetime.now() - relativedelta(days=7)), date_max=datetime.now(), fechar_sap_no_final=True)
        Dados(download_file).incrementar(file_base_path=Execute.file_base_path)
        
        ExtrairRelatorio.limpar_download_path()
        download_file = ExtrairRelatorio().extrair_vtin(file_name="vtin", date_min=(datetime.now() - relativedelta(days=7)), date_max=datetime.now(), fechar_sap_no_final=True)
        Dados(download_file).incrementar(file_base_path=Execute.file_base_vtin_path)
        
        print(P("Fim da automaçao", color='green'))
        Logs_old().register(status='Concluido', description="Automação finalizada com Sucesso!")
    
if __name__ == "__main__":
    Arguments({
        'start': Execute.start
    })