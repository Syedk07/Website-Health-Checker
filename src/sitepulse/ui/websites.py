"""
Websites management view for SitePulse.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from ..services import WebsiteService, HealthChecker
from ..models import CheckStatus
from datetime import datetime
import threading


class WebsitesView:
    """Websites management view."""
    
    def __init__(self, parent, website_service: WebsiteService, health_checker: HealthChecker):
        """
        Initialize the websites view.
        
        Args:
            parent: The parent frame
            website_service: The website service instance
            health_checker: The health checker instance
        """
        self.parent = parent
        self.website_service = website_service
        self.health_checker = health_checker
        self.checking = {}
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Create widgets for the websites view."""
        # Title
        title = ttk.Label(
            self.parent,
            text="Websites",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="Add Website",
            command=self._add_website
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="Edit Website",
            command=self._edit_website
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="Delete Website",
            command=self._delete_website
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="Check Selected",
            command=self._check_selected
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh
        ).pack(side=tk.LEFT, padx=5)
        
        # Websites tree
        columns = ("ID", "Name", "URL", "Status", "Response Time", "Last Check")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("URL", text="URL")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Response Time", text="Response Time")
        self.tree.heading("Last Check", text="Last Check")
        
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("URL", width=250)
        self.tree.column("Status", width=120)
        self.tree.column("Response Time", width=120)
        self.tree.column("Last Check", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-click to edit
        self.tree.bind("<Double-1>", lambda e: self._edit_website())
    
    def refresh(self):
        """Refresh the websites list."""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all websites
        websites = self.website_service.get_all_websites()
        
        for website in websites:
            latest_result = self.website_service.get_latest_check_result(website.id)
            
            if latest_result:
                status = self._format_status(latest_result.result_status)
                response_time = f"{latest_result.response_time_ms} ms" if latest_result.response_time_ms else "N/A"
                last_check = datetime.fromisoformat(latest_result.checked_at).strftime("%Y-%m-%d %H:%M:%S") if isinstance(latest_result.checked_at, str) else latest_result.checked_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                status = "Not checked"
                response_time = "N/A"
                last_check = "Never"
            
            self.tree.insert("", tk.END, values=(
                website.id,
                website.name,
                website.url,
                status,
                response_time,
                last_check
            ))
    
    def _format_status(self, status: CheckStatus) -> str:
        """Format a check status for display."""
        status_map = {
            CheckStatus.SUCCESS: "✓ Online",
            CheckStatus.HTTP_ERROR: "⚠ HTTP Error",
            CheckStatus.TIMEOUT: "✗ Timeout",
            CheckStatus.DNS_FAILURE: "✗ DNS Failed",
            CheckStatus.CONNECTION_ERROR: "✗ Connection Error",
            CheckStatus.SSL_ERROR: "✗ SSL Error",
            CheckStatus.INVALID_URL: "✗ Invalid URL",
            CheckStatus.UNKNOWN_ERROR: "✗ Unknown Error"
        }
        return status_map.get(status, str(status))
    
    def _add_website(self):
        """Show dialog to add a new website."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Website")
        dialog.geometry("400x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Name
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # URL
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        url_entry = ttk.Entry(dialog, width=40)
        url_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def save():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            
            if not name or not url:
                messagebox.showerror("Error", "Please enter both name and URL")
                return
            
            website = self.website_service.add_website(name, url)
            if website:
                messagebox.showinfo("Success", "Website added successfully!")
                dialog.destroy()
                self.refresh()
            else:
                messagebox.showerror("Error", "This URL already exists in the database")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        name_entry.focus()
    
    def _edit_website(self):
        """Edit the selected website."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a website to edit")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        website_id = values[0]
        current_name = values[1]
        current_url = values[2]
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Website")
        dialog.geometry("400x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Name
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.insert(0, current_name)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # URL
        ttk.Label(dialog, text="URL:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        url_entry = ttk.Entry(dialog, width=40)
        url_entry.insert(0, current_url)
        url_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def save():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            
            if not name or not url:
                messagebox.showerror("Error", "Please enter both name and URL")
                return
            
            success = self.website_service.update_website(website_id, name=name, url=url)
            if success:
                messagebox.showinfo("Success", "Website updated successfully!")
                dialog.destroy()
                self.refresh()
            else:
                messagebox.showerror("Error", "Failed to update website. The URL may already exist.")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _delete_website(self):
        """Delete the selected website."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a website to delete")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        website_id = values[0]
        website_name = values[1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{website_name}'?\n\nThis will also delete all check history for this website."
        )
        
        if confirm:
            success = self.website_service.delete_website(website_id)
            if success:
                messagebox.showinfo("Success", "Website deleted successfully!")
                self.refresh()
            else:
                messagebox.showerror("Error", "Failed to delete website")
    
    def _check_selected(self):
        """Check the selected website."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a website to check")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        website_id = values[0]
        website_url = values[2]
        
        if website_id in self.checking:
            return
        
        self.checking[website_id] = True
        
        # Run check in background
        thread = threading.Thread(target=self._perform_check, args=(website_id, website_url))
        thread.daemon = True
        thread.start()
    
    def _perform_check(self, website_id: int, url: str):
        """Perform health check for a website."""
        result = self.health_checker.check_website(website_id, url)
        self.website_service.save_check_result(result)
        
        # Update UI on main thread
        self.parent.after(0, lambda: self._check_complete(website_id))
    
    def _check_complete(self, website_id: int):
        """Called when a check is complete."""
        if website_id in self.checking:
            del self.checking[website_id]
        self.refresh()
