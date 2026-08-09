"""
CountryConfig.py — Country-parameterised configuration loader
=============================================================

Single source of truth for country-specific parameters (EUBUCCO partitions,
TABULA proxy, climate multiplier, retrofit blend, DHW, benchmarks, NUTS3
list, bounding box).

Each country has a YAML file at code/data/country_config/{cc}.yaml where
{cc} is the lowercase 2-letter ISO country code (e.g. `lu`, `fr`, `de`).

USAGE
-----
    from CountryConfig import load_country_config
    cfg = load_country_config("LU")
    print(cfg.country_name)                  # "Luxembourg"
    print(cfg.eubucco_url("LU00"))           # full S3 URL
    print(cfg.climate_multiplier)            # 1.112
    print(cfg.retrofit_blend_value)          # 0.813

Why a class wrapper around YAML
-------------------------------
* Type-safe access (cfg.climate_multiplier vs cfg["climate"]["climate_multiplier"])
* Validation at load time (catches typos in YAML before pipeline runs)
* Convenience methods for computed values (eubucco URLs, country folder paths)
* Single place to evolve the schema as new countries surface new
  requirements (UK with imperial floor heights, NL with no construction-
  year column, etc.)

Schema versioning
-----------------
The YAML carries a `_meta.schema_version` integer. Scripts can refuse to
run against an older schema (raise on mismatch) so a partially-migrated
config doesn't produce silently-wrong outputs.
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

try:
    import yaml
except ImportError as e:
    raise ImportError(
        "PyYAML is required to load country configs. "
        "Install with: pip install pyyaml"
    ) from e


SCHEMA_VERSION = 1


@dataclass
class CountryConfig:
    """Loaded country configuration."""

    # Identity
    country_code: str
    country_name: str

    # EUBUCCO
    eubucco_version: str
    nuts2_partitions: list[str]
    eubucco_base_url: str
    eubucco_license: str

    # Geography
    nuts3_regions: list[str]
    bbox_wgs84: dict[str, float]

    # TABULA
    tabula_source_country: str
    tabula_source_country_name: str
    tabula_intensities_file: str
    tabula_reason_for_proxy: str

    # Climate
    hdd_country: float
    hdd_proxy: float
    # The HDD against which the TABULA file's intensities are actually
    # calibrated. For most TABULA national typologies this equals
    # hdd_proxy (the proxy country's national mean), so the field defaults
    # to hdd_proxy when absent. But several TABULA brochures publish a
    # SINGLE reference zone rather than a national mean (IT Middle zone
    # ~2500 HDD; EL Zone B Athens/Patra ~1100 HDD; DE DIN V 18599 reference
    # climate ~3300 HDD; SE zone 3 ~3500 HDD). For those countries the
    # YAML sets climate.tabula_reference_hdd explicitly so the climate
    # multiplier is computed against the right reference, not the (often
    # very different) proxy-country national mean.
    tabula_reference_hdd: float
    climate_multiplier: float
    hdd_source: str

    # Retrofit
    retrofit_share_original: float
    retrofit_share_standard: float
    retrofit_share_advanced: float
    retrofit_factor_standard: float
    retrofit_factor_advanced: float
    retrofit_blend_value: float

    # DHW
    dhw_sfh: float
    dhw_mfh: float
    dhw_source: str

    # Non-residential
    non_residential_intensity: float
    non_residential_source: str

    # Benchmarks (dict-shaped, kept flexible)
    reconciliation_benchmarks: dict[str, Any]

    # Hotmaps comparison ID
    hotmaps_nuts3_id: str

    # Classification universals
    floor_height_residential_m: float
    floor_height_other_m: float
    useable_area_fraction: float

    # Raw YAML for fallback
    raw: dict[str, Any] = field(repr=False)

    # Floor-count source for 02_classify.py:
    #   'eubucco'  — use EUBUCCO's native `floors` column (roof-aware;
    #                falls back to the height estimate where it is missing)
    #   'estimate' — round(height / floor_height)  [legacy default]
    # Optional in the YAML; defaults to 'estimate' so existing configs are
    # unaffected. NOTE: for a valid cross-country comparison every country
    # must use the SAME value.
    floor_source: str = "estimate"

    # Operational-regime (comfort) deflator. Optional, defaults to None
    # (no deflation applied). When set, the per-building useful-heat
    # intensity computed in 03_heat_intensity.py is multiplied by this
    # scalar to translate TABULA "reference-condition" steady-state
    # demand into actually-realised stock-weighted demand.
    #
    # This is NOT a calibration knob fit to Hotmaps. It is a documented
    # academic adjustment grounded in primary measured-vs-calculated
    # studies for Mediterranean countries whose residential heating
    # culture (low operative T, partial-room heating, intermittent use)
    # diverges structurally from the TABULA 20 deg C / 18 h / whole-house
    # reference regime. Every country setting this field must cite the
    # underlying published deflator in comfort_regime.source.
    #
    # Currently set for ES, EL, CY, PT (Group 3, INV cluster). Unset
    # for cold/temperate countries where TABULA reference closely
    # matches actual operation.
    comfort_regime_deflator: float | None = None
    comfort_regime_source: str = ""

    # Per-building-class TABULA file override. Optional, defaults to None
    # (single-file behaviour preserved). When set, each entry maps a building
    # class (SFH / MFH_LOW / MFH_HIGH) to a TABULA file + a per-class climate
    # multiplier + a source country tag. This lets a country pull SFH values
    # from one TABULA brochure and MFH values from another, when the
    # residential stock is structurally bifurcated (the Baltic case: cold-
    # climate wooden SFH + Soviet-era panel-block MFH come from different
    # construction lineages and the single-proxy TABULA approach over-states
    # one or both classes).
    #
    # Each value dict has the shape:
    #   { file: str, climate_multiplier: float, source_country: str }
    #
    # Entries for classes not in the dict fall back to the primary
    # tabula.intensities_file and cfg.climate_multiplier (backward compatible).
    #
    # Currently used by EE and LT (SFH from SE, MFH from PL). When set, the
    # validator's strict climate_multiplier == hdd_country/tabula_reference_hdd
    # cross-check is skipped (since the multiplier becomes per-class).
    tabula_class_mix: dict[str, dict] | None = None

    # EUBUCCO area-correction factor. Optional, defaults to None (no
    # correction). When set, the per-building heated_floor_area_m2 is
    # multiplied by this scalar before the heat-demand calculation. This
    # propagates to both the total area and total heat demand in the
    # reconciliation table; per-m^2 intensity reporting stays unchanged.
    #
    # This is NOT a calibration knob fit to Hotmaps. It is a documented
    # academic correction grounded in national census data that gives an
    # authoritative ground truth on residential floor-area totals. EUBUCCO
    # v0.2 over-counts residential floor area in some countries because
    # the classification rule (floors >= 3 -> MFH_LOW) captures terraced
    # rural housing and mixed-use ground-floor commercial that should be
    # excluded. The size of the over-count is country-specific.
    #
    # Every country setting this field must cite the underlying national
    # census in eubucco_area_correction_source. Currently set for ES
    # (INE Censos 2021) and CY (CYSTAT 2021). Unset for all other countries
    # pending a per-country area-comparison sweep.
    eubucco_area_correction: float | None = None
    eubucco_area_correction_source: str = ""

    # Climate-based TABULA region split. Optional, defaults to None (single
    # national TABULA proxy/source preserved). When set, different NUTS3
    # regions of the SAME country draw their intensities from different TABULA
    # files, because the country's residential stock spans more than one
    # climate zone whose construction tradition and heating intensity differ
    # structurally. This is the spatial analogue of tabula_class_mix (which
    # splits by building class); region_split splits by geography.
    #
    # Shape:
    #   { default_region: str,
    #     regions: { <region_name>: { file: str, climate_multiplier: float,
    #                                 source_country: str, nuts3: [<codes>] } } }
    # Every NUTS3 code not listed under any region falls back to default_region.
    #
    # Currently used by HR (Croatia): the Adriatic coast (Köppen Csa, NUTS2
    # HR03 Jadranska Hrvatska) draws on the Italian Mediterranean TABULA, the
    # continental interior (Cfb/Dfb) on the Slovenian TABULA. Croatia has no
    # national TABULA/EPISCOPE typology, so a climate-matched neighbour split
    # is the defensible proxy. Each region entry must cite its basis in
    # tabula.region_split_source.
    tabula_region_split: dict | None = None
    tabula_region_split_source: str = ""

    # ── Convenience: paths ──────────────────────────────────────────────────

    @property
    def cc_lower(self) -> str:
        """Lowercase 2-letter country code (e.g. 'lu')."""
        return self.country_code.lower()

    def eubucco_url(self, nuts2: str) -> str:
        """Full HTTPS URL to the EUBUCCO parquet for a given NUTS2 partition."""
        return f"{self.eubucco_base_url}/nuts_id={nuts2}/{nuts2}.parquet"

    def eubucco_filename(self, nuts2: str) -> str:
        """Filename only (e.g. 'LU00.parquet')."""
        return f"{nuts2}.parquet"

    # ── Validation ──────────────────────────────────────────────────────────

    def validate(self) -> None:
        """Run sanity checks. Raises ValueError on inconsistency."""
        errs = []

        # Retrofit shares must sum to 1.0 ± 0.001
        share_sum = (self.retrofit_share_original
                     + self.retrofit_share_standard
                     + self.retrofit_share_advanced)
        if abs(share_sum - 1.0) > 0.001:
            errs.append(f"Retrofit shares sum to {share_sum:.4f}, expected 1.0")

        # Climate multiplier should match the HDD ratio against the
        # TABULA reference HDD (the HDD against which the source TABULA
        # intensities were actually calibrated). Defaults to hdd_proxy
        # for backward compatibility when the YAML doesn't set the field.
        # SKIPPED when tabula_class_mix is set, because in class-mix mode
        # the climate multiplier is per-class (each class_mix entry carries
        # its own climate_multiplier validated below).
        if self.tabula_class_mix is None:
            expected = self.hdd_country / self.tabula_reference_hdd
            if abs(expected - self.climate_multiplier) > 0.002:
                errs.append(
                    f"climate.climate_multiplier ({self.climate_multiplier}) does not "
                    f"match HDD ratio ({self.hdd_country}/{self.tabula_reference_hdd} "
                    f"= {expected:.4f})"
                )
        else:
            # Class-mix validation: every entry must have file, climate_multiplier
            # and source_country; the class key must be a recognised residential
            # class.
            valid_classes = {"SFH", "MFH_LOW", "MFH_HIGH"}
            for cls, entry in self.tabula_class_mix.items():
                if cls not in valid_classes:
                    errs.append(
                        f"tabula.class_mix has unknown class {cls!r}; allowed: "
                        f"{sorted(valid_classes)}")
                    continue
                if not isinstance(entry, dict):
                    errs.append(
                        f"tabula.class_mix[{cls!r}] must be a dict, got "
                        f"{type(entry).__name__}")
                    continue
                for required in ("file", "climate_multiplier", "source_country"):
                    if required not in entry:
                        errs.append(
                            f"tabula.class_mix[{cls!r}] missing required key "
                            f"{required!r}")

        # Recompute retrofit blend
        expected_blend = (self.retrofit_share_original
                          + self.retrofit_share_standard
                          * self.retrofit_factor_standard
                          + self.retrofit_share_advanced
                          * self.retrofit_factor_advanced)
        if abs(expected_blend - self.retrofit_blend_value) > 0.002:
            errs.append(
                f"retrofit.blend_value ({self.retrofit_blend_value}) does not "
                f"match formula result ({expected_blend:.4f})"
            )

        # Country code must be 2 chars uppercase
        if len(self.country_code) != 2 or not self.country_code.isupper():
            errs.append(
                f"country_code {self.country_code!r} must be 2 upper-case letters"
            )

        # Floor source must be one of the two recognised values
        if self.floor_source not in ("eubucco", "estimate"):
            errs.append(
                f"classification.floor_source {self.floor_source!r} must be "
                f"'eubucco' or 'estimate'"
            )

        # When comfort_regime_deflator is set, require it in (0,1] and a
        # non-empty source citation (this is a methodology-shifting field;
        # it MUST be traceable to a published study).
        if self.comfort_regime_deflator is not None:
            if not (0.0 < self.comfort_regime_deflator <= 1.0):
                errs.append(
                    f"comfort_regime.deflator ({self.comfort_regime_deflator}) "
                    f"must be in (0, 1]"
                )
            if not self.comfort_regime_source.strip():
                errs.append(
                    "comfort_regime.deflator is set but comfort_regime.source "
                    "is empty; deflator must cite a published study"
                )

        # Same constraints on the EUBUCCO area correction.
        if self.eubucco_area_correction is not None:
            if not (0.0 < self.eubucco_area_correction <= 1.0):
                errs.append(
                    f"eubucco.area_correction ({self.eubucco_area_correction}) "
                    f"must be in (0, 1]"
                )
            if not self.eubucco_area_correction_source.strip():
                errs.append(
                    "eubucco.area_correction is set but area_correction_source "
                    "is empty; correction must cite a national-census anchor"
                )

        # Region-split: when set, require a default_region, a non-empty regions
        # map with file/climate_multiplier/source_country/nuts3 per region, and a
        # source citation. Skipped entirely when None (all other countries).
        if self.tabula_region_split is not None:
            rs = self.tabula_region_split
            if "regions" not in rs or not isinstance(rs.get("regions"), dict):
                errs.append("tabula.region_split must have a 'regions' dict")
            else:
                if rs.get("default_region") not in rs["regions"]:
                    errs.append(
                        f"tabula.region_split.default_region "
                        f"({rs.get('default_region')!r}) must be one of "
                        f"{sorted(rs['regions'])}")
                for rname, entry in rs["regions"].items():
                    for required in ("file", "climate_multiplier",
                                     "source_country", "nuts3"):
                        if required not in entry:
                            errs.append(
                                f"tabula.region_split.regions[{rname!r}] missing "
                                f"{required!r}")
            if not self.tabula_region_split_source.strip():
                errs.append(
                    "tabula.region_split is set but region_split_source is "
                    "empty; the split must cite its climate/typology basis")

        if errs:
            raise ValueError(
                f"Country config validation failed for {self.country_code}:\n  - "
                + "\n  - ".join(errs)
            )


def load_country_config(country_code: str,
                        repo_root: Path | None = None) -> CountryConfig:
    """Load and validate a country config.

    Parameters
    ----------
    country_code
        Two-letter ISO country code, case-insensitive (LU, lu, Lu all work).
    repo_root
        Optional repo root path. Defaults to autodetect (this file's parents[2]).

    Returns
    -------
    CountryConfig
        Validated, ready to use.

    Raises
    ------
    FileNotFoundError
        If `code/data/country_config/{cc}.yaml` does not exist.
    ValueError
        If the config fails validation (e.g. retrofit shares don't sum to 1).
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    cc = country_code.upper()
    yaml_path = (repo_root / "code" / "data" / "country_config"
                 / f"{cc.lower()}.yaml")
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"Country config not found at {yaml_path}. "
            f"Available countries: "
            + ", ".join(
                p.stem.upper()
                for p in yaml_path.parent.glob("*.yaml")
            )
            if yaml_path.parent.exists() else "(none)"
        )

    with open(yaml_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Schema version check
    meta = raw.get("_meta", {})
    schema = meta.get("schema_version", 0)
    if schema != SCHEMA_VERSION:
        raise ValueError(
            f"Country config {yaml_path.name} has schema_version={schema}, "
            f"loader expects {SCHEMA_VERSION}. Migrate the YAML or update the loader."
        )

    cfg = CountryConfig(
        country_code=raw["country_code"],
        country_name=raw["country_name"],
        eubucco_version=raw["eubucco"]["version"],
        nuts2_partitions=raw["eubucco"]["nuts2_partitions"],
        eubucco_base_url=raw["eubucco"]["base_url"],
        eubucco_license=raw["eubucco"]["license"],
        nuts3_regions=raw["nuts3_regions"],
        bbox_wgs84=raw["bbox_wgs84"],
        tabula_source_country=raw["tabula"]["source_country"],
        tabula_source_country_name=raw["tabula"]["source_country_name"],
        tabula_intensities_file=raw["tabula"]["intensities_file"],
        tabula_reason_for_proxy=raw["tabula"]["reason_for_proxy"],
        hdd_country=raw["climate"]["hdd_country"],
        hdd_proxy=raw["climate"]["hdd_proxy"],
        tabula_reference_hdd=raw["climate"].get(
            "tabula_reference_hdd", raw["climate"]["hdd_proxy"]),
        climate_multiplier=raw["climate"]["climate_multiplier"],
        hdd_source=raw["climate"]["source"],
        retrofit_share_original=raw["retrofit"]["share"]["original"],
        retrofit_share_standard=raw["retrofit"]["share"]["standard"],
        retrofit_share_advanced=raw["retrofit"]["share"]["advanced"],
        retrofit_factor_standard=raw["retrofit"]["factor"]["standard"],
        retrofit_factor_advanced=raw["retrofit"]["factor"]["advanced"],
        retrofit_blend_value=raw["retrofit"]["blend_value"],
        dhw_sfh=raw["dhw"]["sfh"],
        dhw_mfh=raw["dhw"]["mfh"],
        dhw_source=raw["dhw"]["source"],
        non_residential_intensity=raw["non_residential_intensity"]["value"],
        non_residential_source=raw["non_residential_intensity"]["source"],
        reconciliation_benchmarks=raw["reconciliation_benchmarks"],
        hotmaps_nuts3_id=raw["hotmaps_nuts3_id"],
        floor_height_residential_m=raw["classification"]["floor_height_residential_m"],
        floor_height_other_m=raw["classification"]["floor_height_other_m"],
        useable_area_fraction=raw["classification"]["useable_area_fraction"],
        floor_source=raw["classification"].get("floor_source", "estimate"),
        comfort_regime_deflator=(raw.get("comfort_regime") or {}).get("deflator"),
        comfort_regime_source=(raw.get("comfort_regime") or {}).get("source", ""),
        tabula_class_mix=raw["tabula"].get("class_mix"),
        eubucco_area_correction=(raw.get("eubucco") or {}).get("area_correction"),
        eubucco_area_correction_source=(raw.get("eubucco") or {}).get(
            "area_correction_source", ""),
        tabula_region_split=raw["tabula"].get("region_split"),
        tabula_region_split_source=raw["tabula"].get("region_split_source", ""),
        raw=raw,
    )

    cfg.validate()
    return cfg


def list_available_countries(repo_root: Path | None = None) -> list[str]:
    """Return the list of country codes (upper-case) with a config file present."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    cfg_dir = repo_root / "code" / "data" / "country_config"
    if not cfg_dir.exists():
        return []
    return sorted(p.stem.upper() for p in cfg_dir.glob("*.yaml"))
