from datetime import datetime
import numpy as np
import pandas as pd
from ingestor import start_ingestor
def parse_line(line):
    parts=line.split()
    date=pd.to_datetime(parts[3][1:],format='%d/%b/%Y:%H:%M:%S')
    return {
      'ip': parts[0],
      'date': date,
      'method': parts[5][1:],
      'path': parts[6],
      'status': int(parts[8]),
      'response_size': int(parts[9]),
      'ref': ''.join(parts[11:]).strip('"'),
    }

def preprocess(Lines):
    records=[parse_line(line) for line in Lines]
    return pd.DataFrame.from_records(records)
