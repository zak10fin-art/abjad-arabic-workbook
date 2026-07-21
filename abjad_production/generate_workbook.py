#!/usr/bin/env python3
"""
Abjad Arabic Academy - Workbook Production Engine
Main entry point for workbook generation

Usage:
    python abjad_production/generate_workbook.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from abjad_production.config import Config
from abjad_production.data_loader import DataLoader
from abjad_production.page_generator import PageGenerator
from abjad_production.pdf_converter import PDFConverter

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkbookGenerator:
    """Main workbook generation orchestrator"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize workbook generator
        
        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or Config()
        self.data_loader = DataLoader(self.config)
        self.page_generator = PageGenerator(self.config)
        self.pdf_converter = PDFConverter(self.config)
        
        # Create output directories if they don't exist
        self._create_output_directories()
        
        logger.info("WorkbookGenerator initialized")
    
    def _create_output_directories(self) -> None:
        """Create necessary output directories"""
        for directory in [
            self.config.OUTPUT_SVG_DIR,
            self.config.OUTPUT_PNG_DIR,
            self.config.OUTPUT_PDF_DIR
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory ready: {directory}")
    
    def load_workbook_data(self) -> Dict:
        """
        Load all workbook data from JSON files
        
        Returns:
            Dictionary containing all workbook data
        """
        logger.info("Loading workbook data...")
        
        try:
            workbook_data = self.data_loader.load_all_data()
            logger.info(f"Successfully loaded workbook data")
            return workbook_data
        except Exception as e:
            logger.error(f"Failed to load workbook data: {e}")
            raise
    
    def generate_all_pages(self, workbook_data: Dict) -> List[str]:
        """
        Generate all workbook pages
        
        Args:
            workbook_data: Dictionary containing lesson and activity data
            
        Returns:
            List of generated SVG file paths
        """
        logger.info("Generating all workbook pages...")
        
        generated_files = []
        
        try:
            # Generate lesson pages
            lesson_files = self.page_generator.generate_lesson_pages(
                workbook_data.get('lessons', [])
            )
            generated_files.extend(lesson_files)
            logger.info(f"Generated {len(lesson_files)} lesson pages")
            
            # Generate activity pages
            activity_files = self.page_generator.generate_activity_pages(
                workbook_data.get('activities', [])
            )
            generated_files.extend(activity_files)
            logger.info(f"Generated {len(activity_files)} activity pages")
            
            # Generate review pages
            review_files = self.page_generator.generate_review_pages(
                workbook_data.get('lessons', [])
            )
            generated_files.extend(review_files)
            logger.info(f"Generated {len(review_files)} review pages")
            
            logger.info(f"Total pages generated: {len(generated_files)}")
            return generated_files
            
        except Exception as e:
            logger.error(f"Failed to generate pages: {e}")
            raise
    
    def convert_to_pdf(self, svg_files: List[str], 
                      output_filename: str = "workbook") -> str:
        """
        Convert all SVG files to print-ready PDF
        
        Args:
            svg_files: List of SVG file paths
            output_filename: Name for output PDF (without extension)
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Converting {len(svg_files)} SVG files to PDF...")
        
        try:
            pdf_path = self.pdf_converter.create_pdf_from_svgs(
                svg_files,
                output_filename
            )
            logger.info(f"PDF created successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Failed to convert to PDF: {e}")
            raise
    
    def generate_complete_workbook(self) -> Dict:
        """
        Generate complete workbook (all pages and PDF)
        
        Returns:
            Dictionary with paths to generated files
        """
        logger.info("="*60)
        logger.info("STARTING COMPLETE WORKBOOK GENERATION")
        logger.info("="*60)
        
        try:
            # Step 1: Load data
            workbook_data = self.load_workbook_data()
            
            # Step 2: Generate all pages
            svg_files = self.generate_all_pages(workbook_data)
            
            # Step 3: Convert to PDF
            pdf_path = self.convert_to_pdf(svg_files)
            
            result = {
                'status': 'success',
                'svg_files': svg_files,
                'pdf_file': pdf_path,
                'total_pages': len(svg_files),
                'output_directory': self.config.OUTPUT_DIR
            }
            
            logger.info("="*60)
            logger.info("WORKBOOK GENERATION COMPLETE")
            logger.info("="*60)
            logger.info(f"Total pages: {len(svg_files)}")
            logger.info(f"PDF file: {pdf_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"Workbook generation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }


def main():
    """Main entry point"""
    try:
        # Initialize generator
        generator = WorkbookGenerator()
        
        # Generate complete workbook
        result = generator.generate_complete_workbook()
        
        # Print results
        if result['status'] == 'success':
            print(f"\n✓ Workbook generated successfully!")
            print(f"  Total pages: {result['total_pages']}")
            print(f"  Output directory: {result['output_directory']}")
            print(f"  PDF file: {result['pdf_file']}")
            return 0
        else:
            print(f"\n✗ Workbook generation failed: {result.get('error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
