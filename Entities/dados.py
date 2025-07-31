import os
import shutil
import pandas as pd
from functools import wraps
from patrimar_dependencies.functions import P
import traceback
from botcity.maestro import * #type:ignore
import json

class Dados:
    maestro:BotMaestroSDK|None
    try:
        maestro = BotMaestroSDK().from_sys_args()
        maestro.get_execution()
    except:
        maestro = None
    
    @property
    def file_path(self) -> str:
        return self.__file_path
    
    @property
    def df(self) -> pd.DataFrame:
        return self.__df
    
    def __init__(self, file_path:str) -> None:
        self.__file_path:str = file_path
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"arquivo {self.file_path=} não encontrado")
        
        if self.file_path.endswith('xlsx'):
            print(P(f"carregando arquivo {self.file_path}"))
            self.__df:pd.DataFrame = pd.read_excel(self.file_path, dtype=str)
        else:
            raise TypeError(f"tipo do arquivo invalido {self.file_path=}")
    
    @staticmethod
    def validar_file_base(f):
        @wraps(f)
        def wrap(self, *args, **kwargs):
            if (file_base_path:=kwargs.get('file_base_path')):
                if not os.path.exists(file_base_path):
                    raise FileNotFoundError(f"o arquivo base {file_base_path=} não foi encontrado!")
                if not file_base_path.endswith('.json'):
                    raise TypeError("é aceito apenas arquivos do tipo Json")
            
            return f(self, *args, **kwargs)
        return wrap
    
    @validar_file_base
    def incrementar(self, *, file_base_path:str, coluna_chaves:str='Chave de acesso de 44 dígitos'):
        try:
            df:pd.DataFrame = pd.read_json(file_base_path)
            df_concat:pd.DataFrame = pd.concat([df, self.df], ignore_index=True)
            # df_concat = df_concat.drop_duplicates()
            # df_concat.to_json(file_base_path, orient='records', date_format='iso')
            
            df_concat = df_concat.drop_duplicates(subset=df_concat.columns.difference([coluna_chaves]))
            try:
                df_concat[coluna_chaves] = df_concat[coluna_chaves].astype(str)
                with open(file_base_path, 'w', encoding='utf-8') as _file:
                    json.dump(df_concat.to_dict(orient='records'), _file, default=str)
            except:
                df_concat.to_json(file_base_path, orient='records', date_format='iso')
                
            print(P("Incrementação Concluida!", color='green'))
            return self
        except Exception as error:
            print(P("Erro ao fazer a incrementação", color='red'))
            print(P((type(error), str(error)), color='red'))
            
            if not self.maestro is None:
                self.maestro.alert(
                    task_id=self.maestro.get_execution().task_id,
                    title=str(error),
                    message=str(traceback.format_exc()),
                    alert_type=AlertType.ERROR
                )  
                          
            raise error
            
if __name__ == "__main__":
    pass 
    