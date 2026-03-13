from . import export_parquet


def add_parsers(parsers):
    export_parser = parsers.add_parser(
        'export-parquet',
        help='Export optimized parquet files for frontend queries')
    export_parser.add_argument('--input-dir',
                              default='out',
                              help='Directory to read data from')
    export_parser.add_argument('--out-dir',
                              default='out',
                              help='Output directory')
    export_parser.add_argument('--year',
                              help='Year to export (defaults to all years)')
    export_parser.set_defaults(func=export_parquet.export_parquet_views)
