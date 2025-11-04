# Personal Expense Tracker with Supabase

A modern, minimalist expense tracking application built with PyQt5 and powered by Supabase for cloud storage and multi-user support.

## Features

- **User Authentication**: Secure login/registration with PBKDF2 password hashing
- **Multi-User Support**: Each user has isolated access to their own expenses
- **Dashboard**: Quick overview with today's, weekly, and monthly expense totals plus recent expense history
- **Expense Management**: Add, edit, delete, and search expenses with full details
- **History**: Browse all expenses with date range and category filters
- **Analytics**: Multiple visualization types:
  - Daily expenses (last 30 days)
  - Weekly expenses (last 12 weeks)
  - Monthly expenses (last 12 months)
  - Yearly expenses (last 5 years)
  - Category breakdown (pie chart and bar chart)
- **Search**: Advanced search by description, date, amount, category, or transaction ID
- **Categories**: 7 pre-configured expense categories with color coding
- **Payment Methods**: Support for multiple payment methods (Cash, Credit Card, Debit Card, Digital Wallet, Bank Transfer)
- **Cloud Storage**: All data securely stored in Supabase PostgreSQL with Row Level Security

## Technology Stack

- **Frontend**: PyQt5 (Modern Desktop UI)
- **Backend**: Supabase (PostgreSQL + Authentication)
- **Database**: PostgreSQL
- **Charting**: Matplotlib
- **Security**: PBKDF2-SHA256 password hashing (100,000 iterations)

# Quick Start Guide - Personal Expense Tracker

## Prerequisites
- Python 3.8 or higher
- A Supabase account (free tier is fine)

## Step 1: Get Supabase Credentials

