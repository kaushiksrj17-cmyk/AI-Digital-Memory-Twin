"""Document Processing Service for ECHO.

Processes scanned and digital textual documents (PDF, TXT, DOCX):
- Preserves original documents unmodified in D:\\ECHO\\storage\\originals
- Extracts clean textual content with page/paragraph hierarchy
- Extracts document technical metadata (page count, author, creation date)
- Strictly preserves text fidelity without rewriting or hallucinating
- Generates structured evidence records with DIRECTLY_OBSERVED provenance.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from uuid import uuid4
import os
import pypdf
import docx

from models.enums import (
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType
)
from models.evidence import Evidence
from storage.vault_storage import vault_storage


class DocumentProcessor:
    """Specialized processor for historical letters, official records, and manuscripts."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}

    def __init__(self):
        self.processor_name = "DocumentProcessor"
        self.processor_version = "echo-doc-v1.0"

    async def process_document(
        self,
        media_id: str,
        relative_path: str,
        memory_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract structured text and metadata from document assets."""
        abs_path = vault_storage.get_absolute_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Document file missing from storage: {relative_path}")

        ext = abs_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported document format: {ext}")

        file_size = abs_path.stat().st_size
        full_text = ""
        pages_data: List[Dict[str, Any]] = []
        headings: List[str] = []
        author = None
        doc_title = None

        # 1. Format-specific text extraction
        if ext == ".txt":
            try:
                full_text = abs_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                full_text = abs_path.read_text(encoding="latin-1", errors="replace")
            pages_data.append({
                "page_number": 1,
                "text": full_text
            })

        elif ext == ".pdf":
            try:
                reader = pypdf.PdfReader(str(abs_path))
                if reader.metadata:
                    author = reader.metadata.author
                    doc_title = reader.metadata.title

                for idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    pages_data.append({
                        "page_number": idx + 1,
                        "text": page_text
                    })
                    if page_text:
                        full_text += f"\n[Page {idx + 1}]\n" + page_text
                full_text = full_text.strip()
            except Exception as e:
                full_text = f"[PDF Parsing Notice: Direct text extraction encountered an error: {str(e)}]"

        elif ext == ".docx":
            try:
                doc = docx.Document(str(abs_path))
                paragraphs_text = []
                for p in doc.paragraphs:
                    text = p.text.strip()
                    if text:
                        paragraphs_text.append(text)
                        if p.style and "heading" in p.style.name.lower():
                            headings.append(text)

                full_text = "\n\n".join(paragraphs_text)
                pages_data.append({
                    "page_number": 1,
                    "text": full_text
                })
                if doc.core_properties:
                    author = doc.core_properties.author
                    doc_title = doc.core_properties.title
            except Exception as e:
                full_text = f"[DOCX Parsing Notice: Direct text extraction encountered an error: {str(e)}]"

        technical_metadata = {
            "format": ext.replace(".", "").upper(),
            "file_size": file_size,
            "page_count": len(pages_data),
            "character_count": len(full_text),
            "word_count": len(full_text.split()),
            "author": author,
            "title": doc_title,
            "detected_headings": headings
        }

        evidence_items: List[Evidence] = []

        # Technical Metadata Evidence
        meta_evidence = Evidence(
            id=str(uuid4()),
            memory_id=memory_id,
            media_id=media_id,
            title="Document Archival Metadata",
            evidence_type=EvidenceType.DOCUMENT_METADATA,
            content=f"Document format {ext.upper()}, {len(pages_data)} pages, {len(full_text.split())} words.",
            structured_value=technical_metadata,
            source_reference=f"Document Manifest ({abs_path.name})",
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=1.0,
            extraction_method="format_document_inspector",
            processor_version=self.processor_version
        )
        evidence_items.append(meta_evidence)

        # Primary Text Content Evidence
        if full_text.strip():
            text_evidence = Evidence(
                id=str(uuid4()),
                memory_id=memory_id,
                media_id=media_id,
                title="Preserved Document Text Excerpt",
                evidence_type=EvidenceType.TEXT,
                content=full_text[:4000] if len(full_text) > 4000 else full_text,  # Keep excerpt reasonable
                structured_value={
                    "page_count": len(pages_data),
                    "is_full_text": len(full_text) <= 4000
                },
                source_reference=f"Primary Text Source ({abs_path.name})",
                provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                extraction_method="direct_document_text_parser",
                processor_version=self.processor_version
            )
            evidence_items.append(text_evidence)

        return {
            "media_id": media_id,
            "processor": self.processor_name,
            "processor_version": self.processor_version,
            "technical_metadata": technical_metadata,
            "full_text": full_text,
            "pages": pages_data,
            "evidence": evidence_items,
            "document_status": "COMPLETED",
            "message": f"Document extraction complete. Extracted {len(full_text)} characters across {len(pages_data)} pages."
        }


document_processor = DocumentProcessor()
