### Currency Converter Project 
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pyperclip
import csv

# ---------------- Fetch available currencies ---------------- #
def get_currencies():
    try:
        response = requests.get("https://api.frankfurter.app/currencies")
        if response.status_code == 200:
            return list(response.json().keys())
    except:
        pass
    return ["USD", "EUR", "INR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY"]

# ---------------- Currency Conversion ---------------- #
def convert_currency():
    base_currency = base_currency_combo.get().upper()
    target_currency = target_currency_combo.get().upper()

    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for amount.")
        return

    try:
        url = f"https://api.frankfurter.app/latest?from={base_currency}&to={target_currency}"
        response = requests.get(url)
        data = response.json()

        rate = data["rates"].get(target_currency)
        if rate:
            converted_amount = amount * rate
            result_label.config(
                text=f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency}"
            )
            last_updated_label.config(text=f"Data Date: {data.get('date', 'N/A')}")
        else:
            messagebox.showerror("Error", "Target currency not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# ---------------- Multi-Currency Conversion ---------------- #
def convert_to_all():
    base_currency = base_currency_combo.get().upper()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for amount.")
        return

    try:
        url = f"https://api.frankfurter.app/latest?from={base_currency}"
        response = requests.get(url)
        data_all = response.json()
        rates_data = data_all["rates"]

        for row in rate_table.get_children():
            rate_table.delete(row)

        for currency, rate in rates_data.items():
            rate_table.insert("", "end", values=(currency, f"{amount * rate:.2f}"))

        last_updated_label.config(text=f"Rates Date: {data_all.get('date', 'N/A')}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch multi-currency rates: {e}")

# ---------------- Show Historical Rates ---------------- #
def show_historical_rates():
    base_currency = base_currency_combo.get().upper()
    target_currency = target_currency_combo.get().upper()

    try:
        days = int(trend_days_combo.get())
    except ValueError:
        days = 7

    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    try:
        url = (f"https://api.frankfurter.app/{start_date.strftime('%Y-%m-%d')}.."
               f"{end_date.strftime('%Y-%m-%d')}?from={base_currency}&to={target_currency}")
        response = requests.get(url)
        data = response.json()["rates"]

        dates = sorted(data.keys())
        rates = [data[date][target_currency] for date in dates]

        plt.figure(figsize=(6, 4))
        plt.plot(dates, rates, marker="o")
        plt.title(f"{base_currency} to {target_currency} - Last {days} Days")
        plt.xlabel("Date")
        plt.ylabel("Rate")
        plt.grid(True)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch historical rates: {e}")

# ---------------- Export to CSV ---------------- #
def export_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Currency", "Rate"])
            for row_id in rate_table.get_children():
                row = rate_table.item(row_id)["values"]
                writer.writerow(row)
        messagebox.showinfo("Success", "Rates exported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export: {e}")

# ---------------- Save Favorite Pair ---------------- #
def save_favorite():
    pair = f"{base_currency_combo.get()}-{target_currency_combo.get()}"
    if pair not in favorites:
        favorites.append(pair)
        fav_combo["values"] = favorites
        messagebox.showinfo("Saved", f"{pair} saved to favorites!")

# ---------------- Load Favorite Pair ---------------- #
def load_favorite(event=None):
    pair = fav_combo.get()
    if "-" in pair:
        base, target = pair.split("-")
        base_currency_combo.set(base)
        target_currency_combo.set(target)

# ---------------- Theme Toggle ---------------- #
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        bg_color = "#2c3e50"
        fg_color = "white"
        btn_bg = "#34495e"
    else:
        bg_color = "#f0f8ff"
        fg_color = "black"
        btn_bg = "#4da6ff"

    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        if isinstance(widget, (tk.Label, tk.Entry, ttk.Combobox)):
            widget.configure(background=bg_color, foreground=fg_color)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=btn_bg, fg=fg_color)

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("Currency Converter 💱")
root.geometry("600x780")
root.configure(bg="#f0f8ff")

dark_mode = False
currencies = get_currencies()
favorites = []

# Base currency
tk.Label(root, text="From Currency:", font=("Arial", 12, "bold"), bg="#f0f8ff").pack()
base_currency_combo = ttk.Combobox(root, values=currencies, font=("Arial", 12))
base_currency_combo.pack()
base_currency_combo.set("USD")

# Target currency
tk.Label(root, text="To Currency:", font=("Arial", 12, "bold"), bg="#f0f8ff").pack()
target_currency_combo = ttk.Combobox(root, values=currencies, font=("Arial", 12))
target_currency_combo.pack()
target_currency_combo.set("INR")

# Amount
tk.Label(root, text="Amount:", font=("Arial", 12, "bold"), bg="#f0f8ff").pack()
amount_entry = tk.Entry(root, font=("Arial", 12))
amount_entry.pack()

# Favorites
tk.Label(root, text="Favorites:", font=("Arial", 12, "bold"), bg="#f0f8ff").pack()
fav_combo = ttk.Combobox(root, values=favorites, font=("Arial", 12))
fav_combo.pack()
fav_combo.bind("<<ComboboxSelected>>", load_favorite)

# Trend days selector
tk.Label(root, text="Trend Duration (days):", font=("Arial", 12, "bold"), bg="#f0f8ff").pack()
trend_days_combo = ttk.Combobox(root, values=["7", "30", "90"], font=("Arial", 12))
trend_days_combo.pack()
trend_days_combo.set("7")

# Buttons
tk.Button(root, text="Convert", command=convert_currency, bg="#4da6ff", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(root, text="Convert to All", command=convert_to_all, bg="#8e44ad", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(root, text="📊 Show Trend", command=show_historical_rates, bg="#28a745", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(root, text="💾 Save Favorite", command=save_favorite, bg="#f39c12", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(root, text="📤 Export CSV", command=export_csv, bg="#e74c3c", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
tk.Button(root, text="🌗 Toggle Theme", command=toggle_theme, bg="#34495e", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

# Result label
result_label = tk.Label(root, text="", font=("Arial", 13, "bold"), bg="#f0f8ff", fg="green")
result_label.pack()

# Table
rate_table = ttk.Treeview(root, columns=("Currency", "Rate"), show="headings", height=10)
rate_table.heading("Currency", text="Currency")
rate_table.heading("Rate", text="Rate")
rate_table.pack()

# Last updated
last_updated_label = tk.Label(root, text="", font=("Arial", 10), bg="#f0f8ff", fg="gray")
last_updated_label.pack()

root.mainloop()


