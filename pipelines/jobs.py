from typing import Union
from babydragon.models.generators.PolarsGenerator import PolarsGenerator
import polars as pl
from time import time as now
import os


class EmbeddingsPipeline:

    def __init__(
        self,
        raw_thread: Union[pl.DataFrame,None] = None,
        restore: Union[str,None] = None,
        user_id: str = "6e1abc64-09f6-4950-9cea-fd425006e1b3",
        job_type: str = "embeddings",
        input_col: str = "content",
        open_api_api_key : str = "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"

    ) -> None:

        os.environ["OPENAI_API_KEY"] = open_api_api_key 
        
        if restore is not None:

            self.name = restore
            self.load_path = f'users/{user_id}/jobs/{job_type}/'
            self.input_df = pl.read_ndjson(self.load_path+self.name+'.ndjson')
            self.generator = PolarsGenerator( input_df = self.input_df,
                                              name = self.name,
                                              save_path=self.load_path
                                             )

        elif raw_thread is not None:

            self.timestamp = int(str(now()).split('.')[0])
            self.input_df = self.prepare_input_df_for_embeddings(raw_thread, input_col)
            self.generator = PolarsGenerator( input_df = self.input_df,
                                              name = f'{self.timestamp}_{input_col}',
                                              save_path=f'users/{user_id}/jobs/{job_type}'
                                            )


    def start(self):
        if self.generator is not None:
            self.generator.execute()
            return(pl.read_ndjson(self.generator.save_path))


    def prepare_input_df_for_embeddings(self, df: pl.DataFrame, input_col: str):
        df = df.select(input_col).with_columns(pl.lit("text-embedding-ada-002").alias("model"))
        input_df = df.with_columns(df[input_col].alias('input')).drop(input_col)
        return(input_df)


