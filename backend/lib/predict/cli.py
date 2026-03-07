import json
from pathlib import Path

from scripts import backtest_baseline
from ..shared import shared
from . import predict


def run_backtest(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    for year in shared.years(args.year):
        report = backtest_baseline.generate_report(Path(args.data_dir), year)
        reports.append(report)
        (out_dir / f"{year}.json").write_text(json.dumps(report, indent=2) + "\\n")

    summary = backtest_baseline.render_team_summary_markdown(reports)
    (out_dir / 'summary.md').write_text(summary)
    print(summary)


def add_parsers(parsers):
    predict_parser = parsers.add_parser(
        'predict', help='calculate ratings and predictions')
    predict_parser.add_argument('--input-dir',
                                default='out',
                                help='Directory to read schedules from')
    predict_parser.add_argument('--out-dir',
                                default='out',
                                help='Output directory')
    predict_parser.set_defaults(func=predict.predict)

    backtest_parser = parsers.add_parser(
        'backtest', help='run predictive backtest baseline')
    backtest_parser.add_argument('--data-dir',
                                 required=True,
                                 help='Root dir containing <year>/games(.json) data')
    backtest_parser.add_argument('--out-dir',
                                 default='out/backtest',
                                 help='Directory to write per-year JSON reports and summary.md')
    backtest_parser.set_defaults(func=run_backtest)
