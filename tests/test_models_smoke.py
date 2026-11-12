from kerbal_copilot.models import BuildReport, PartRef


def test_part_ref_defaults() -> None:
    part = PartRef(name="mk1pod")
    assert part.qty == 1
    assert part.placement == "stack"


def test_build_report_defaults() -> None:
    report = BuildReport(stages=[], total_dv_vac=0, launch_twr=1.0)
    assert report.warnings == []
