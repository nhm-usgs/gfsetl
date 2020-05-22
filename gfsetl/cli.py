"""Console script for gfsetl."""
from gfsetl.gfs_etl import GFSEtl
import sys
import click
import datetime


def valid_date(ctx, param, value):
    try:
        for date in value:
            return datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(value)
        raise click.BadParameter(msg)


@click.command()
@click.option('-p', '--period',
    help='option: start date and end date of retrieval (YYYY-MM-DD)',
    default=None,
    required=True,
    nargs=2,
    type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('-f', '--file_prefix',
    help='option: prefix for output files',
    default='',
    type=str,
    required=False)
@click.option('-i', '--inpath',
    help='input_path (location of HRU shapefiles and pulled .grib2 files)',
    default=None,
    required=True,
    type=click.Path(exists=True))
@click.option('-o', '--outpath',
    help='Output path (location of netCDF .cbh output files)',
    default=None,
    required=True,
    type=click.Path(exists=True))
@click.option('-w', '--weightsfile',
    help='path/weight.csv - path/name of weight file)',
    default=None,
    required=True,
    type=click.Path(exists=True))
@click.option('-g','--gpkg_file',
    help='path/hru.gpkg = path/name of HRU .gpkg file',
    default=None,
    required=True,
    type=click.Path(exists=True))
def main(period, file_prefix, inpath, outpath, weightsfile, gpkg_file, args=None):
    """Console script for gfsetl."""
    click.echo(f"period: {period}, {type(period[0])}, {period[0].date()}")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    etl = GFSEtl(period, prefix=file_prefix, inpath=inpath, outpath=outpath, weightsfile=weightsfile,
        gpkg=gpkg_file)
    
    etl.initialize()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
