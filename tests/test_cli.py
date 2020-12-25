import argparse
from pathlib import Path

import tslogs.cli as cli


class TestArgsParser:
    def test_args_parser(
        self, args_parser: argparse.ArgumentParser, tmp_path: Path
    ) -> None:
        # version & help
        args_parser.parse_args("--version")
        args_parser.parse_args("--help")

        p = args_parser.parse_args(
            "--json --interval 2 --smooth 10"
            f" --output {str(tmp_path / 'output.jpg')} --indent 4 path".split()
        )
        assert p.json is True
        assert p.interval == 2
        assert p.smooth == 10
        assert p.output is not None
        assert p.indent == 4
        assert len(p.paths) == 1

    def test_summary(self, log_root: Path) -> None:
        cli.main([f"{str(log_root)}"])

    def test_json(self, log_root: Path) -> None:
        cli.main([str(log_root), "-j"])

    def test_plot(self, log_root, tmp_path: Path) -> None:
        output = tmp_path / "output.png"
        # default plot
        cli.main([str(log_root), "--output", str(output), "-p"])
        # custom data plot
        cli.main(
            [
                str(log_root),
                "--output",
                str(output),
                "-p",
                "battery_mw",
                "cpu_temp",
                "gpu_mhz",
            ]
        )
