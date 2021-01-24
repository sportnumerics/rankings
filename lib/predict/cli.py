from . import predict
from datetime import datetime

def add_parsers(parsers):
  predict_parser = parsers.add_parser('predict', help='calculate ratings and predictions')
  predict_parser.add_argument('--schedule-dir', required=True, help='Directory to read schedules from')
  predict_parser.add_argument('--out-dir', default='out', help='Output directory')
  predict_parser.set_defaults(func=predict.predict)
