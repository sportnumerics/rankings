from . import render

def add_parsers(parsers):
  render_parser = parsers.add_parser('render', help='render to html')
  render_parser.add_argument('--year', help='Year to render')
  render_parser.add_argument('--input-dir', default='out', help='Input directory')
  render_parser.add_argument('--out-dir', default='out', help='Output directory')
  render_parser.set_defaults(func=render.render)
