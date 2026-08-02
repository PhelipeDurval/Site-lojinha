mport tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
import json
import os

HISTORY_FILE = "calc_history.json"


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Python")
        self.root.geometry("760x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.history = self._load_history()
        self.currency_mode = False

        self.display_var = tk.StringVar(value="0")

        main_frame = ttk.Frame(root, padding=16)
        main_frame.pack(fill="both", expand=True)
        main_frame.configure(style="Main.TFrame")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Panel.TLabelframe", background="#111827", bordercolor="#1f2937")
        style.configure("Panel.TLabelframe.Label", background="#111827", foreground="#f9fafb")
        style.configure("Button.TButton", background="#1f2937", foreground="#f9fafb")
        style.map("Button.TButton", background=[("active", "#374151")])
        style.configure("Operator.TButton", background="#ff9f1c", foreground="#111111")
        style.map("Operator.TButton", background=[("active", "#f59e0b")])
        style.configure("Action.TButton", background="#1d4ed8", foreground="#ffffff")
        style.map("Action.TButton", background=[("active", "#2563eb")])
        style.configure("Danger.TButton", background="#ef4444", foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", "#dc2626")])
        style.configure("Accent.TButton", background="#7c3aed", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#6d28d9")])

        self.display = ttk.Entry(
            main_frame,
            textvariable=self.display_var,
            font=("Segoe UI", 24, "bold"),
            justify="right",
            width=24,
        )
        self.display.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0, 12))

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, rowspan=8, sticky="nsew")
        left_frame.configure(style="Main.TFrame")

        buttons = [
            [("C", "Danger.TButton", lambda: self.clear()), ("Hist", "Accent.TButton", lambda: self.toggle_history()), ("⌫", "Accent.TButton", lambda: self.backspace()), ("%", "Accent.TButton", lambda: self.percent())],
            [("/", "Operator.TButton", lambda: self.append_value("/")), ("1", "Button.TButton", lambda: self.append_value("1")), ("2", "Button.TButton", lambda: self.append_value("2")), ("3", "Button.TButton", lambda: self.append_value("3"))],
            [("*", "Operator.TButton", lambda: self.append_value("*")), ("4", "Button.TButton", lambda: self.append_value("4")), ("5", "Button.TButton", lambda: self.append_value("5")), ("6", "Button.TButton", lambda: self.append_value("6"))],
            [("+", "Operator.TButton", lambda: self.append_value("+")), ("7", "Button.TButton", lambda: self.append_value("7")), ("8", "Button.TButton", lambda: self.append_value("8")), ("9", "Button.TButton", lambda: self.append_value("9"))],
            [("-", "Operator.TButton", lambda: self.append_value("-")), ("0", "Button.TButton", lambda: self.append_value("0")), (".", "Button.TButton", lambda: self.append_value(".")), ("Lim.H", "Danger.TButton", lambda: self.clear_history())],
            [("R$", "Accent.TButton", lambda: self.format_currency()), ("=", "Action.TButton", lambda: self.calculate())],
        ]

        for row_idx, row in enumerate(buttons):
            for col_idx, (text, style_name, command) in enumerate(row):
                btn = ttk.Button(left_frame, text=text, style=style_name, command=command)
                if row_idx == 5:
                    btn.grid(row=row_idx, column=col_idx*2, columnspan=2, padx=6, pady=6, sticky="nsew")
                else:
                    btn.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky="nsew")
                btn.config(width=10, padding=10)

        for i in range(4):
            left_frame.columnconfigure(i, weight=1)
        for i in range(len(buttons)):
            left_frame.rowconfigure(i, weight=1)

        history_frame = ttk.LabelFrame(main_frame, text="Histórico", style="Panel.TLabelframe")
        history_frame.grid(row=1, column=4, rowspan=7, padx=(12, 0), sticky="nsew")
        history_frame.configure(padding=10)
        history_frame.grid_remove()
        self.history_frame = history_frame

        self.history_list = tk.Listbox(history_frame, height=15, width=24, bg="#111827", fg="#f9fafb", bd=0, highlightthickness=0)
        self.history_list.pack(fill="both", expand=True)
        self.history_list.bind("<<ListboxSelect>>", self.load_history_item)

        self._refresh_history()
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(4, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(self.history, file, ensure_ascii=False, indent=2)

    def _refresh_history(self):
        self.history_list.delete(0, tk.END)
        if not self.history:
            self.history_list.insert(tk.END, "Nenhuma conta ainda")
            return
        for item in self.history[-10:]:
            self.history_list.insert(tk.END, f"{item['expression']} = {item['result']}")

    def append_value(self, value):
        current = self.display_var.get().strip()
        if current in {"Erro", "Infinity"}:
            current = ""
        if current == "0" and value not in {".", ","}:
            current = value
        else:
            current += value
        self.display_var.set(current)

    def clear(self):
        self.display_var.set("0")
        self.currency_mode = False

    def backspace(self):
        current = self.display_var.get()
        if current in {"Erro", "Infinity"}:
            self.clear()
            return
        if len(current) <= 1:
            self.display_var.set("0")
        else:
            self.display_var.set(current[:-1])

    def percent(self):
        try:
            value = self._parse_input(self.display_var.get())
            self.display_var.set(str(value / 100))
        except (InvalidOperation, ValueError, ZeroDivisionError):
            self.display_var.set("Erro")

    def format_currency(self):
        current = self.display_var.get().strip()
        if not current or current == "Erro":
            return

        try:
            value = self._parse_input(current)
            if self.currency_mode:
                self.display_var.set(str(value))
                self.currency_mode = False
            else:
                self.display_var.set(f"R$ {value:,.2f}".replace(",", "~").replace(".", ",").replace("~", "."))
                self.currency_mode = True
        except (InvalidOperation, ValueError):
            self.display_var.set("Erro")

    def calculate(self):
        expression = self.display_var.get().strip()
        if not expression or expression == "0":
            return
        try:
            result = self._evaluate(expression)
            result_text = self._format_result(result)
            self.display_var.set(result_text)
            self.history.append({"expression": expression, "result": result_text})
            if len(self.history) > 20:
                self.history = self.history[-20:]
            self._save_history()
            self._refresh_history()
            self.currency_mode = False
        except Exception:
            self.display_var.set("Erro")

    def load_history_item(self, event):
        selection = self.history_list.curselection()
        if not selection:
            return
        item = self.history[selection[0] * -1 if self.history else 0] if self.history else None
        if item:
            self.display_var.set(item["result"])

    def toggle_history(self):
        if self.history_frame.winfo_viewable():
            self.history_frame.grid_remove()
        else:
            self.history_frame.grid()

    def clear_history(self):
        self.history = []
        self._save_history()
        self._refresh_history()

    def _parse_input(self, value):
        cleaned = value.replace("R$", "").replace(" ", "")
        cleaned = cleaned.replace(".", "").replace(",", ".")
        return Decimal(cleaned)

    def _evaluate(self, expression):
        cleaned = expression.replace("R$", "").replace(" ", "")
        cleaned = cleaned.replace(".", "").replace(",", ".")
        cleaned = cleaned.replace("%", "/100")
        if not cleaned:
            raise ValueError("Vazio")
        return Decimal(str(eval(cleaned, {"__builtins__": {}}, {})))

    def _format_result(self, result):
        if result == result.to_integral():
            return format(result.quantize(Decimal("1")), "f")
        return format(result.normalize(), "f")


def main():
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
