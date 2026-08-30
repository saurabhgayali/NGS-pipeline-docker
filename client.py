#!/usr/bin/env python3
"""
NGS Pipeline Web Wrapper - Python API Client
Example client for interacting with the web API
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import sys

class NGSPipelineClient:
    """Client for NGS Pipeline Web API"""
    
    def __init__(self, base_url: str = "http://localhost:7860"):
        """Initialize client"""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()
    
    def list_projects(self) -> Dict:
        """List all projects"""
        response = self.session.get(f"{self.base_url}/api/projects")
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id: str) -> Dict:
        """Get project details"""
        response = self.session.get(f"{self.base_url}/api/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    
    def get_project_status(self, project_id: str) -> Dict:
        """Get real-time project status"""
        response = self.session.get(f"{self.base_url}/api/projects/{project_id}/status")
        response.raise_for_status()
        return response.json()
    
    def create_project(self) -> Dict:
        """Create new project from input queue"""
        response = self.session.post(f"{self.base_url}/api/projects/create")
        response.raise_for_status()
        return response.json()
    
    def execute_project(self, project_id: str) -> Dict:
        """Execute pipeline for project"""
        response = self.session.post(f"{self.base_url}/api/projects/{project_id}/execute")
        response.raise_for_status()
        return response.json()
    
    def get_stage_logs(self, project_id: str, stage: str) -> Dict:
        """Get logs for a specific stage"""
        response = self.session.get(f"{self.base_url}/api/projects/{project_id}/logs/{stage}")
        response.raise_for_status()
        return response.json()
    
    def list_artifacts(self, project_id: str) -> Dict:
        """List project artifacts"""
        response = self.session.get(f"{self.base_url}/api/projects/{project_id}/artifacts")
        response.raise_for_status()
        return response.json()
    
    def download_artifact(self, project_id: str, file_path: str, output_file: str) -> Path:
        """Download artifact to local file"""
        from urllib.parse import quote
        url = f"{self.base_url}/api/projects/{project_id}/artifacts/{quote(file_path)}"
        response = self.session.get(url)
        response.raise_for_status()
        
        output_path = Path(output_file)
        output_path.write_bytes(response.content)
        return output_path
    
    def wait_for_completion(self, project_id: str, timeout: int = 86400, poll_interval: int = 30) -> Dict:
        """Wait for project to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                metadata = self.get_project(project_id)
                status = metadata.get('status', 'unknown')
                
                print(f"Status: {status}")
                
                if status in ['completed', 'failed']:
                    return metadata
                
                time.sleep(poll_interval)
            
            except requests.RequestException as e:
                print(f"Error checking status: {e}")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Project {project_id} did not complete within {timeout} seconds")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="NGS Pipeline Web Wrapper - Python API Client"
    )
    parser.add_argument(
        '--url', 
        default='http://localhost:7860',
        help='Base URL of NGS Pipeline API (default: http://localhost:7860)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health check
    subparsers.add_parser('health', help='Check API health')
    
    # List projects
    subparsers.add_parser('list', help='List all projects')
    
    # Create project
    subparsers.add_parser('create', help='Create new project from input queue')
    
    # Get project info
    get_parser = subparsers.add_parser('get', help='Get project details')
    get_parser.add_argument('project_id', help='Project ID')
    
    # Get project status
    status_parser = subparsers.add_parser('status', help='Get project status')
    status_parser.add_argument('project_id', help='Project ID')
    
    # Execute project
    execute_parser = subparsers.add_parser('execute', help='Execute pipeline')
    execute_parser.add_argument('project_id', help='Project ID')
    
    # Get logs
    logs_parser = subparsers.add_parser('logs', help='Get stage logs')
    logs_parser.add_argument('project_id', help='Project ID')
    logs_parser.add_argument('stage', help='Stage name')
    
    # List artifacts
    artifacts_parser = subparsers.add_parser('artifacts', help='List artifacts')
    artifacts_parser.add_argument('project_id', help='Project ID')
    
    # Download artifact
    download_parser = subparsers.add_parser('download', help='Download artifact')
    download_parser.add_argument('project_id', help='Project ID')
    download_parser.add_argument('file_path', help='File path in artifacts')
    download_parser.add_argument('output_file', help='Output file path')
    
    # Wait for completion
    wait_parser = subparsers.add_parser('wait', help='Wait for project completion')
    wait_parser.add_argument('project_id', help='Project ID')
    wait_parser.add_argument('--timeout', type=int, default=86400, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create client
    client = NGSPipelineClient(args.url)
    
    try:
        if args.command == 'health':
            result = client.health_check()
            print(json.dumps(result, indent=2))
        
        elif args.command == 'list':
            result = client.list_projects()
            print(json.dumps(result, indent=2))
        
        elif args.command == 'create':
            result = client.create_project()
            print(json.dumps(result, indent=2))
        
        elif args.command == 'get':
            result = client.get_project(args.project_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'status':
            result = client.get_project_status(args.project_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'execute':
            result = client.execute_project(args.project_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'logs':
            result = client.get_stage_logs(args.project_id, args.stage)
            print('\n'.join(result.get('logs', [])))
        
        elif args.command == 'artifacts':
            result = client.list_artifacts(args.project_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'download':
            output_path = client.download_artifact(
                args.project_id, 
                args.file_path, 
                args.output_file
            )
            print(f"Downloaded to: {output_path}")
        
        elif args.command == 'wait':
            result = client.wait_for_completion(args.project_id, args.timeout)
            print(json.dumps(result, indent=2))
        
        return 0
    
    except requests.RequestException as e:
        print(f"API Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
