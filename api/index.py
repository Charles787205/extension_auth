from main import app
import os

# Set environment for serverless
os.environ.setdefault('VERCEL', '1')

# This is the handler Vercel needs
handler = app
