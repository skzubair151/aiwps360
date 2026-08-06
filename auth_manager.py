# AUTH MANAGER - Login & User Management
import sqlite3
import hashlib
from datetime import datetime

class AuthManager:
    def __init__(self, db_name='production.db'):
        self.db_name = db_name
        self.current_user = None
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Authenticate user"""
        hashed = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ? AND status = 'Active'",
            (username, hashed)
        )
        result = cursor.fetchone()
        
        if result:
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result[0])
            )
            conn.commit()
            
            self.current_user = {
                'id': result[0],
                'username': result[1],
                'full_name': result[2],
                'role': result[3]
            }
            conn.close()
            return True, "Login successful!"
        
        conn.close()
        return False, "Invalid username or password!"
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        return True
    
    def get_current_user(self):
        """Get current user info"""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is Admin"""
        return self.current_user and self.current_user['role'] == 'Admin'
    
    def is_manager(self):
        """Check if current user is Manager or Admin"""
        return self.current_user and self.current_user['role'] in ['Admin', 'Manager']
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        hashed_old = self.hash_password(old_password)
        hashed_new = self.hash_password(new_password)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, hashed_old)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Current password is incorrect!"
        
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_new, username)
        )
        conn.commit()
        conn.close()
        return True, "Password changed successfully!"
    
    def add_user(self, username, password, full_name, role='Staff'):
        """Add new user"""
        hashed = self.hash_password(password)
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role, created_date) VALUES (?, ?, ?, ?, ?)",
                (username, hashed, full_name, role, today)
            )
            conn.commit()
            conn.close()
            return True, f"User '{username}' added successfully!"
        except:
            conn.close()
            return False, f"Username '{username}' already exists!"
    
    def get_all_users(self):
        """Get all users"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, full_name, role, status, last_login FROM users ORDER BY username"
        )
        results = cursor.fetchall()
        conn.close()
        return results
    
    def delete_user(self, username):
        """Delete user (cannot delete admin)"""
        if username == 'admin':
            return False, "Cannot delete admin user!"
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True, f"User '{username}' deleted!"
    
    def update_user_role(self, username, role):
        """Update user role"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (role, username)
        )
        conn.commit()
        conn.close()
        return True, f"Role updated for '{username}'!"
    
    def update_user_status(self, username, status):
        """Activate/Deactivate user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET status = ? WHERE username = ?",
            (status, username)
        )
        conn.commit()
        conn.close()
        return True, f"Status updated for '{username}'!"