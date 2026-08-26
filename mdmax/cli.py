"""
MDMAX CLI - Command-line interface for document conversion
"""

import click
from pathlib import Path
from typing import Optional
import sys
import os

# Fix Windows encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from .converter import MdMax
from .economy import TokenEconomy, estimate_tokens


@click.group()
@click.version_option(version="3.0.0")
def cli():
    """MDMAX - Convert any document to optimized Markdown"""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output Markdown file (default: stdout)"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Show detailed progress"
)
def convert(input_file: str, output: Optional[str], verbose: bool):
    """Convert a document to Markdown"""
    try:
        converter = MdMax()

        if verbose:
            click.echo(f"📄 Converting: {input_file}", err=True)

        markdown = converter.convert(input_file, output)

        if not output:
            click.echo(markdown)
            if verbose:
                stats = converter.get_stats()
                click.echo(f"\n✅ Conversion complete!", err=True)
                if stats["total_conversions"] > 0:
                    last = stats["total_conversions"] - 1
                    click.echo(f"   Saved: {stats['total_savings_tokens']:,} tokens", err=True)

    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command(name="batch")
@click.argument("pattern", type=str)
@click.option(
    "-o", "--output-dir",
    type=click.Path(),
    help="Output directory for Markdown files"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Show detailed progress"
)
def batch_convert(pattern: str, output_dir: Optional[str], verbose: bool):
    """Batch convert multiple files (e.g., *.pdf)"""
    from glob import glob

    files = glob(pattern, recursive=True)

    if not files:
        click.echo(f"❌ No files matching: {pattern}", err=True)
        sys.exit(1)

    converter = MdMax()
    output_dir_path = Path(output_dir) if output_dir else None
    if output_dir_path:
        output_dir_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"📦 Processing {len(files)} files...", err=True)

    for i, file_path in enumerate(files, 1):
        try:
            if verbose:
                click.echo(f"  [{i}/{len(files)}] {file_path}", err=True)

            output_path = None
            if output_dir_path:
                output_path = output_dir_path / (Path(file_path).stem + ".md")

            converter.convert(file_path, output_path)

        except Exception as e:
            click.echo(f"  ⚠️  Failed: {file_path}: {e}", err=True)

    stats = converter.get_stats()
    click.echo(f"\n✅ Batch complete! Conversions: {stats['total_conversions']}", err=True)
    click.echo(f"💾 Total saved: {stats['total_savings_tokens']:,} tokens", err=True)


@cli.command()
@click.option(
    "--export",
    type=click.Choice(["json", "csv"]),
    help="Export stats in format"
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file (default: stdout)"
)
def stats(export: Optional[str], output: Optional[str]):
    """Show token economy statistics"""
    economy = TokenEconomy()

    # Load existing stats from log
    if economy.log_file.exists():
        import json
        with open(economy.log_file) as f:
            for line in f:
                record = json.loads(line)
                economy.sessions.append(record)

    stats_data = economy.get_stats()

    if export:
        result = economy.export(format=export, output_path=Path(output) if output else None)
        if output:
            click.echo(f"✅ Exported to: {output}", err=True)
        else:
            click.echo(result)
    else:
        dashboard = economy.get_dashboard()
        click.echo(dashboard)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def estimate(input_file: str):
    """Estimate tokens in a file"""
    try:
        tokens = estimate_tokens(input_file)
        file_path = Path(input_file)

        click.echo(f"📊 Token Estimate")
        click.echo(f"  File: {file_path.name}")
        click.echo(f"  Size: {file_path.stat().st_size:,} bytes")
        click.echo(f"  Estimated tokens: {tokens:,}")
        click.echo(f"  Markdown tokens (est.): {int(tokens * 0.6):,}")
        click.echo(f"  Savings (est.): {int(tokens * 0.4):,} tokens (~40%)")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="cache")
@click.option("--show", is_flag=True, help="Show cache statistics")
@click.option("--list", is_flag=True, help="List cached files")
@click.option("--clear", is_flag=True, help="Clear cache")
@click.option("--clear-old", type=int, help="Clear files older than N days")
def cache_cmd(show: bool, list: bool, clear: bool, clear_old: Optional[int]):
    """Manage conversion cache"""
    from .cache import CacheManager

    manager = CacheManager()

    if show:
        dashboard = manager.get_dashboard()
        click.echo(dashboard)

    elif list:
        cached = manager.list_cached(limit=20)
        if not cached:
            click.echo("Cache is empty")
            return

        click.echo(f"Cached files ({len(cached)} most recent):")
        click.echo("-" * 70)
        for item in cached:
            click.echo(
                f"  {item['filename']:30} | {item['format']:6} | {item['processed_at']}"
            )

    elif clear_old:
        manager.clear_cache(older_than_days=clear_old)
        click.echo(f"Cleared cache entries older than {clear_old} days", err=True)

    elif clear:
        manager.clear_cache()
        click.echo("Cache cleared", err=True)

    else:
        stats = manager.get_stats()
        click.echo(f"Cache: {stats['cached_files']} files, {stats['cache_size_bytes']:,} bytes")


@cli.command(name="config")
@click.option("--show", is_flag=True, help="Show configuration")
@click.option("--reset", is_flag=True, help="Reset to defaults")
def config(show: bool, reset: bool):
    """Configure MDMAX"""
    config_dir = Path.home() / ".mdmax"
    config_file = config_dir / "config.json"

    if show:
        if config_file.exists():
            import json
            with open(config_file) as f:
                cfg = json.load(f)
            click.echo(json.dumps(cfg, indent=2))
        else:
            click.echo("No configuration found. Using defaults.")

    elif reset:
        import json
        config_dir.mkdir(exist_ok=True)
        defaults = {
            "optimize_tokens": True,
            "remove_metadata": True,
            "compress_tables": True,
            "supported_formats": [
                ".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".xlsm",
                ".csv", ".tsv", ".txt", ".json", ".ods", ".rtf",
                ".jpg", ".jpeg", ".png", ".svg", ".epub"
            ]
        }
        config_file.write_text(json.dumps(defaults, indent=2))
        click.echo(f"✅ Config reset to defaults: {config_file}")


def main():
    """Entry point for CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Interrupted", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
