from . import predict


def add_parsers(parsers):
  predict_parser = parsers.add_parser('predict',
                                      help='calculate ratings and predictions')
  predict_parser.add_argument('--year', help='Year to calculate ratings for')
  predict_parser.add_argument('--input-dir',
                              default='out',
                              help='Directory to read schedules from')
  predict_parser.add_argument('--out-dir',
                              default='out',
                              help='Output directory')
  predict_parser.set_defaults(func=predict.predict)
