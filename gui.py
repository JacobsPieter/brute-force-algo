import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from parse_items import load_items_from_json
from run_all_combinations import run_all_combinations  # je bestaande functie

class BuildPickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wynncraft Build Picker")
        self.root.geometry("950x600")

        # ===== JSON bestand =====
        self.json_path_var = tk.StringVar()
        tk.Label(root, text="Items JSON:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(root, textvariable=self.json_path_var, width=60).grid(row=0, column=1, sticky="we", padx=5)
        tk.Button(root, text="Browse", command=self.browse_json).grid(row=0, column=2, padx=5)

        # ===== Vereiste stats =====
        tk.Label(root, text="Required Stats (str:100,agi:50,...):").grid(row=1, column=0, columnspan=3, sticky="w", padx=5)
        self.stats_entry = tk.Entry(root, width=80)
        self.stats_entry.grid(row=2, column=0, columnspan=3, sticky="we", padx=5, pady=2)

        # ===== Beste amount =====
        tk.Label(root, text="Number of best combinations:").grid(row=3, column=0, sticky="w", padx=5)
        self.best_amount_var = tk.IntVar(value=10)
        tk.Entry(root, textvariable=self.best_amount_var, width=10).grid(row=3, column=1, sticky="w", padx=5)

        # ===== Run knop =====
        tk.Button(root, text="Find Best Combinations", command=self.run_combinations).grid(row=4, column=0, columnspan=3, pady=5)

        # ===== Resultaten frame =====
        result_frame = tk.Frame(root)
        result_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        root.grid_rowconfigure(5, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Treeview
        self.tree = ttk.Treeview(result_frame, columns=("combination", "stats"), show="headings")
        self.tree.heading("combination", text="Combination")
        self.tree.heading("stats", text="Stats")
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel scrolling
        self.tree.bind("<Enter>", lambda e: self.tree.bind_all("<MouseWheel>", self.on_mousewheel))
        self.tree.bind("<Leave>", lambda e: self.tree.unbind_all("<MouseWheel>"))

    def on_mousewheel(self, event):
        self.tree.yview_scroll(int(-1*(event.delta/120)), "units")

    def browse_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.json_path_var.set(path)

    def parse_required_stats(self):
        stat_text = self.stats_entry.get()
        stats = {}
        if stat_text:
            try:
                for pair in stat_text.split(","):
                    key, val = pair.split(":")
                    stats[key.strip()] = int(val.strip())
            except Exception:
                messagebox.showerror("Error", "Invalid required stats format. Example: str:100,agi:50")
                return None
        return stats

    def run_combinations(self):
        json_path = self.json_path_var.get()
        if not json_path:
            messagebox.showerror("Error", "Please select a JSON file.")
            return
        required_stats = self.parse_required_stats()
        if required_stats is None:
            return
        best_amount = self.best_amount_var.get()

        try:
            best_combos = run_all_combinations(json_path, required_stats, best_amount)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compute combinations:\n{e}")
            return

        # Clear previous results
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Insert new results
        for name, stats in best_combos.items():
            stats_str = ", ".join(f"{k}:{v}" for k, v in stats.items())
            self.tree.insert("", "end", values=(name, stats_str))

        # Auto resize columns
        """ for col in ("combination", "stats"):
            self.tree.column(col, width=tk.font.Font().measure(col.title()))
 """
if __name__ == "__main__":
    root = tk.Tk()
    app = BuildPickerGUI(root)
    root.mainloop()
