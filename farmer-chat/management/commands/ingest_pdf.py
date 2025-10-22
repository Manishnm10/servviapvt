import os
from django.core.management.base import BaseCommand
from healthcare.ingest_pdf import ingest_home_remedies_pdf, setup_pdf_ingestion_environment

class Command(BaseCommand):
    help = 'Ingest Home Remedies PDF into ServVIA healthcare vector database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pdf-path',
            type=str,
            help='Custom path to the PDF file',
            default=None
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏥 ServVIA Healthcare PDF Ingestion Starting...')
        )
        
        # Setup environment
        data_dir = setup_pdf_ingestion_environment()
        
        # Custom PDF path if provided
        if options['pdf_path']:
            pdf_path = options['pdf_path']
            if os.path.exists(pdf_path):
                self.stdout.write(f"📄 Using custom PDF path: {pdf_path}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Custom PDF path not found: {pdf_path}")
                )
                return
        
        # Run ingestion
        success = ingest_home_remedies_pdf()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('✅ PDF ingestion completed successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS('🎯 ServVIA can now provide home remedies from your PDF')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ PDF ingestion failed. Check the logs for details.')
            )