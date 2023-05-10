from . import render
from datetime import datetime

def add_parsers(parsers):
  render_parser = parsers.add_parser('render', help='render to html')
  render_parser.add_argument('--year', default=str(datetime.now().year), help='Year to render')
  render_parser.add_argument('--input-dir',
                             default='out',
                             help='Input directory')
  render_parser.add_argument('--out-dir',
                             default='out',
                             help='Output directory')
  render_parser.add_argument('--serve',
                             action='store_true',
                             help='Serve the rendered files via HTTP')
  render_parser.add_argument('--port',
                             default=8000,
                             help='Port to serve files on')
  render_parser.set_defaults(func=render.render)
