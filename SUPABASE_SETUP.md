# Supabase Setup Guide

## Overview
This Personal Expense Tracker has been migrated to use Supabase as the cloud database backend with user authentication and multi-user support.

## Prerequisites
- Python 3.8+
- Supabase account (free tier available at https://supabase.com)
- A Supabase project created

## Step 1: Get Your Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Settings** → **API**
4. Copy:
   - `Project URL` (will be your `SUPABASE_URL`)
   - `anon public` key (will be your `SUPABASE_ANON_KEY`)

## Step 2: Set Environment Variables

Add these to your system environment or create a `.env` file in the project root:

\`\`\`\
bash\
export SUPABASE_URL="your-project-url-here"\
export SUPABASE_ANON_KEY="your-anon-key-here"\
\`\`\`

Or on Windows (PowerShell):
```powershell
$env:SUPABASE_URL="your-project-url-here"
$env:SUPABASE_ANON_KEY="your-anon-key-here"
