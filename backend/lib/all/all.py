from dataclasses import dataclass
from datetime import datetime

from ..scrape import scrape
from ..predict import predict
from ..render import render

def run(args):
  for source in args.source:
    scrape.scrape_schedules(ScrapeArgs(source=source, year=args.year, out_dir=args.out_dir))

  predict.predict(PredictArgs(input_dir=args.out_dir, year=args.year, out_dir=args.out_dir))
  render.render(RenderArgs(input_dir=args.out_dir, year=args.year, out_dir=args.out_dir))

@dataclass
class ScrapeArgs:
  source: str
  year: str
  out_dir: str

@dataclass
class PredictArgs:
  input_dir: str
  year: str
  out_dir: str

@dataclass
class RenderArgs:
  input_dir: str
  year: str
  out_dir: str