1. Go to [supabase.com](https://supabase.com)
2. Sign in or create a free account
3. Create a new project (or use existing)
4. Go to **Settings → API**
5. Copy:
    - **Project URL** → This is your `SUPABASE_URL`
    - **anon** public key → This is your `SUPABASE_ANON_KEY`

## Step 2: Set Up Environment Variables

### Option A: Using .env file (Recommended)

1. In your project root folder (where `main.py` is), create a file named `.env`
2. Add your credentials:
   \`\`\`
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   \`\`\`
3. Save the file

### Option B: Using Windows Environment Variables

1. Press `Win + X` and select "Command Prompt (Admin)"
2. Run these commands (replace with your actual credentials):
   \`\`\`
   setx SUPABASE_URL "https://your-project-id.supabase.co"
   setx SUPABASE_ANON_KEY "your-anon-key-here"
   \`\`\`
3. **Restart your terminal or IDE** for changes to take effect

## Step 3: Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

If you get an error, try:
\`\`\`bash
python -m pip install -r requirements.txt
\`\`\`

## Step 4: Verify Setup

\`\`\`bash
python scripts/verify_setup.py
\`\`\`

You should see ✓ Setup verification PASSED

## Step 5: Create Database Schema

1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **+ New Query**
4. Open `scripts/supabase_schema.sql` with a text editor
5. Copy ALL the SQL code
6. Paste it into the Supabase SQL Editor
7. Click **Run** (or press Ctrl + Enter)
8. Wait for success message

## Step 6: Run the App

\`\`\`bash
python main.py
\`\`\`

## First Time Use

1. Click the **Register** tab
2. Create a new account with username and password
3. Click **Register**
4. Switch to **Login** tab
5. Login with your credentials
6. Start tracking expenses!

## Troubleshooting

### "Missing SUPABASE_URL or SUPABASE_ANON_KEY"
- Check Step 1 and Step 2 above
- Make sure you created the `.env` file correctly
- If using environment variables, restart your terminal/IDE

### "Connection refused" or "Failed to connect"
- Verify your SUPABASE_URL is correct (should start with `https://`)
- Check that your Supabase project is active
- Try running `python scripts/verify_setup.py` for more details

### "Table doesn't exist"
- You haven't run the database schema yet (Step 5)
- Go to Supabase SQL Editor and run `scripts/supabase_schema.sql`

### Other errors
- Run `python scripts/verify_setup.py` to diagnose the issue
- Check your internet connection
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Need Help?

- Supabase Docs: https://supabase.com/docs
- Check if `verify_setup.py` can help diagnose issues
- Review logs in the console window
  \`\`\`

## Usage

### Dashboard Tab
- View today's, this week's, and this month's spending totals
- See your 10 most recent expenses
- Click "+ Add Expense" to create a new expense entry

### History Tab
- Browse all your expenses
- Filter by category and date range
- Edit or delete individual expenses

### Analytics Tab
- Visualize spending over time (daily, weekly, monthly, yearly)
- View category breakdown as pie or bar chart

### Search Tab
- Search expenses by description, date, amount, category, or transaction ID

## Database Schema

### Users Table
- `id` (UUID): Primary key
- `username` (VARCHAR): Unique login identifier
- `password_hash` (VARCHAR): Encrypted password with salt
- `email` (VARCHAR): Optional email
- `created_at`, `updated_at`: Timestamps

### Expenses Table
- `id` (SERIAL): Primary key
- `user_id` (UUID): Foreign key to users
- `amount` (DECIMAL): Expense amount
- `category` (VARCHAR): Expense category
- `description` (TEXT): Optional description
- `date` (DATE): Expense date
- `time` (TIME): Expense time
- `payment_method` (VARCHAR): Payment type
- `transaction_id` (VARCHAR): Optional transaction reference
- `created_at`, `updated_at`: Timestamps

### Categories Table
- Per-user categories with custom colors
- Default categories created automatically

## Security Features

1. **Password Encryption**: PBKDF2-SHA256 with 100,000 iterations + salt
2. **Row Level Security**: PostgreSQL RLS policies enforce user data isolation
3. **User Authentication**: Verified login system with session management
4. **Data Privacy**: Each user can only access their own expenses
5. **Automatic Triggers**: Timestamp updates on data changes

## UI Design

- **Color Scheme**: Blue (#3498db), Red (#e74c3c), Orange (#f39c12), Green (#27ae60), Teal (#1abc9c), Gray (#95a5a6)
- **Minimalist Design**: Clean, distraction-free interface
- **Responsive Layout**: Tables and charts scale with window size
- **Modern Styling**: Rounded corners, smooth hover effects, professional typography

## File Structure

\`\`\`
expense_tracker/
├── main.py                          # Application entry point with login
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── SUPABASE_SETUP.md               # Detailed Supabase setup guide
├── MIGRATION_GUIDE.md              # Data migration from SQLite
└── scripts/
    ├── supabase_db.py              # Supabase database layer
    ├── supabase_schema.sql         # Database schema (run in Supabase)
    ├── auth_utils.py               # Password encryption utilities
    ├── login_dialog.py             # Login/registration UI
    ├── charts.py                   # Chart generation
    ├── supabase_init.py            # Supabase connection test
    ├── verify_setup.py             # Setup verification script
    ├── database.py                 # Legacy SQLite (deprecated)
    └── 01_init_database.py         # Legacy SQLite (deprecated)
\`\`\`

## Environment Variables

Required:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

See [Supabase Setup Guide](SUPABASE_SETUP.md) for detailed instructions.

## Troubleshooting

### Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are correct
- Ensure your Supabase project is active
- Run `python scripts/verify_setup.py` to diagnose issues

### Login Problems
- Username is case-sensitive
- Minimum 3 characters for username, 6 for password
- Ensure you registered before attempting login

### Missing Data
- Data is user-specific; verify you're logged in as the correct user
- Check database connection is active

### Charts Not Displaying
- Ensure you have expenses in your database
- Charts will show "No expenses yet" if data is missing

## Future Enhancements

- Budget alerts and notifications
- Recurring expense templates
- Multi-currency support
- Mobile app (iOS/Android)
- Data export (CSV, PDF)
- Advanced analytics and reports
- Shared expenses/splitting
- Receipt image attachment

## Requirements

- Python 3.8+
- PyQt5 5.15+
- Matplotlib 3.8+
- Supabase 2.4+

## License

Personal use. Modify as needed for your expense tracking needs.

## Support

For issues or questions:
1. Check the [Supabase Setup Guide](SUPABASE_SETUP.md)
2. Review the [Troubleshooting](#troubleshooting) section
3. Run `python scripts/verify_setup.py` for diagnostics
4. Check Supabase documentation: https://supabase.com/docs
