# DV Aviation Chat Agent - Cloud Run Deployment
# Optimized for fast cold starts and low cost

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY knowledge/ ./knowledge/

# Verify logo file exists
RUN ls -la /app/app/static/assets/ || echo "Assets directory listing"

# Expose port (Cloud Run uses PORT env var)
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
# Force rebuild - 2025-11-19 language button added to sticky bar as 4th button
# Rebuild trigger Sat Nov 29 - Desktop viewport refinements
# Sat Nov 29 11:45 - Local SEO & GEO optimization: schema, meta tags, sr-only AI content
# Fri Nov 29 03:22 - Added DV Aviation logo to header and footer
# Fri Nov 29 03:40 - WCAG 2.1 AA typography: responsive font scale, touch targets, color contrast
# Fri Nov 29 03:50 - Added white opaque background to jet-subtext for readability
