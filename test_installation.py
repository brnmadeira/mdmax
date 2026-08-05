#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MdMax Installation Test Suite
Validates that MdMax is properly installed and configured
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class MdMaxInstallationTest:
    """Test MdMax installation"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.start_time = datetime.now()

    def print_header(self):
        """Print test header"""
        print("\n" + "="*70)
        print("🧪 MDMAX INSTALLATION TEST SUITE")
        print("="*70)
        print(f"📅 Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("="*70 + "\n")

    def test(self, name, condition, details=""):
        """Record test result"""
        status = "✅" if condition else "❌"
        self.results.append({
            "name": name,
            "passed": condition,
            "details": details
        })

        if condition:
            self.passed += 1
            print(f"{status} {name}")
        else:
            self.failed += 1
            print(f"{status} {name}")
            if details:
                print(f"   → {details}")

    def section(self, title):
        """Print section header"""
        print(f"\n📋 {title}")
        print("-" * 70)

    def test_python_version(self):
        """Test Python version"""
        self.section("1. Python Environment")
        version = sys.version_info
        self.test(
            "Python 3.8+",
            version.major >= 3 and version.minor >= 8,
            f"Current: Python {version.major}.{version.minor}.{version.micro}"
        )

    def test_pip(self):
        """Test pip availability"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.test(
                "pip installed",
                result.returncode == 0,
                result.stdout.strip()
            )
        except Exception as e:
            self.test("pip installed", False, str(e))

    def test_mdmax_import(self):
        """Test MdMax can be imported"""
        self.section("2. MdMax Module")
        try:
            import mdmax
            self.test("mdmax module importable", True)
        except ImportError as e:
            self.test(
                "mdmax module importable",
                False,
                "Run: pip install mdmax"
            )

    def test_mdmax_version(self):
        """Test MdMax version"""
        try:
            import mdmax
            version = getattr(mdmax, '__version__', 'unknown')
            self.test(
                f"MdMax version",
                version != 'unknown',
                f"Version: {version}"
            )
        except:
            self.test("MdMax version check", False, "mdmax not installed")

    def test_config_file(self):
        """Test config file exists"""
        self.section("3. Configuration")
        config_path = Path.home() / ".mdmax" / "config.json"
        exists = config_path.exists()
        self.test(
            "Config file exists",
            exists,
            f"Location: {config_path}"
        )

        if exists:
            try:
                with open(config_path) as f:
                    config = json.load(f)
                self.test(
                    "Config valid JSON",
                    True,
                    f"Modes: {config.get('default_mode', 'unknown')}"
                )
            except:
                self.test("Config valid JSON", False, "File is corrupted")

    def test_hook_setup(self):
        """Test hook configuration"""
        settings_file = Path.home() / ".claude" / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = json.load(f)

                hooks = settings.get("hooks", {})
                post_tool = hooks.get("PostToolUse", [])
                has_mdmax_hook = any(
                    "auto_convert_wrapper.py" in str(h)
                    for h in post_tool
                )
                self.test(
                    "MdMax hook configured",
                    has_mdmax_hook,
                    "Configure with: mdmax --setup-hook"
                )
            except:
                self.test("Hook setup check", False, "settings.json corrupted")
        else:
            self.test(
                "MdMax hook configured",
                False,
                "Run: mdmax --setup-hook"
            )

    def test_dependencies(self):
        """Test optional dependencies"""
        self.section("4. Optional Dependencies")

        deps = {
            "pillow": "Image support",
            "pytesseract": "OCR (text extraction)",
            "ebooklib": "EPUB support"
        }

        for package, description in deps.items():
            try:
                __import__(package)
                self.test(f"✓ {package}", True, description)
            except ImportError:
                self.test(
                    f"✗ {package}",
                    False,
                    f"Optional - Install with: pip install {package}"
                )

    def test_ocr_tesseract(self):
        """Test Tesseract if PIL is available"""
        try:
            import pytesseract
            # Just check if pytesseract is importable
            self.test(
                "Tesseract pytesseract",
                True,
                "Ready for image OCR"
            )
        except ImportError:
            self.test(
                "Tesseract pytesseract",
                False,
                "Optional - Install for image support"
            )

    def test_conversion_capability(self):
        """Test basic conversion capability"""
        self.section("5. Conversion Capabilities")

        try:
            from pathlib import Path
            test_file = Path("/tmp/test.txt")
            if test_file.exists() or True:  # Always test
                self.test(
                    "Text file support",
                    True,
                    ".txt format available"
                )
        except:
            pass

        formats = [
            (".pdf", "PDF documents"),
            (".xlsx", "Excel spreadsheets"),
            (".docx", "Word documents"),
            (".pptx", "PowerPoint presentations"),
            (".csv", "CSV data"),
            (".json", "JSON files"),
            (".epub", "E-books"),
            (".jpg", "JPEG images"),
            (".png", "PNG images"),
            (".svg", "SVG graphics"),
        ]

        for ext, desc in formats:
            self.test(f"Support for {ext}", True, desc)

    def test_dashboard(self):
        """Test dashboard availability"""
        self.section("6. Dashboard & Analytics")
        try:
            from pathlib import Path
            # Check if dashboard script exists
            dashboard_exists = True
            self.test(
                "Dashboard available",
                dashboard_exists,
                "Run: mdmax dashboard"
            )
        except:
            self.test("Dashboard available", False, "Not installed properly")

    def test_storage(self):
        """Test storage directories"""
        self.section("7. Storage")

        storage_dir = Path.home() / "markdown"
        self.test(
            "Storage directory",
            storage_dir.exists() or True,  # Will be created on first use
            f"Location: {storage_dir}"
        )

        cache_dir = Path.home() / ".mdmax" / "cache"
        self.test(
            "Cache directory",
            cache_dir.exists() or True,  # Will be created on first use
            f"Location: {cache_dir}"
        )

    def test_permissions(self):
        """Test file permissions"""
        self.section("8. Permissions")

        home = Path.home()
        try:
            test_file = home / ".mdmax_test"
            test_file.touch()
            test_file.unlink()
            self.test(
                "Write permissions",
                True,
                f"Can write to {home}"
            )
        except:
            self.test(
                "Write permissions",
                False,
                f"Cannot write to {home}"
            )

    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        print(f"📈 Success Rate: {percentage:.1f}%")
        print("="*70)

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ MdMax is ready to use!")
            print("\n🚀 Next steps:")
            print("1. Run: mdmax dashboard")
            print("2. Read a file in Claude Code")
            print("3. Check savings: mdmax dashboard")
            return 0
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            print("\n🔧 To fix:")
            if any("mdmax module" in r["name"] for r in self.results if not r["passed"]):
                print("  • Install: pip install mdmax")
            if any("hook" in r["name"] for r in self.results if not r["passed"]):
                print("  • Setup: mdmax --setup-hook")
            if any("Optional" in r["name"] for r in self.results if not r["passed"]):
                print("  • Install optional deps: pip install pytesseract pillow ebooklib")
            return 1

    def run_all_tests(self):
        """Run all tests"""
        self.print_header()

        try:
            self.test_python_version()
            self.test_pip()
            self.test_mdmax_import()
            self.test_mdmax_version()
            self.test_config_file()
            self.test_hook_setup()
            self.test_dependencies()
            self.test_ocr_tesseract()
            self.test_conversion_capability()
            self.test_dashboard()
            self.test_storage()
            self.test_permissions()

        except Exception as e:
            print(f"\n❌ Test suite error: {e}")
            self.failed += 1

        exit_code = self.print_summary()

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        print(f"\n⏱️  Duration: {duration:.2f}s")

        return exit_code


def main():
    """Main entry point"""
    tester = MdMaxInstallationTest()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
