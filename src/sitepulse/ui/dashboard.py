"""
Dashboard view for SitePulse.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Optional
from datetime import datetime

from ..models import Website, CheckResult, CheckStatus
from ..services import WebsiteService, HealthChecker


class DashboardView:
    """Dashboard view showing website status and summary."""
    
    def __init__(self, parent, website_service: WebsiteService, health_checker: HealthChecker):
        """
        Initialize the dashboard view.
        
        Args:
            parent: The parent frame
            website_service: The website service instance
            health_checker: The health checker instance
        """
        self.parent = parent
        self.website_service = website_service
        self.health_checker = health_checker
        self.checking = False
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Create dashboard widgets."""
        # Title
        title = ttk.Label(
            self.parent,
            text="Dashboard",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Summary cards frame
        summary_frame = ttk.Frame(self.parent)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create summary cards
        self.total_label = self._create_summary_card(summary_frame, "Total Websites", "0", 0)
        self.online_label = self._create_summary_card(summary_frame, "Online", "0", 1)
        self.offline_label = self._create_summary_card(summary_frame, "Offline", "0", 2)
        self.errors_label = self._create_summary_card(summary_frame, "Errors", "0", 3)
        
        # Action buttons
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.check_button = ttk.Button(
            button_frame,
            text="Check All Websites",
            command=self._check_all_websites
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh
        ).pack(side=tk.LEFT, padx=5)
        
        # Progress bar (hidden by default)
        self.progress_frame = ttk.Frame(self.parent)
        self.progress_label = ttk.Label(self.progress_frame, text="Checking websites...")
        self.progress_label.pack()
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Websites list
        list_label = ttk.Label(
            self.parent,
            text="Monitored Websites",
            font=("Arial", 14, "bold")
        )
        list_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Create treeview for websites
        columns = ("Name", "URL", "Status", "Response Time", "Last Check")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Name":
                self.tree.column(col, width=150)
            elif col == "URL":
                self.tree.column(col, width=250)
            elif col == "Status":
                self.tree.column(col, width=100)
            elif col == "Response Time":
                self.tree.column(col, width=120)
            elif col == "Last Check":
                self.tree.column(col, width=150)
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_summary_card(self, parent, title: str, value: str, column: int):
        """Create a summary card widget."""
        card = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        card.grid(row=0, column=column, padx=10, pady=5, sticky=tk.NSEW)
        parent.columnconfigure(column, weight=1)
        
        title_label = ttk.Label(card, text=title, font=("Arial", 10))
        title_label.pack(pady=(10, 5))
        
        value_label = ttk.Label(card, text=value, font=("Arial", 24, "bold"))
        value_label.pack(pady=(0, 10))
        
        return value_label
    
    def refresh(self):
        """Refresh the dashboard data."""
        # Get all websites
        websites = self.website_service.get_all_websites()
        
        # Update summary
        total = len(websites)
        online = 0
        offline = 0
        errors = 0
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate tree and calculate stats
        for website in websites:
            latest_result = self.website_service.get_latest_check_result(website.id)
            
            if latest_result:
                status = self._format_status(latest_result.result_status)
                response_time = f"{latest_result.response_time_ms} ms" if latest_result.response_time_ms else "N/A"
                last_check = datetime.fromisoformat(latest_result.checked_at).strftime("%Y-%m-%d %H:%M:%S") if isinstance(latest_result.checked_at, str) else latest_result.checked_at.strftime("%Y-%m-%d %H:%M:%S")
                
                if latest_result.result_status == CheckStatus.SUCCESS:
                    online += 1
                elif latest_result.result_status == CheckStatus.HTTP_ERROR:
                    errors += 1
                else:
                    offline += 1
            else:
                status = "Not checked"
                response_time = "N/A"
                last_check = "Never"
            
            self.tree.insert("", tk.END, values=(
                website.name,
                website.url,
                status,
                response_time,
                last_check
            ))
        
        # Update summary cards
        self.total_label.config(text=str(total))
        self.online_label.config(text=str(online))
        self.offline_label.config(text=str(offline))
        self.errors_label.config(text=str(errors))
    
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
    
    def _check_all_websites(self):
        """Check all websites in the background."""
        if self.checking:
            return
        
        websites = self.website_service.get_all_websites()
        
        if not websites:
            messagebox.showinfo("No Websites", "No websites to check. Add some websites first.")
            return
        
        self.checking = True
        self.check_button.config(state=tk.DISABLED)
        self.progress_frame.pack(fill=tk.X, pady=10)
        self.progress_bar.start()
        
        # Run checks in background thread
        thread = threading.Thread(target=self._perform_checks, args=(websites,))
        thread.daemon = True
        thread.start()
    
    def _perform_checks(self, websites: List[Website]):
        """Perform health checks for all websites."""
        for website in websites:
            result = self.health_checker.check_website(website.id, website.url)
            self.website_service.save_check_result(result)
        
        # Update UI on main thread
        self.parent.after(0, self._checks_complete)
    
    def _checks_complete(self):
        """Called when all checks are complete."""
        self.checking = False
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        self.check_button.config(state=tk.NORMAL)
        self.refresh()
        messagebox.showinfo("Complete", "All websites have been checked!")
