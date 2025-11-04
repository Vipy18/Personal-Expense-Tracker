-- Create users table
CREATE TABLE IF NOT EXISTS users (
                                     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
                                          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
    );

-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
                                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    time TIME DEFAULT '00:00:00',
    payment_method VARCHAR(100),
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(user_id, category);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to update updated_at
DROP TRIGGER IF EXISTS update_expenses_updated_at ON expenses;
CREATE TRIGGER update_expenses_updated_at
    BEFORE UPDATE ON expenses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Allow registration by permitting INSERT without authentication
CREATE POLICY "Allow user registration" ON users
    FOR INSERT WITH CHECK (true);

-- Restrict SELECT/UPDATE to authenticated users viewing their own data
CREATE POLICY "Users can view their own user record" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own user record" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Categories policies - authenticated users only
CREATE POLICY "Users can select their own categories" ON categories
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own categories" ON categories
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own categories" ON categories
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own categories" ON categories
    FOR DELETE USING (user_id = auth.uid());

-- Expenses policies - authenticated users only
CREATE POLICY "Users can select their own expenses" ON expenses
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own expenses" ON expenses
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own expenses" ON expenses
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own expenses" ON expenses
    FOR DELETE USING (user_id = auth.uid());
