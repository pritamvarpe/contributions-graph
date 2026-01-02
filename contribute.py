#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta
import random

def run_command(command, cwd=None):
    """Execute shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Command failed: {e}")
        return False

def init_git_repo():
    """Initialize git repository"""
    if not os.path.exists('.git'):
        run_command('git init')
        run_command('git config user.name "GitHub Activity Generator"')
        
def create_commit(date, commit_count=1):
    """Create commits for a specific date"""
    for i in range(commit_count):
        # Create or modify a file
        filename = f"data_{date.strftime('%Y%m%d')}_{i}.txt"
        with open(filename, 'w') as f:
            f.write(f"Commit {i+1} on {date.strftime('%Y-%m-%d')}\n")
            f.write(f"Random data: {random.randint(1000, 9999)}\n")
        
        # Add and commit with random time during the day
        hour = random.randint(9, 18)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        commit_datetime = date.replace(hour=hour, minute=minute, second=second)
        
        run_command(f'git add {filename}')
        commit_date = commit_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # Set both author and committer date for GitHub to recognize
        os.environ['GIT_AUTHOR_DATE'] = commit_date
        os.environ['GIT_COMMITTER_DATE'] = commit_date
        run_command(f'git commit -m "Activity on {date.strftime("%Y-%m-%d")}"')

def generate_activity(args):
    """Generate GitHub activity based on arguments"""
    init_git_repo()
    
    # Calculate date range
    today = datetime.now()
    start_date = today - timedelta(days=args.days_before)
    end_date = today + timedelta(days=args.days_after)
    
    current_date = start_date
    total_days = (end_date - start_date).days
    active_days = int(total_days * (args.frequency / 100))
    
    print(f"Generating activity from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Target active days: {active_days} out of {total_days} days")
    
    # Generate random active days
    all_days = []
    while current_date <= end_date:
        # Skip weekends if requested
        if args.no_weekends and current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        all_days.append(current_date)
        current_date += timedelta(days=1)
    
    # Select random days to be active
    if active_days < len(all_days):
        active_dates = random.sample(all_days, active_days)
    else:
        active_dates = all_days
    
    active_dates.sort()
    
    # Generate commits for active days
    for date in active_dates:
        commit_count = random.randint(1, args.max_commits)
        create_commit(date, commit_count)
        print(f"Created {commit_count} commit(s) for {date.strftime('%Y-%m-%d')}")
    
    print(f"\nGenerated {len(active_dates)} active days with commits")
    
    # Push to repository if specified
    if args.repository:
        print(f"\nPushing to repository: {args.repository}")
        run_command(f'git remote add origin {args.repository}')
        run_command('git branch -M main')
        if run_command('git push -u origin main'):
            print("Successfully pushed to GitHub!")
            print("Wait 2-5 minutes for GitHub to update your contribution graph")
        else:
            print("❌ Failed to push to repository")
    else:
        print("\n🧪 Test mode: Commits generated locally but not pushed to GitHub")
        print("To push later, add: --repository=git@github.com:username/repo.git")

def main():
    parser = argparse.ArgumentParser(description='Generate GitHub contribution activity')
    
    parser.add_argument('--repository', type=str, help='GitHub repository SSH URL')
    parser.add_argument('--max_commits', type=int, default=3, help='Maximum commits per day (default: 3)')
    parser.add_argument('--frequency', type=int, default=70, help='Percentage of days to be active (default: 70)')
    parser.add_argument('--days_before', type=int, default=365, help='Days before today to start (default: 365)')
    parser.add_argument('--days_after', type=int, default=0, help='Days after today to continue (default: 0)')
    parser.add_argument('--no_weekends', action='store_true', help='Skip weekends')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.max_commits < 1:
        print("Error: max_commits must be at least 1")
        sys.exit(1)
    
    if args.frequency < 1 or args.frequency > 100:
        print("Error: frequency must be between 1 and 100")
        sys.exit(1)
    
    generate_activity(args)

if __name__ == '__main__':
    main()