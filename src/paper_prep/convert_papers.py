"""Convert PDF papers to Markdown using docling.

This is a thin, file-level wrapper around the docling Python API. It converts
every PDF in an input directory to a Markdown file in an output directory,
skipping files that already have a corresponding Markdown file unless
``--overwrite`` is set.

Per-file enrichment failures (notably formula enrichment) are caught and the
file is retried with a less enriched pipeline, so one problematic PDF does not
stop the batch.

After conversion, a ``paper_index.json`` file is written in the output directory
mapping each PDF filename to its Markdown filename and extracted title.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, TextItem
from docling_core.types.doc.labels import DocItemLabel

if TYPE_CHECKING:
    from collections.abc import Sequence

_IMAGE_MODES = {
    "placeholder": ImageRefMode.PLACEHOLDER,
    "embedded": ImageRefMode.EMBEDDED,
    "referenced": ImageRefMode.REFERENCED,
}

logger = logging.getLogger("convert_papers")

_MAX_TITLE_LEN = 300
_INDEX_FILE = "paper_index.json"


def _clean_title(text: str) -> str:
    """Normalize and truncate a title string for the index."""
    title = " ".join(text.split())
    if len(title) > _MAX_TITLE_LEN:
        title = title[: _MAX_TITLE_LEN - 1] + "…"
    return title


def _extract_title(doc: object) -> str | None:
    """Extract the document title, falling back to the first heading or paragraph."""
    # Explicit title items come first.
    for item, _level in doc.iterate_items():
        if item.label == DocItemLabel.TITLE and isinstance(item, TextItem):
            text = item.text.strip()
            if text:
                return _clean_title(text)

    # First section header is usually the paper title.
    for item, _level in doc.iterate_items():
        if item.label == DocItemLabel.SECTION_HEADER and isinstance(item, TextItem):
            text = item.text.strip()
            if text:
                return _clean_title(text)

    # Fallback to any non-empty text item.
    for item, _level in doc.iterate_items():
        if isinstance(item, TextItem):
            text = item.text.strip()
            if text:
                return _clean_title(text)

    return None


def _build_converter(
    *, formula: bool = False, code: bool = False, charts: bool = False
) -> DocumentConverter:
    """Build a docling converter with the requested enrichments enabled."""
    options = PdfPipelineOptions()
    options.do_formula_enrichment = formula
    options.do_code_enrichment = code
    options.do_chart_extraction = charts
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def _convert_file(
    converter: DocumentConverter,
    pdf_path: Path,
    out_path: Path,
    image_mode: ImageRefMode,
) -> tuple[bool, str | None]:
    """Convert a single PDF and write Markdown. Return (success, title)."""
    try:
        result = converter.convert(str(pdf_path))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Conversion failed for %s: %s", pdf_path.name, exc)
        return False, None

    title = _extract_title(result.document)

    try:
        result.document.save_as_markdown(str(out_path), image_mode=image_mode)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Markdown export failed for %s: %s", pdf_path.name, exc)
        return False, None

    logger.info("Wrote %s", out_path.name)
    return True, title


def _convert_with_fallback(
    pdf_path: Path,
    out_path: Path,
    image_mode: ImageRefMode,
    *,
    enrich_formula: bool,
    enrich_code: bool,
    enrich_charts: bool,
) -> tuple[bool, str | None]:
    """Convert one PDF, falling back to a simpler pipeline on failure."""
    converter = _build_converter(
        formula=enrich_formula, code=enrich_code, charts=enrich_charts
    )
    success, title = _convert_file(converter, pdf_path, out_path, image_mode)
    if success:
        return True, title

    if enrich_formula:
        logger.info("Retrying %s without formula enrichment", pdf_path.name)
        converter = _build_converter(
            formula=False, code=enrich_code, charts=enrich_charts
        )
        success, title = _convert_file(converter, pdf_path, out_path, image_mode)
        if success:
            logger.info("Wrote %s (formula enrichment disabled)", out_path.name)
            return True, title

    if enrich_formula or enrich_code or enrich_charts:
        logger.info("Retrying %s without any enrichment", pdf_path.name)
        converter = _build_converter()
        success, title = _convert_file(converter, pdf_path, out_path, image_mode)
        if success:
            logger.info("Wrote %s (no enrichment)", out_path.name)
            return True, title

    logger.error("Failed to convert %s after fallback attempts", pdf_path.name)
    return False, None


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF papers to Markdown using docling."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path("docs/raw_papers"),
        help="Directory containing PDF files (default: docs/raw_papers).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs/md_papers"),
        help="Directory to write Markdown files (default: docs/md_papers).",
    )
    parser.add_argument(
        "--image-mode",
        choices=list(_IMAGE_MODES),
        default="placeholder",
        help=(
            "How to include images: placeholder (default, smallest), "
            "embedded (base64), or referenced (PNG files alongside the markdown)."
        ),
    )
    parser.add_argument(
        "--enrich-formula",
        action="store_true",
        help="Extract mathematical formulas as LaTeX.",
    )
    parser.add_argument(
        "--enrich-code",
        action="store_true",
        help="Apply code-block enrichment.",
    )
    parser.add_argument(
        "--enrich-charts",
        action="store_true",
        help="Convert bar/pie/line charts into tables.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-convert PDFs even if a Markdown file already exists.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N PDFs (useful for a quick test).",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Console logging level (default: INFO).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    if not input_dir.is_dir():
        logger.error("Input directory does not exist: %s", input_dir)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    image_mode = _IMAGE_MODES[args.image_mode]

    pdf_paths = sorted(input_dir.glob("*.pdf"))
    if args.limit is not None:
        pdf_paths = pdf_paths[: args.limit]

    if not pdf_paths:
        logger.warning("No PDF files found in %s", input_dir)
        return 0

    skipped = 0
    failed: list[Path] = []
    index: dict[str, dict[str, str]] = {}

    for pdf_path in pdf_paths:
        out_path = output_dir / (pdf_path.stem + ".md")
        if out_path.exists() and not args.overwrite:
            logger.info("Skipping %s (already exists)", out_path.name)
            skipped += 1
            continue

        success, title = _convert_with_fallback(
            pdf_path,
            out_path,
            image_mode,
            enrich_formula=args.enrich_formula,
            enrich_code=args.enrich_code,
            enrich_charts=args.enrich_charts,
        )
        if success:
            index[pdf_path.name] = {
                "markdown": out_path.name,
                "title": title or "",
            }
        else:
            failed.append(pdf_path)

    index_path = output_dir / _INDEX_FILE
    try:
        with index_path.open("w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=2, ensure_ascii=False)
        logger.info("Wrote index %s with %d entries", index_path.name, len(index))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to write %s: %s", index_path.name, exc)

    logger.info(
        "Done. Processed %d PDFs, skipped %d existing, failed %d.",
        len(pdf_paths) - skipped,
        skipped,
        len(failed),
    )
    if failed:
        logger.error("Failed files: %s", ", ".join(p.name for p in failed))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
