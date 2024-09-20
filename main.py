from Entities.extrair_relatorio import ExtrairRelatorio
from Entities.dados import Dados
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from Entities.dependencies.arguments import Arguments
from Entities.dependencies.functions import P
from Entities.dependencies.logs import Logs
import traceback

class Execute:
    file_base_path:str = f"C:\\Users\\renan.oliveira\\PATRIMAR ENGENHARIA S A\\RPA - Documentos\\RPA - Dados\\Dados - Contabilidade\\base.json"
    if not os.path.exists(file_base_path):
        try:
            raise FileNotFoundError(f"não foi possivel localizar o arquivo '{file_base_path}'")
        except Exception as error:
            Logs().register(status='Error', description=str(error), exception=traceback.format_exc())
            raise error
    
    @staticmethod
    def start():
        print(P("Iniciando Automação", color='blue'))
        download_file = ExtrairRelatorio().extrair(file_name="cockpit_central_notas", date_min=(datetime.now() - relativedelta(days=7)), date_max=datetime.now(), fechar_sap_no_final=True)
        Dados(download_file).incrementar(file_base_path=Execute.file_base_path)
        ExtrairRelatorio.limpar_download_path()
        print(P("Fim da automaçao", color='green'))
        Logs().register(status='Concluido', description="Automação finalizada com Sucesso!")
    
if __name__ == "__main__":
    Arguments({
        'start': Execute.start
    })