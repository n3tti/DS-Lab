
import os
import subprocess
import logging
import shutil
import tempfile
from azure.functions import HttpRequest, HttpResponse, func

app = func.FunctionApp()

@app.route(route="scraper", auth_level=func.AuthLevel.FUNCTION)
async def scraper(req: func.HttpRequest) -> func.HttpResponse:
    # Parse request for repo URL and command
    repo_url = req.params.get('https://github.com/n3tti/DS-Lab.git')
    command = req.params.get('cd crawler && scrapy crawl mycrawler')
    
    if not repo_url or not command:
        return HttpResponse("Please pass a repo_url and command in the query string", status_code=400)
    
    # Temporary directory for cloning the repo
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Clone the repository
        logging.info(f"Cloning repository: {repo_url}")
        subprocess.run(['git', 'clone', repo_url, temp_dir], check=True)

        # Change to repo directory
        os.chdir(temp_dir)

        # Run the specified command
        logging.info(f"Running command: {command}")
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        # Return command output
        return HttpResponse(f"Command output: {process.stdout}", status_code=200)
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command: {e}")
        return HttpResponse(f"Error: {e}", status_code=500)
    
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


