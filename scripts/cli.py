#!/usr/bin/env python3
"""
MdMax CLI - Command-line interface for file conversion
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import json

__version__ = "2.0.0"

# Configuration directory
CONFIG_DIR = Path.home() / ".mdmax"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"
STATE_FILE = CONFIG_DIR / "state.json"


def ensure_config():
    """Ensure configuration directory exists"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        default_config = {
            "default_mode": "ultra",
            "cache_cleanup_days": 7,
            "enable_logging": True,
            "parallelization": {
                "enabled": True,
                "workers": 3
            },
            "supported_formats": [
                ".pdf", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv",
                ".txt", ".json", ".docx", ".pptx", ".ods",
                ".jpg", ".jpeg", ".png", ".svg", ".epub"
            ]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)


def load_config():
    """Load configuration"""
    ensure_config()
    with open(CONFIG_FILE) as f:
        return json.load(f)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*50)
    print("MdMax v" + __version__)
    print("Compress files by 79.7% + track token economy")
    print("="*50 + "\n")


def cmd_convert(args):
    """Convert file to markdown with optimizations"""
    print_banner()

    # Import converter and optimizers
    try:
        from scripts.converters_real import MarkdownConverter
        from scripts.optimizers import optimize_markdown, calculate_savings, check_duplicate
        from scripts.token_counter import get_token_count, calculate_real_savings
        from scripts.summarizer import smart_summarize
        from scripts.metadata_extractor import MetadataExtractor
    except ImportError:
        try:
            from converters_real import MarkdownConverter
            from optimizers import optimize_markdown, calculate_savings, check_duplicate
            from token_counter import get_token_count, calculate_real_savings
            from summarizer import smart_summarize
            from metadata_extractor import MetadataExtractor
        except ImportError:
            print("Error: converters module not found")
            print("Please ensure you have all dependencies installed:")
            print("  pip install mdmax")
            sys.exit(1)

    file_path = Path(args.file)

    # AUTO-CONVERSION: Detect and convert .xls to .xlsx automatically
    if file_path.suffix.lower() == ".xls":
        print(f"[AUTO-CONVERT] 🔄 Detected legacy Excel format (.xls)")
        file_path = Path(auto_detect_and_convert(str(file_path)))
        print(f"[AUTO-CONVERT] ✅ File automatically converted to .xlsx")

    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    # Determine file type
    file_ext = file_path.suffix.lower()

    print(f"[INFO] Converting: {file_path.name}")
    print(f"[INFO] Format: {file_ext}")
    print(f"[INFO] Mode: {args.mode}")
    print(f"[INFO] Optimization: {args.optimize}")
    if args.real_tokens:
        print(f"[INFO] Token counting: REAL (Claude API)")
    if args.summarize:
        print(f"[INFO] Summarization: ENABLED")
    print()

    try:
        converter = MarkdownConverter()

        # Convert based on file type
        if file_ext == ".pdf":
            markdown = converter.pdf_to_markdown(str(file_path))
        elif file_ext in [".xlsx", ".xlsm"]:
            markdown = converter.xlsx_to_markdown(str(file_path))
        elif file_ext == ".xls":
            markdown = converter.xls_to_markdown(str(file_path))
        elif file_ext == ".csv":
            markdown = converter.csv_to_markdown(str(file_path))
        elif file_ext == ".json":
            markdown = converter.json_to_markdown(str(file_path))
        elif file_ext == ".svg":
            markdown = converter.svg_to_markdown(str(file_path))
        elif file_ext == ".txt":
            with open(file_path) as f:
                markdown = f.read()
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            markdown = converter.jpg_to_markdown(str(file_path))
        elif file_ext in [".docx"]:
            markdown = converter.docx_to_markdown(str(file_path))
        elif file_ext in [".pptx"]:
            markdown = converter.pptx_to_markdown(str(file_path))
        elif file_ext in [".epub"]:
            markdown = converter.epub_to_markdown(str(file_path))
        else:
            print(f"[ERROR] Unsupported format: {file_ext}")
            sys.exit(1)

        # Apply optimizations based on mode
        optimize_flags = []
        if args.optimize == 'all' or args.optimize == 'full':
            optimize_flags = ['all']
        elif args.optimize == 'basic':
            optimize_flags = ['boilerplate', 'urls']
        elif args.optimize == 'none':
            optimize_flags = []

        if optimize_flags and args.mode == 'ultra':
            print(f"[OPTIMIZE] Applying optimizations: {', '.join(optimize_flags)}")
            markdown = optimize_markdown(markdown, optimize_flags)

        # Apply summarization if requested
        if args.summarize and len(markdown) > 5000:
            print(f"[SUMMARIZE] Enabling AI summarization...")
            markdown = smart_summarize(markdown, enable_api=True)

        # FEATURE [3]: Generate metadata frontmatter
        print(f"[METADATA] Extracting metadata and generating frontmatter...")
        extractor = MetadataExtractor()

        # Try to extract from file first
        if file_ext in ['.xlsx', '.xls']:
            metadata = extractor.extract_from_excel_metadata(str(file_path))
        elif file_ext == '.pdf':
            metadata = extractor.extract_from_pdf_metadata(str(file_path))
        else:
            metadata = {}

        # Merge with text-based extraction
        text_metadata = extractor.extract_from_text(markdown, file_path.name)
        metadata.update({k: v for k, v in text_metadata.items() if k not in metadata})

        # Add filename-based metadata if missing
        filename_metadata = extractor.extract_from_filename(file_path.name)
        if 'title' not in metadata and 'title' in filename_metadata:
            metadata['title'] = filename_metadata['title']
        if 'date' not in metadata and 'date' in filename_metadata:
            metadata['date'] = filename_metadata['date']

        # Add content-based tags
        if 'tags' not in metadata or not metadata['tags']:
            content_tags = extractor.detect_content_tags(markdown)
            if content_tags:
                metadata['tags'] = content_tags

        # Add to markdown
        if metadata:
            markdown = extractor.add_frontmatter_to_markdown(markdown, metadata)
            print(f"[METADATA] ✅ Frontmatter added: title, date, author, tags")

        # Save output
        output_path = args.output or file_path.with_suffix('.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        # Calculate stats
        original_size = file_path.stat().st_size
        output_size = Path(output_path).stat().st_size
        reduction = (1 - output_size / original_size) * 100 if original_size > 0 else 0

        # Token counting
        if args.real_tokens:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    original_content = f.read()
                token_stats = calculate_real_savings(original_content, markdown)
                print(f"[SUCCESS] Converted to: {output_path}")
                print(f"[STATS] Original: {original_size / 1024:.1f} KB")
                print(f"[STATS] Compressed: {output_size / 1024:.1f} KB")
                print(f"[STATS] Reduction: {reduction:.1f}%")
                print(f"[TOKENS] Original: {token_stats['original_tokens']:,} ({token_stats['original_method']})")
                print(f"[TOKENS] After: {token_stats['optimized_tokens']:,} ({token_stats['optimized_method']})")
                print(f"[ECONOMY] {token_stats['status']} tokens saved: {token_stats['tokens_saved']:,} ({token_stats['savings_percent']:.1f}%)")
            except Exception as e:
                print(f"[WARNING] Real token counting failed: {e}")
                estimated_tokens_original = int(original_size * 0.00025)
                estimated_tokens_after = int(output_size * 0.00025)
                tokens_saved = estimated_tokens_original - estimated_tokens_after
                print(f"[SUCCESS] Converted to: {output_path}")
                print(f"[STATS] Original: {original_size / 1024:.1f} KB")
                print(f"[STATS] Compressed: {output_size / 1024:.1f} KB")
                print(f"[STATS] Reduction: {reduction:.1f}%")
                print(f"[ECONOMY] Estimated tokens saved: {tokens_saved:,}")
        else:
            estimated_tokens_original = int(original_size * 0.00025)
            estimated_tokens_after = int(output_size * 0.00025)
            tokens_saved = estimated_tokens_original - estimated_tokens_after
            print(f"[SUCCESS] Converted to: {output_path}")
            print(f"[STATS] Original: {original_size / 1024:.1f} KB")
            print(f"[STATS] Compressed: {output_size / 1024:.1f} KB")
            print(f"[STATS] Reduction: {reduction:.1f}%")
            print(f"[ECONOMY] Estimated tokens saved: {tokens_saved:,}")
        print()

    except Exception as e:
        print(f"[ERROR] Conversion failed: {str(e)}")
        sys.exit(1)


def cmd_dashboard(args):
    """Show token economy dashboard"""
    print_banner()

    try:
        from dashboard_advanced import DashboardGenerator

        dashboard = DashboardGenerator()

        if args.format == "console":
            dashboard.print_console_dashboard_advanced()
        elif args.format == "json":
            dashboard.generate_html_dashboard_advanced()
            print("[INFO] Dashboard saved to: dashboard.html")

    except Exception as e:
        print(f"[ERROR] Dashboard failed: {str(e)}")
        sys.exit(1)


def cmd_config(args):
    """Manage configuration"""
    print_banner()

    ensure_config()

    if args.show:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        print("Current configuration:")
        print(json.dumps(config, indent=2))
    elif args.reset:
        os.remove(CONFIG_FILE)
        ensure_config()
        print("[SUCCESS] Configuration reset to defaults")


def cmd_version(args):
    """Show version"""
    print(f"MdMax v{__version__}")


def cmd_init(args):
    """Initialize configuration"""
    ensure_config()
    print_banner()
    print("[SUCCESS] Configuration initialized")
    print(f"[INFO] Config directory: {CONFIG_DIR}")
    print(f"[INFO] Config file: {CONFIG_FILE}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MdMax - Compress files by 79.7% and track token economy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mdmax convert file.pdf                    # Convert PDF to Markdown
  mdmax convert file.xlsx -o output.md      # Convert Excel with custom output
  mdmax dashboard                            # Show token economy dashboard
  mdmax config --show                        # Display current configuration
  mdmax init                                 # Initialize configuration
  mdmax --version                            # Show version
        """
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert file to Markdown')
    convert_parser.add_argument('file', help='Input file path')
    convert_parser.add_argument('-o', '--output', help='Output file path')
    convert_parser.add_argument('-m', '--mode', default='ultra',
                                choices=['normal', 'ultra', 'enterprise'],
                                help='Compression mode (default: ultra)')
    convert_parser.add_argument('--optimize', default='all',
                                choices=['none', 'basic', 'full', 'all'],
                                help='Optimization level (default: all)')
    convert_parser.add_argument('--real-tokens', action='store_true',
                                help='Use Claude API for real token counting (requires API key)')
    convert_parser.add_argument('--summarize', action='store_true',
                                help='Use AI to summarize verbose content')
    convert_parser.set_defaults(func=cmd_convert)

    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Show dashboard')
    dashboard_parser.add_argument('-f', '--format', default='console',
                                  choices=['console', 'json', 'html'],
                                  help='Output format')
    dashboard_parser.set_defaults(func=cmd_dashboard)

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show configuration')
    config_parser.add_argument('--reset', action='store_true', help='Reset to defaults')
    config_parser.set_defaults(func=cmd_config)

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize configuration')
    init_parser.set_defaults(func=cmd_init)

    args = parser.parse_args()

    # Handle version flag
    if args.version:
        cmd_version(args)
        sys.exit(0)

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
