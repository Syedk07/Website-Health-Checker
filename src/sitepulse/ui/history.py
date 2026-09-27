"""
History view for SitePulse.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ..services import WebsiteService
from ..models import CheckStatus


class HistoryView:
    """History view showing check results."""
    
    def __init__(self, parent, website_service: WebsiteService):
        """
        Initialize the history view.
        
        Args:
            parent: The parent frame
            website_service: The website service instance
        """
        self.parent = parent
        self.website_service = website_service
        
        self._create_widgets()
        self.refresh()
    
    def _create_widgets(self):
        """Create widgets for the history view."""
        # Title
        title = ttk.Label(
            self.parent,
            text="Check History",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Filter frame
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Website:").pack(side=tk.LEFT, padx=5)
        
        self.website_var = tk.StringVar(value="All Websites")
        self.website_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.website_var,
            state="readonly",
            width=30
        )
        self.website_combo.pack(side=tk.LEFT, padx=5)
        self.website_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        
        ttk.Label(filter_frame, text="Limit:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.limit_var = tk.StringVar(value="100")
        limit_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.limit_var,
            state="readonly",
            width=10,
            values=["50", "100", "200", "500", "All"]
        )
        limit_combo.pack(side=tk.LEFT, padx=5)
        limit_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        
        ttk.Button(
            filter_frame,
            text="Refresh",
            command=self.refresh
        ).pack(side=tk.LEFT, padx=20)
        
        # History tree
        columns = ("Date/Time", "Website", "Status", "Status Code", "Response Time", "Error")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=18)
        
        self.tree.heading("Date/Time", text="Date/Time")
        self.tree.heading("Website", text="Website")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Status Code", text="Status Code")
        self.tree.heading("Response Time", text="Response Time")
        self.tree.heading("Error", text="Error Message")
        
        self.tree.column("Date/Time", width=150)
        self.tree.column("Website", width=150)
        self.tree.column("Status", width=120)
        self.tree.column("Status Code", width=100)
        self.tree.column("Response Time", width=120)
        self.tree.column("Error", width=300)
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=1, column=0, sticky=tk.NSEW)
        vsb.grid(row=1, column=1, sticky=tk.NS)
        hsb.grid(row=2, column=0, sticky=tk.EW)
        
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
    
    def refresh(self):
        """Refresh the history list."""
        # Update website filter combo
        websites = self.website_service.get_all_websites()
        website_names = ["All Websites"] + [w.name for w in websites]
        self.website_combo['values'] = website_names
        
        # Get selected website ID
        selected_name = self.website_var.get()
        website_id = None
        if selected_name != "All Websites":
            for w in websites:
                if w.name == selected_name:
                    website_id = w.id
                    break
        
        # Get limit
        limit_str = self.limit_var.get()
        limit = None if limit_str == "All" else int(limit_str)
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get history
        history = self.website_service.get_check_history(
            website_id=website_id,
            limit=limit
        )
        
        # Create website lookup
        website_lookup = {w.id: w.name for w in websites}
        
        # Populate tree
        for result in history:
            checked_at = datetime.fromisoformat(result.checked_at).strftime("%Y-%m-%d %H:%M:%S") if isinstance(result.checked_at, str) else result.checked_at.strftime("%Y-%m-%d %H:%M:%S")
            website_name = website_lookup.get(result.website_id, f"ID: {result.website_id}")
            status = self._format_status(result.result_status)
            status_code = str(result.status_code) if result.status_code else "N/A"
            response_time = f"{result.response_time_ms} ms" if result.response_time_ms else "N/A"
            error = result.error_message if result.error_message else ""
            
            self.tree.insert("", tk.END, values=(
                checked_at,
                website_name,
                status,
                status_code,
                response_time,
                error
            ))
    
    def _format_status(self, status: CheckStatus) -> str:
        """Format a check status for display."""
        status_map = {
            CheckStatus.SUCCESS: "✓ Success",
            CheckStatus.HTTP_ERROR: "⚠ HTTP Error",
            CheckStatus.TIMEOUT: "✗ Timeout",
            CheckStatus.DNS_FAILURE: "✗ DNS Failed",
            CheckStatus.CONNECTION_ERROR: "✗ Connection Error",
            CheckStatus.SSL_ERROR: "✗ SSL Error",
            CheckStatus.INVALID_URL: "✗ Invalid URL",
            CheckStatus.UNKNOWN_ERROR: "✗ Unknown Error"
        }
        return status_map.get(status, str(status))
