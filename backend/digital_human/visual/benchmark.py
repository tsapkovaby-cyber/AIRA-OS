from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkScenario:
    scenario_id: str
    description: str


AIRA_VISUAL_IDENTITY_V1 = (
    BenchmarkScenario("01_REFERENCE_REPRODUCTION", "controlled master-reference reproduction"),
    BenchmarkScenario("02_SOFT_SMILE", "front portrait with soft smile"),
    BenchmarkScenario("03_30_DEGREE_LEFT", "30 degree left angle"),
    BenchmarkScenario("04_30_DEGREE_RIGHT", "30 degree right angle"),
    BenchmarkScenario("05_WHITE_SHIRT_WORKSPACE", "signature white-shirt workspace"),
    BenchmarkScenario("06_NATURAL_DAYLIGHT", "natural daylight"),
    BenchmarkScenario("07_PURPLE_ACCENT_LIGHT", "controlled soft violet accent"),
    BenchmarkScenario("08_OUTDOOR_LIFESTYLE", "realistic outdoor lifestyle"),
)
