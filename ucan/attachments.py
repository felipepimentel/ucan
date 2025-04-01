import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple

import fitz  # PyMuPDF
import magic
from PIL import Image

logger = logging.getLogger("UCAN")


class AttachmentManager:
    def __init__(self, db):
        self.db = db
        self.max_image_size = (800, 800)  # Maximum image dimensions
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = {
            "text": [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "document": [".pdf", ".doc", ".docx"],
            "code": [".py", ".js", ".html", ".css", ".json", ".ts", ".jsx", ".tsx"],
        }

        # Create attachments directory
        self.attachments_dir = Path.home() / ".ucan" / "attachments"
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: str) -> Optional[Tuple[str, str, str]]:
        """Process and optimize a file for storage"""
        try:
            file_path = Path(file_path)

            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                raise ValueError("Arquivo muito grande (máximo 10MB)")

            # Get file type
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(str(file_path))
            extension = file_path.suffix.lower()

            # Check if file type is allowed
            allowed = False
            for category, extensions in self.allowed_types.items():
                if extension in extensions:
                    allowed = True
                    break

            if not allowed:
                raise ValueError(f"Tipo de arquivo não suportado: {extension}")

            # Generate unique filename
            file_hash = self._get_file_hash(file_path)
            new_filename = f"{file_hash}{extension}"
            new_path = self.attachments_dir / new_filename

            # Process file based on type
            if file_type.startswith("image/"):
                self._process_image(file_path, new_path)
            elif extension == ".pdf":
                self._process_pdf(file_path, new_path)
            else:
                # Copy file as is
                with open(file_path, "rb") as src, open(new_path, "wb") as dst:
                    dst.write(src.read())

            return str(new_path), file_type, self._generate_preview(new_path, file_type)

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return None

    def _process_image(self, src_path: Path, dst_path: Path) -> None:
        """Process and optimize an image"""
        try:
            with Image.open(src_path) as img:
                # Convert to RGB if needed
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Resize if needed
                if (
                    img.size[0] > self.max_image_size[0]
                    or img.size[1] > self.max_image_size[1]
                ):
                    img.thumbnail(self.max_image_size)

                # Save with optimization
                img.save(dst_path, optimize=True, quality=85)

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise

    def _process_pdf(self, src_path: Path, dst_path: Path) -> None:
        """Process and optimize a PDF"""
        try:
            doc = fitz.open(src_path)
            doc.save(dst_path, garbage=4, deflate=True)
            doc.close()
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    def _generate_preview(self, file_path: Path, mime_type: str) -> Optional[str]:
        """Generate a preview for the file"""
        try:
            if mime_type.startswith("image/"):
                # Create thumbnail
                with Image.open(file_path) as img:
                    img.thumbnail((200, 200))
                    preview_path = file_path.parent / f"preview_{file_path.name}"
                    img.save(preview_path)
                    return str(preview_path)

            elif mime_type == "application/pdf":
                # Get first page as image
                doc = fitz.open(file_path)
                page = doc[0]
                pix = page.get_pixmap()
                preview_path = file_path.parent / f"preview_{file_path.stem}.png"
                pix.save(preview_path)
                doc.close()
                return str(preview_path)

            elif mime_type.startswith("text/"):
                # Get first few lines
                with open(file_path, "r", encoding="utf-8") as f:
                    preview = "\n".join(f.readlines()[:5])
                return preview

            return None

        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            return None

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate a unique hash for a file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:12]
        except Exception as e:
            logger.error(f"Error generating file hash: {str(e)}")
            raise

    def get_file_info(self, file_path: str) -> dict:
        """Get information about a file"""
        try:
            path = Path(file_path)
            mime = magic.Magic(mime=True)

            return {
                "name": path.name,
                "size": path.stat().st_size,
                "type": mime.from_file(str(path)),
                "extension": path.suffix.lower(),
                "preview_supported": any(
                    path.suffix.lower() in exts for exts in self.allowed_types.values()
                ),
            }
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {}
